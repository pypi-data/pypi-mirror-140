"""This file includes dataset handlers

Given the path to the files
module will be able to detect the most appropriate dataset class
and create such instance

Example:
    given: some/path/to/csv/file.csv

    Module uses the type of the
"""
import innoframework


class DataModuleCreator:
    def create(self, data_path, task):
        # data_type = self.find_type(data_path)
        fw = innoframework.get_framework()
        if fw is None:
            raise Exception("Framework is not set")

        data_handler = framework_n_task[fw][task]
        return data_handler(data_path)


        # if model_type == "sklearn":
        #     if data_type == "tabular":

        #     elif data_type == "image":
        #         pass
        #     else:
        #         raise NotImplementedError("Unable to use such type of the data")
        # elif model_type == "pytorch":
        #     pass



def torch_img_seg_data_handler(data_path):
    pass


def torch_img_cls_data_handler(data_path):
    pass


def sklearn_img_cls_data_handler(data_path):
    pass


from typing import Union
from pathlib import Path

import pandas as pd


def table_data_handler(data_path: Union[str, Path]):
    return pd.read_csv(data_path)


# following functions will create a data_module
torch_task_to_data_handler = {
    'image-segmentation': torch_img_seg_data_handler,
    'image-classification': torch_img_cls_data_handler,
}

sklearn_task_to_data_handler = {
    # 'image-segmentation': img_seg_data_handler,
    'image-classification': sklearn_img_cls_data_handler,
    'table-classification': table_data_handler,
    # 'table-regression': table_data_handler,
}


framework_n_task = {
    'torch': torch_task_to_data_handler,
    'sklearn': sklearn_task_to_data_handler
}
