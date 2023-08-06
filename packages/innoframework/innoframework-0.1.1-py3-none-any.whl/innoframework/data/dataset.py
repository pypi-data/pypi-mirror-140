from pathlib import Path
from typing import List, Union

import albumentations as albu
import h5py
import numpy as np
# import rasterio as rio
import torch
from torch.utils.data import Dataset


def get_indices_dict_size(hdf5_files):
    indices_dict_ = {}
    last_idx = 0
    for file in hdf5_files:
        with h5py.File(file) as f:
            last_idx += f['len'][0]
            indices_dict_[file] = last_idx

    return indices_dict_, last_idx


class HDF5Dataset(Dataset):
    def __init__(self, hdf5_files: Union[List[Path], List[str]],
                 bands_num: int,
                 transform: albu.Compose):
        self.indices_dict, self.size_ = get_indices_dict_size(hdf5_files)
        self.bands_num = bands_num
        self.transform = transform

    def __len__(self):
        return self.size_

    def __getitem__(self, idx):
        count = 0
        for key, value in self.indices_dict.items():
            if idx <= value:
                with h5py.File(key) as f:
                    index = idx - count

                    image = f[str(index)][..., :self.bands_num]
                    mask = f[str(index)][..., self.bands_num:]

                    return prep_data(image, mask, self.transform)
            else:
                count += value
        raise Exception(f"Dataset element {idx} not found; Max is {self.__len__()}")


def prep_data(image, mask, transform):
    if transform:
        sample = transform(image=image.astype('uint8'), mask=mask.astype('uint8'))
        image, mask = sample["image"], sample["mask"]

    image = np.moveaxis(image, 2, 0)
    # ============== preprocessing ==============
    image = image / 255.  # todo: move out
    # ===========================================
    image = torch.from_numpy(image)
    image = image.float()
    mask = (mask > 0).astype(np.uint8)
    mask = torch.from_numpy(mask)
    mask = torch.unsqueeze(mask, 0).float()

    return {"images": image,
            "masks": mask}
