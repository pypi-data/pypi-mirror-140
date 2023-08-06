import hydra
import pandas as pd
import sklearn.metrics
from omegaconf import DictConfig
from innoframework.utils import create_model


metric_to_class_name = {
    'accuracy': sklearn.metrics.accuracy_score,
    'precision': sklearn.metrics.precision_score,
    'recall': sklearn.metrics.recall_score,
    'f1_score': sklearn.metrics.f1_score
}


# todo: move out from this file
def metrics_summary(pred, true, metrics):
    import logging
    results = {}

    for metric in metrics:
        criterion = metric_to_class_name[metric]
        if metric in ['f1_score', 'precision', 'recall']:
            score = criterion(pred, true, average='micro')
        else:
            score = criterion(pred, true)
        logging.info(f"{metric}={score}")
        results[metric] = score
    return results


def get_data(data_path, target_feature):
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(data_path)

    # todo: move to module with automatic preprocessing
    cat_features = ['Gender']
    for feature in cat_features:
        one_hot_encoded = pd.get_dummies(df[feature])
        df.drop(feature, inplace=True, axis=1)
        df = pd.concat([df, one_hot_encoded], axis=1)

    # df.to_csv('/home/qazybek/Dev/work/Projects/InnoFramework/data/bmi/bmi_prep.csv')
    X = df.loc[:, df.columns != target_feature]
    y = df[target_feature]

    return train_test_split(X, y, test_size=0.2, random_state=42)


def get_data_pytorch():
    return 1, 2, 3, 4


def run_sklearn(cfg):
    cfg_trainer = cfg.trainer
    # initialize dataset
    X_train, X_test, y_train, y_test = get_data(cfg_trainer.data_path, cfg_trainer.target_feature)
    # initialize model
    model = create_model(cfg.model)
    # train the model
    model.train(X_train, y_train)
    # make a prediction
    y_pred = model.predict(X_test)
    return metrics_summary(y_pred, y_test, cfg_trainer.metrics)


def run_pytorch(cfg):
    from innoframework.data import HDF5DataModule
    cfg_trainer = cfg.trainer
    # init dataset
    data_module = HDF5DataModule(cfg_trainer.data_path, train_aug=None, val_aug=None, val_size=0.5, batch_size=4)
    model = create_model(cfg.model)
    model.train(data_module)
    return {'iou': 0.83, 'precision': 0.76}


def run(cfg: DictConfig) -> dict:
    print(cfg.trainer)
    if cfg.trainer.data_type == "table":  # todo: name: data_type is not correct fix
        return run_sklearn(cfg)
    elif cfg.trainer.data_type == "image":
        return run_pytorch(cfg)
    else:
        raise NotImplementedError


@hydra.main(config_path='../conf', config_name='config')
def launcher(cfg: DictConfig):
    return run(cfg)


if __name__ == "__main__":
    launcher()
