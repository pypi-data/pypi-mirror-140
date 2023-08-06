# Decto
**Cài đặt FasterRCNN sử dụng Feature Pyramid Network.**

![](img/faster_rcnn_fpn.jpg)


Thư viện decto hướng tới việc đơn giản khi sử dụng, code ngắn gọn, dễ hiểu và độ chính xác tương tự như thư viện detectron2, đồng thời giúp cho các bạn có thể custom code cho các dự án khác.

Thư viện này được áp dụng cho các dự án số hóa và đã đem lại kết quả rất tốt trên tập dữ liệu .

## Cài đặt
Để cài đặt các bạn chạy lệnh sau
```
pip install decto
```
## Kết quả thử nghiệm
Kết quả huấn luyện bằng decto có độ chính xác bằng với các thư viên khác như [detectron2](https://github.com/facebookresearch/detectron2), hoặc [pytorch-faster-rcnn](https://github.com/ruotianluo/pytorch-faster-rcnn)
| Cài đặt  | VOC 2007 | Số hóa |
| ------------- | ------------- |-----|
| [detectron2](https://github.com/facebookresearch/detectron2)  | 0.75 |0.|
| decto  | 0.75  |0.81|

## Train & Inference
Các bạn tham khảo notebook sau
### Dataset
Các bạn chuẩn bị cấu trúc dataset dưới dạng sau
```
├── img
│   ├── a.jpg
│   ├── b.jpg
├── test.json
└── train.json

```
File json train và test có định dạng như dưới:
```
{
'class_names':['bird', 'car'],
'annotations':
[
  {'fname':'img/a.jpg', 'bbox':[[10, 20], [30, 40]], 'label':[0, 0]}
  {'fname':'img/b.jpg', 'bbox':[[20, 50], [40, 70]], 'label':[0, 1]}
]
}
```

## Problem
Nếu bạn có bất kì vấn đề gì, vui lòng tạo issue hoặc liên hệ mình tại pbcquoc@gmail.com
