from abc import ABC, abstractmethod
import pytorch_lightning as pl
from pytorch_toolbelt.losses import BinaryFocalLoss, JaccardLoss
from typing import Any
from functools import singledispatchmethod
import torch
import sklearn


class AbstractWrapper(ABC):
    @abstractmethod
    def predict(self, x):
        pass

    # @abstractmethod
    # def predict_proba(self):
    #     pass

    @abstractmethod
    def train(self, x, y):
        pass

    # @abstractmethod
    # def score(self, x, y):
    #     pass


class PLModule(pl.LightningModule):
    def __init__(self, model, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.model = model
        self.losses = [
            ("jaccard", 0.1, JaccardLoss(mode="binary", from_logits=True)),
            ("focal", 0.9, BinaryFocalLoss())
        ]

    def forward(self, batch: torch.Tensor) -> torch.Tensor:
        return self.model(batch)

    def training_step(self, batch, batch_idx):
        images, masks = batch["images"], batch["masks"]
        logits = self.model(images)

        total_loss = self.log_losses("train", logits, masks)
        return {"loss": total_loss}

    def log_losses(self, name, logits, masks):
        total_loss = 0
        for loss_name, weight, loss in self.losses:
            ls_mask = loss(logits, masks)
            total_loss += weight * ls_mask
            self.log(f"loss/{name}/{weight} * {loss_name}", ls_mask, on_step=False, on_epoch=True)

        self.log(f"loss/{name}/total", total_loss, on_step=False, on_epoch=True)
        return total_loss

    def configure_optimizers(self):
        params = [x for x in self.model.parameters() if x.requires_grad]
        optim = torch.optim.Adam(params, lr=3e-4)
        return [optim]
        # optim = obj_from_cfg(self.optim_cfg, params)
        # scheduler = obj_from_cfg(self.scheduler_cfg, optim)

        # return [optim], [scheduler]


class PytorchWrapper(AbstractWrapper):
    def __init__(self, model):
        self.model = PLModule(model)

    def predict(self, x):
        # with torch.no_grad()
        self.model.forward(x)

    def train(self, data_module):
        import pytorch_lightning as pl
        trainer = pl.Trainer(max_epochs=1, gpus=1)
        trainer.fit(self.model, data_module)


class SklearnWrapper(AbstractWrapper):
    def __init__(self, model):
        self.model = model

    def predict(self, x):
        return self.model.predict(x)

    def train(self, x, y):
        self.model.fit(x, y)

    def predict_proba(self, *args):
        return self.model.predict_proba(*args)


class Wrapper:
    @singledispatchmethod
    @classmethod
    def wrap(cls, model):
        raise NotImplementedError("This framework is not supported")

    @wrap.register
    @classmethod
    def _(cls, model: torch.nn.Module):
        return PytorchWrapper(model)

    @wrap.register
    @classmethod
    def _(cls, model: sklearn.base.BaseEstimator):
        set_framework("sklearn")
        return SklearnWrapper(model)


# ======================
FRAMEWORK = None
VALID_FRAMEWORKS = ['sklearn', 'torch']


def set_framework(name: str):
    global FRAMEWORK

    if name in VALID_FRAMEWORKS:
        FRAMEWORK = name
    else:
        raise ValueError("wrong framework name is given, possible values are:", ", ".join(VALID_FRAMEWORKS))


def get_framework():
    return FRAMEWORK
