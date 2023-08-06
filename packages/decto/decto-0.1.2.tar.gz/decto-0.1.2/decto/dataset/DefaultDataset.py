import json
import os
import numpy as np

from decto.dataset.preprocess import read_image

class DefaultDataset(object):
    def __init__(self, data_dir, split):
        self.data_dir = data_dir
        self.split = split
        anns = json.load(open('{}/{}'.format(data_dir, split)))
        self.classes = anns['class_names'] 
        self.data = anns['annotations']

    def __len__(self):
        return len(self.data)
    
    def get_example(self, i):
        item = self.data[i]
        
        fname = item['fname']
        fname = os.path.join(self.data_dir, fname)
        bbox = item['bbox']
        label = item['label']
            
        img = read_image(fname, color=True)
        bbox = np.stack(bbox).astype(np.float32)
        label = np.stack(label).astype(np.int32)
        difficult = np.zeros_like(label, dtype=np.uint8)
        
        return img, bbox, label, difficult
