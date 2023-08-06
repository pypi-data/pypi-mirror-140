
import torch

from decto.model.faster_rcnn import FasterRCNN

class Predictor():
    def __init__(self, config, weights, device):
        self.device = device
        self.config = config
        self.min_size = config['dataset_config']['min_size_test']
        self.max_size = config['dataset_config']['max_size_test']
        self.classes = config['dataset_config']['classes']

        self.model = FasterRCNN(config['backbone'],
                        config['fpn_config'],
                        config['rpn_config'],
                        config['roi_pooler_config'],
                        config['roi_head_config'])
        
        self.model.eval()
        self.model.load_state_dict(torch.load(weights, map_location='cpu'))

        if self.device.startswith('cuda'):
            self.model = self.model.to(self.device)

    def predict(self, img, return_roi=False, include_bg=False):
        """
        img: RGB 3 channels HxWxC
        """

        img = img.transpose((2, 0, 1))

        pred = self.model.predict(img, min_size=self.min_size, max_size=self.max_size, return_roi=return_roi, include_bg=include_bg)
        return pred

    
    def predict_bbox(self, img):
        img = img.transpose((2, 0, 1))
        bboxes, labels, scores = self.model.predict(img, min_size=self.min_size, max_size=self.max_size)
        
        results = []
        for box, prob, clazz in zip(bboxes, scores, labels):
            y1, x1, y2, x2 = box
            w = x2 - x1
            h = y2 - y1
            r = {'x': x1, 'y': y1, 'w': w, 'h': h, 'prob': prob, 'name': self.classes[clazz]}
            results.append(r)

        return results

