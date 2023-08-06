import streamlit as st
import pandas as pd

# st.sidebar.button("one")
# st.sidebar.button("two")
import uuid
from main import launcher


def get_uuid():
    gen_uuid = uuid.uuid4()
    gen_uuid = str(gen_uuid).split('-')[0]
    return gen_uuid


# with st.form(key="model"):
proj_uuid = get_uuid()
proj_name = st.text_input("What is the name of the project?", value=f"random-project-{proj_uuid}")

input_type = st.selectbox("What is your input type?", ["table", "images"])

if input_type == "table":
    data_path = st.text_input("Provide location to the file:",
                              value="/home/qazybek/Projects/InnoFramework/data/bmi/bmi.csv")

    df = pd.read_csv(data_path)
    st.dataframe(df)

    task = st.selectbox("What task you want to solve?", ["classification", "regression"])  # , "clustering"

    columns = list(df.columns)
    target_feature = st.selectbox("What is the target feature?", columns[::-1])

    metrics = st.multiselect("What metrics to measure", ['accuracy', 'f1_score', 'precision', 'recall'],
                             default='f1_score')

    if task == "classification":
        model = st.selectbox("What model you want to try?", ["KNN", "SVM", "Random Forest", "Decision Tree"])

        if model == "KNN":
            model_params = {}
            with st.expander("Open to tune parameters"):
                model_params['n_neighbors'] = st.slider("n_neighbors", value=3, min_value=1, max_value=100)
                model_params['weights'] = st.selectbox("weights", ["uniform", "distance"])
                model_params['algorithm'] = st.selectbox("algorithm", ['auto', 'ball_tree', 'kd_tree', 'brute'])
                model_params['leaf_size'] = st.slider("leaf_size", value=30, min_value=1, max_value=100)
                model_params['n_jobs'] = st.slider("n_jobs", value=1, min_value=-1, max_value=16)
    else:
        model = st.selectbox("What model you want to try?",
                             ["Linear Regression", "LGBM Regressor", "CatBoost Regressor", "KNN Regressor"])
        model_params = {}

    if st.button("Create!"):
        # save training configurations
        with open(f'conf/trainer/{proj_name}.yaml', 'w') as cfg:
            cfg.write('data_type: table\n')
            cfg.write(f"target_feature: {target_feature}\n")
            cfg.write(f"data_path: {data_path}\n")
            cfg.write(f"metrics:\n")

            for metric in metrics:
                cfg.write(f"  - {metric}\n")

        # save model configurations
        with open(f'conf/model/{model.lower()}.yaml', 'w') as cfg:
            cfg.write(f'name: {model.lower()}\n')
            cfg.write("_target_: ???\n")

            if model == 'KNN':
                for key, val in model_params.items():
                    cfg.write(f'{key}: {val}\n')

        # save default configurations
        with open(f'conf/config.yaml', 'w') as cfg:
            cfg.write(f"defaults:\n")
            cfg.write(f"  - _self_\n")
            cfg.write(f"  - model: {model.lower()}\n")
            cfg.write(f"  - trainer: {proj_name}\n")

        st.success("Configurations are saved!")

else:
    task = st.selectbox("What task you want to solve?",
                        ["segmentation", "detection", "image generation", "classification", "regression"])
    metrics = st.multiselect("What metrics to measure", ['iou', 'accuracy', 'f1_score', 'precision', 'recall'])
    data_path = st.text_input("Path to the data",
                              value="/mnt/datastore/GIS/les/GPN_forest/data/31-01-22-interim/hdf5/512")

    if task == "segmentation":
        model = st.selectbox("What model you want to try?", ["Unet", "Unet++", "DeepLabV3", "DeepLabV3+"])
        model_size = st.selectbox("What size of the model you want?", ['Small', 'Medium', 'Large'])

        model_params = dict()
        model_params['in_channels'] = st.number_input("number of channels", value=3, min_value=1, max_value=8)
        model_params['classes'] = st.number_input("number of classes", value=1, min_value=1)

        with st.expander("Open to tune parameters"):
            model_params['activation'] = st.selectbox("activation function", ['sigmoid', 'None', 'softmax'])

            if model_size == "Small":
                model_params['encoder_name'] = st.selectbox("encoder", ['resnet18', 'dpn68'])
                # model_params['n_jobs'] = st.slider("n_jobs", value=1, min_value=-1, max_value=16)
            elif model_size == "Medium":
                model_params['encoder_name'] = st.selectbox("encoder", ['resnet34', 'resnet50'])
            elif model_size == "Large":
                model_params['encoder_name'] = st.selectbox("encoder", ['resnet101', 'resnet152'])
            else:
                raise NotImplementedError

    if st.button("Create!"):
        # save training configurations
        with open(f'conf/trainer/{proj_name}.yaml', 'w') as cfg:
            cfg.write(f"data_path: {data_path}\n")
            cfg.write('data_type: image\n')
            cfg.write(f"metrics:\n")

            for metric in metrics:
                cfg.write(f"  - {metric}\n")

        # save model configurations
        with open(f'conf/model/{model.lower()}.yaml', 'w') as cfg:
            cfg.write(f'name: {model.lower()}\n')
            cfg.write("_target_: ???\n")

            for key, val in model_params.items():
                cfg.write(f'{key}: {val}\n')

        # save default configurations
        with open(f'conf/config.yaml', 'w') as cfg:
            cfg.write(f"defaults:\n")
            cfg.write(f"  - _self_\n")
            cfg.write(f"  - model: {model.lower()}\n")
            cfg.write(f"  - trainer: {proj_name}\n")

        st.success("Configurations are saved!")


import hydra
from omegaconf import DictConfig
from innoframework.main import run


@hydra.main(config_path='../conf', config_name='config')
def start(cfg: DictConfig):
    metric_results = run(cfg)
    print(metric_results)

    cols = st.columns(len(metric_results))
    for col, key, val in zip(cols, metric_results.keys(), metric_results.values()):
        col.metric(key, val)


with st.form(key="training"):
    if st.form_submit_button("Start training!"):
        start()
