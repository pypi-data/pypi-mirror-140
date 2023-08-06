from bunch import Bunch

from pytorch_common.callbacks import Callback
from pytorch_common.callbacks.output import Logger
from pytorch_common.util import Stopwatch


class CallbackManager:
    def __init__(self, epochs, optimizer, loss_fn, model, callbacks=[Logger()], verbose=1, extra_ctx={}):
        self.callbacks = callbacks
        self.epochs = epochs
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.model = model
        self.verbose = verbose
        self.ctx = ContextFactory.create(self.epochs, self.optimizer, self.loss_fn, self.model, extra_ctx, self.verbose)
        Callback.invoke_on_init(self.ctx, self.callbacks)

    def on_epoch_start(self, epoch):
        self.ctx.stopwatch.reset()
        self.ctx.epoch = epoch + 1

    def on_epoch_end(self, train_loss, val_loss=None):
        self.ctx.train_loss = train_loss
        self.ctx.val_loss = val_loss
        self.ctx.time = self.ctx.stopwatch.to_str()
        Callback.invoke_on_after_train(self.ctx, self.callbacks)

    def break_training(self):
        return 'early_stop' in self.ctx and self.ctx.early_stop is True


class ContextFactory:
    @staticmethod
    def create(epochs, optimizer, loss_fn, model, extra_ctx={}, verbose=1):
        ctx = Bunch({
            'verbose': verbose,
            'epochs': epochs,
            'optimizer': optimizer,
            'loss_fn': loss_fn,
            'device': model.device,
            'model': model,
            'stopwatch': Stopwatch()
        })

        for (k, v) in extra_ctx.items():
            ctx[k] = v

        return ctx
