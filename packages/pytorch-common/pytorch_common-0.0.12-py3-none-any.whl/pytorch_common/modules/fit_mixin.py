from pytorch_common.callbacks import CallbackManager
from pytorch_common.callbacks.output import Logger
from pytorch_common.modules import Fn
from pytorch_common.modules.common_mixin import CommonMixin


class FitMixin(CommonMixin):
    def fit(
            self,
            data_loader,
            loss_fn,
            epochs,
            optimizer,
            callbacks=[Logger()],
            verbose=1,
            extra_ctx={}
    ):
        """
        Train a model.
        :param data_loader: data_loader with train set.
        :param loss_fn: function to minimize.
        :param epochs: number of epochs to train model.
        :param optimizer: optimizer used to adjust model.
        :param callbacks: callback collection. See Callback.
        :param verbose: show/hide logs.
        """
        callback_manager = CallbackManager(epochs, optimizer, loss_fn, self, callbacks, verbose, extra_ctx)

        for epoch in range(epochs):
            callback_manager.on_epoch_start(epoch)

            train_loss = Fn.train(
                self,
                data_loader,
                loss_fn,
                optimizer,
                callback_manager.ctx.device
            )

            callback_manager.on_epoch_end(train_loss)

            if callback_manager.break_training():
                break

        return callback_manager.ctx
