# from src.wrappers import SklearnWrapper, PytorchWrapper
# import sklearn
# import torch
import hydra
# import segmentation_models_pytorch


def obj_from_cfg(model_cfg, *args, **kwargs):
    return hydra.utils.instantiate(model_cfg, *args, **kwargs, _recursive_=True)


model_name_to_class = {
    'knn': 'sklearn.neighbors.KNeighborsClassifier',
    'unet': 'segmentation_models_pytorch.Unet',
    'unet++': 'segmentation_models_pytorch.UnetPlusPlus',
    'deeplabv3': 'segmentation_models_pytorch.DeepLabV3',
    'deeplabv3+': 'segmentation_models_pytorch.DeepLabV3Plus',
}


from src.wrappers import Wrapper


def create_model(model_cfg):
    class_name = model_name_to_class[model_cfg.name]
    model_cfg['_target_'] = class_name
    del model_cfg.name

    model = obj_from_cfg(model_cfg)
    return Wrapper.wrap(model)

