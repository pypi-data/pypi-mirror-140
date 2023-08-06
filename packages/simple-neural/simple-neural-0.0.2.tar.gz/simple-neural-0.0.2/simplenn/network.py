import pathlib
import pickle
from copy import deepcopy
from typing import List
from typing import Union

import numpy as np
from simplenn.block import Block
from simplenn.layer import Layer
from simplenn.metrics.accuracy import Accuracy


class Network:
    """Base class used for block orquestration"""

    def __init__(self, optimizer) -> None:
        self.optimizer = optimizer

    def get_block_names(self):
        """Retrieve all block names"""
        block_names = [prop for prop in self.__dir__() if isinstance(getattr(self, prop), Block)]
        return block_names

    def get_layers(self) -> List[Layer]:
        """Retrieve all layer blocks"""
        block_names = self.get_block_names()

        layers = []
        for block_name in block_names:
            block: Block = getattr(self, block_name)
            if isinstance(block, Layer):
                layers.append(block)
        return layers

    def get_backward_execution_graph(self) -> List[Block]:
        """Retrieve all blocks and return their execution order backwards"""

        block_names = self.get_block_names()
        graph_start = None

        # Seek network end
        for block_name in block_names:
            block: Block = getattr(self, block_name)
            setattr(block, "name", block_name)
            if block.next_block is None:
                graph_start = block
                break

        current_block: Union[Block, None] = graph_start
        execution_graph = []
        while current_block:
            execution_graph.append(current_block)
            current_block = current_block.prev_block
        return execution_graph

    def get_forward_execution_graph(self) -> List[Block]:
        """Retrieve all blocks and return their execution order forwards"""

        block_names = self.get_block_names()
        graph_start = None

        # Seek network end
        for block_name in block_names:
            block: Block = getattr(self, block_name)
            setattr(block, "name", block_name)
            if block.prev_block is None:
                graph_start = block
                break

        current_block: Union[Block, None] = graph_start
        execution_graph = []
        while current_block:
            execution_graph.append(current_block)
            current_block = current_block.next_block
        return execution_graph

    def backwards(self, output, targets):
        """Automatic differentiator orquestrator for sequential networks"""
        blocks: List[Block] = self.get_backward_execution_graph()

        # backpropagation
        z = blocks[0].back(output, targets)
        for block in blocks[1:]:
            z = block.back(z)

        # optimize parameters
        self.optimizer.learn(self.get_layers())

    def predict(self, X):
        blocks: List[Block] = self.get_forward_execution_graph()
        z = blocks[0](X, inference=True)
        for block in blocks[1:]:
            z = block(z, inference=True)
        return z

    def _init_training_report(self, metrics, X_val, y_val):
        custom_metrics = [f"Train_{m.NAME}" for m in metrics]
        custom_metrics_alias = [f"Train_{m.ALIAS}" for m in metrics]

        if X_val is not None and y_val is not None:
            custom_metrics += [f"Val_{m.NAME}" for m in metrics]
            custom_metrics_alias += [f"Val_{m.ALIAS}" for m in metrics]

        self.tr_report_columns = ["Loss"] + custom_metrics
        self.tr_report_format_row = (
            "epoch={epoch:<10} loss={loss:<10} reg_loss={reg_loss:<10}"
            + " ".join([f"{a}=" + "{" + x + ":<10}" for a, x in zip(custom_metrics_alias, custom_metrics)])
            + " lr={lr:<10}"
        )
        # print(self.tr_report_format_row.format(epoch="", loss="", reg_loss="", **{k: k for k in custom_metrics}))

    def training_report(self, epoch, loss, reg_loss, train_metrics, val_metrics=None):
        metrics = {f"Train_{k}": f"{v:.4f}" for k, v in train_metrics.items()}

        if val_metrics:
            val_format_metrics = {f"Val_{k}": f"{v:.4f}" for k, v in val_metrics.items()}
            metrics = {**metrics, **val_format_metrics}

        print(
            self.tr_report_format_row.format(
                epoch=epoch,
                loss=f"{loss:.4f}",
                reg_loss=f"{reg_loss:.4f}",
                **metrics,
                lr=f"{self.optimizer.get_adjusted_lr():.4f}",
            )
        )

    def fit(self, X, y, batch_size=32, epochs=100, shuffle=True, X_val=None, y_val=None, metrics=[Accuracy()]):
        self._init_training_report(metrics, X_val, y_val)
        loss_fcn = None

        steps = X.shape[0] // batch_size
        if steps * batch_size < X.shape[0]:
            steps += 1

        for epoch in range(epochs):
            for step in range(steps):
                mini_batch_X = X[step * batch_size : (step + 1) * batch_size]
                mini_batch_y = y[step * batch_size : (step + 1) * batch_size]

                output, loss = self.forward(mini_batch_X, mini_batch_y)

                if loss_fcn is None:
                    loss_fcn = self.get_backward_execution_graph()[0]
                    loss_fcn = loss_fcn.loss if hasattr(loss_fcn, "loss") else loss_fcn

                self.backwards(output, mini_batch_y)

            if not epoch % (1 if epochs <= 100 else int(epochs / 100)):
                yhat = self.predict(X)
                reg_loss = loss + sum([loss_fcn.get_reg_loss(layer) for layer in self.get_layers()])
                train_metrics = {m.NAME: m(yhat, y) for m in metrics}
                val_metrics = None
                if X_val is not None and y_val is not None:
                    yhat_val = self.predict(X_val)
                    val_metrics = {m.NAME: m(yhat_val, y_val) for m in metrics}

                self.training_report(epoch, loss, reg_loss, train_metrics, val_metrics)

            if shuffle:
                idx = np.random.permutation(len(X))
                X = X[idx]
                y = y[idx]

    def save(self, path: Union[str, pathlib.Path]) -> None:
        for block in self.get_forward_execution_graph():
            block.cleanup()

        network = deepcopy(self)
        with open(path, "wb") as f:
            pickle.dump(network, f)

    @staticmethod
    def load(path: Union[str, pathlib.Path]):
        with open(path, "rb") as f:
            network = pickle.load(f)
        return network
