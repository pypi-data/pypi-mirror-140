from pytorch_lightning import LightningDataModule
from pathlib import Path
from sklearn.model_selection import train_test_split
from .dataset import HDF5Dataset
import torch


class HDF5DataModule(LightningDataModule):
    def __init__(self,
                 data_path,
                 train_aug,
                 val_aug,
                 # test_aug,
                 channels_num: int = 3,
                 val_size: float = 0.2,
                 # test_size: float = 0.1,
                 batch_size: int = 32,
                 max_workers: int = 1,
                 random_seed: int = 42,
                 *args,
                 **kwargs):
        super().__init__()
        self.data_path = Path(data_path)

        # TODO: should object instantiation be here?
        self.train_aug = train_aug
        self.val_aug = val_aug
        # self.test_aug = test_aug

        self.channels_num = channels_num

        self.val_size = val_size
        # self.test_size = test_size

        self.batch_size = batch_size
        self.max_workers = max_workers

        self.random_seed = random_seed

    def prepare_data(self) -> None:
        # make hdf5 files from raw data
        # dreams...
        pass

    def setup(self, **kwargs):
        # files = list(self.data_path.rglob(''))
        train_files = [self.data_path / 'train_samples.hdf5']
        val_files = [self.data_path / 'val_samples.hdf5']

        # split files into train_val and test
        # self.train_val_files, self.test_files = train_test_split(files,
        #                                                          test_size=self.test_size,
        #                                                          random_state=self.random_seed)
        # split train_val files into train and val
        # train_files, val_files = train_test_split(files,
        #                                           test_size=self.val_size,
        #                                           random_state=self.random_seed)

        # prepare datasets
        self.train_dataset = HDF5Dataset(train_files, self.channels_num, self.train_aug)
        self.val_dataset = HDF5Dataset(val_files, self.channels_num, self.val_aug)
        # self.test_dataset = HDF5Dataset(files, self.channels_num, self.test_aug)

    def train_dataloader(self):
        train_dataloader = torch.utils.data.DataLoader(self.train_dataset,
                                                       batch_size=self.batch_size,
                                                       num_workers=self.max_workers)
        return train_dataloader

    def val_dataloader(self):
        val_dataloader = torch.utils.data.DataLoader(self.val_dataset,
                                                     batch_size=self.batch_size,
                                                     num_workers=self.max_workers)
        return val_dataloader

    def test_dataloader(self):
        pass
        # test_dataloader = torch.utils.data.DataLoader(self.test_dataset,
        #                                               batch_size=self.batch_size,
        #                                               num_workers=self.max_workers)
        # return test_dataloader

    def predict_dataloader(self):  # TODO: set to specific data that I want to test
        pass
        # test_dataloader = torch.utils.data.DataLoader(self.test_dataset,
        #                                               batch_size=self.batch_size,
        #                                               num_workers=self.max_workers)
        # return test_dataloader

    # def teardown(self):  # clean up when the run is finished
    # pass
