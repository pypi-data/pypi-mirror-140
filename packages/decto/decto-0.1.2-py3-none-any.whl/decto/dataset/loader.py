import torch

from decto.dataset.preprocess import preprocess
from decto.dataset.augmentation import resize_bbox, random_flip, flip_bbox
from decto.dataset.VOCDataset import VOCBboxDataset
from decto.dataset.VIADataset import VIADataset
from decto.dataset.DefaultDataset import DefaultDataset

class Transform(object):

    def __init__(self, min_size, max_size):
        self.min_size = min_size
        self.max_size = max_size

    def __call__(self, in_data):
        img, bbox, label = in_data
        _, _, H, W = img.shape
        
        img = preprocess(img, self.min_size, self.max_size)
        _, _, o_H, o_W = img.shape
        scale = o_H / H
        bbox = resize_bbox(bbox, (H, W), (o_H, o_W))
        
                # horizontally flip
        img, params = random_flip(
            img, x_random=True, return_param=True)
        bbox = flip_bbox(
            bbox, (o_H, o_W), x_flip=params['x_flip'])
        
        return img, bbox, label, scale


class Dataset:
    def __init__(self, data_dir, min_size, max_size, split='trainval', **kwargs):
#        self.db = VOCBboxDataset(data_dir, split=split)
#        self.db = VIADataset(data_dir, split=split)
        self.db = DefaultDataset(data_dir, split=split)   
        self.tsf = Transform(min_size, max_size)

    def __getitem__(self, idx):
        ori_img, bbox, label, difficult = self.db.get_example(idx)
        
        ori_img = torch.from_numpy(ori_img[None])
        
        img, bbox, label, scale = self.tsf((ori_img, bbox, label))
        
        img = img[0]
        
        return img, bbox, label, scale

    def __len__(self):
        return len(self.db)

class TestDataset:
    def __init__(self, data_dir, min_size, max_size, split='test', use_difficult=True, **kwargs):
#        self.db = VOCBboxDataset(data_dir, split=split, use_difficult=use_difficult)
#        self.db = VIADataset(data_dir, split=split)
        self.db = DefaultDataset(data_dir, split=split)
        self.tsf = Transform(min_size, max_size)

    def __getitem__(self, idx):
        ori_img, bbox, label, difficult = self.db.get_example(idx)

        ori_img = torch.from_numpy(ori_img[None])        
        scale_img, scale_bbox, label, scale = self.tsf((ori_img, bbox, label))
        
        ori_img = ori_img[0]
        scale_img = scale_img[0]        
        
        return (ori_img, bbox, label, difficult), (scale_img, scale_bbox, label, scale)

    def __len__(self):
        return len(self.db)
