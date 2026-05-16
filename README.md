# Lane Violation Detection

Hệ thống phát hiện vi phạm làn đường từ video hoặc ảnh giao thông, sử dụng YOLO để nhận diện phương tiện, phân vùng làn xe máy / ô tô, và đánh dấu các trường hợp đi sai làn.

## Tính năng

- Nhận diện phương tiện: ô tô, xe máy, bus, xe tải (YOLOv8)
- Phân làn tự động theo kích thước khung hình (làn xe máy và làn ô tô)
- Theo dõi đối tượng đơn giản theo tọa độ trung tâm
- Phát hiện vi phạm: xe máy không ở làn xe máy, ô tô/bus/tải không ở làn ô tô
- Hiển thị kết quả trực tiếp trên cửa sổ OpenCV
- Lưu ảnh/video đã annotate và báo cáo vi phạm (JSON, CSV)

## Cấu trúc dự án

```
lane_violation-main/
├── main.py                 # Điểm vào chương trình
├── config.py               # Cấu hình mặc định
├── detection/
│   └── detector.py         # Nhận diện phương tiện (YOLO)
├── lane/
│   └── lane_detector.py    # Xác định làn đường
├── tracking/
│   └── tracker.py          # Gán ID theo dõi đối tượng
├── violation/
│   └── violation_detector.py  # Kiểm tra vi phạm làn
└── utils/
    ├── draw.py             # Vẽ khung, làn, nhãn
    └── results.py          # Hiển thị thống kê và lưu kết quả
```

## Yêu cầu

- Python 3.8+
- OpenCV
- Ultralytics (YOLOv8)
- NumPy

## Cài đặt

```bash
cd lane_violation-main
pip install opencv-python ultralytics numpy
```

Lần chạy đầu tiên, mô hình `yolov8s.pt` sẽ được tải tự động nếu chưa có trong thư mục làm việc.

## Cách sử dụng

### Xử lý video

```bash
python main.py --video traffic.mp4
```

Dùng video mặc định trong `config.py` (biến `VIDEO_PATH`):

```bash
python main.py
```

Nhấn **ESC** để dừng khi đang xem trước.

### Xử lý ảnh

```bash
python main.py --image input.jpg
```

### Hiển thị và lưu kết quả

Lưu toàn bộ (ảnh hoặc video + log) vào thư mục có timestamp:

```bash
python main.py --image input.jpg --output-dir output
python main.py --video traffic.mp4 --output-dir output
```

Lưu riêng từng file:

```bash
python main.py --image input.jpg --save result.jpg
python main.py --video traffic.mp4 --save-video result.mp4
```

Chạy không hiển thị cửa sổ (chỉ lưu file):

```bash
python main.py --image input.jpg --save result.jpg --no-display
```

### Tham số dòng lệnh

| Tham số | Mô tả |
|---------|--------|
| `--video` | Đường dẫn video đầu vào |
| `--image` | Đường dẫn ảnh đầu vào |
| `--model` | Tên hoặc đường dẫn mô hình YOLO (mặc định: `yolov8s.pt`) |
| `--output-dir` | Thư mục gốc lưu kết quả (tạo subfolder theo thời gian) |
| `--save` | Lưu ảnh kết quả ra đường dẫn chỉ định |
| `--save-video` | Lưu video kết quả ra đường dẫn chỉ định |
| `--no-display` | Tắt cửa sổ xem trước |
| `--no-log` | Không ghi file JSON/CSV vi phạm |

## Kết quả đầu ra

Khi dùng `--output-dir`, mỗi lần chạy tạo thư mục dạng `output/YYYYMMDD_HHMMSS/`:

| File | Nội dung |
|------|----------|
| `result.jpg` | Ảnh đã vẽ khung và làn (chế độ ảnh) |
| `result.mp4` | Video đã annotate (chế độ video) |
| `violations.json` | Báo cáo chi tiết: frame, ID, loại xe, làn, bbox |
| `violations.csv` | Bảng vi phạm dạng CSV |

### Quy tắc vi phạm

| Loại xe | Làn hợp lệ | Vi phạm khi |
|---------|------------|-------------|
| motorcycle, motorbike | `motor_lane` | Không nằm trong làn xe máy |
| car, bus, truck | `car_lane` | Không nằm trong làn ô tô |

Trên màn hình:
- Khung **xanh lá**: phương tiện hợp lệ
- Khung **đỏ** + nhãn `VIOLATION`: vi phạm
- Góc trên: số vi phạm trong frame hiện tại và tổng cộng

## Cấu hình

Chỉnh trong `config.py`:

```python
VIDEO_PATH = "traffic.mp4"   # Video mặc định
MODEL_PATH = "yolov8s.pt"    # Mô hình YOLO
OUTPUT_DIR = "output"        # Thư mục gốc khi dùng --output-dir
```

Điều chỉnh vùng làn: sửa tỷ lệ trong `lane/lane_detector.py` (hàm `build_lanes`).

## Luồng xử lý

```
Video / Ảnh
    → YOLO phát hiện xe
    → Tracker gán ID
    → LaneDetector xác định làn (motor / car)
    → ViolationDetector kiểm tra vi phạm
    → Vẽ kết quả + thống kê
    → Hiển thị / lưu file
```

## Ghi chú

- Làn đường được tính từ frame đầu tiên (video) hoặc frame duy nhất (ảnh); góc quay camera cố định cho kết quả ổn định nhất.
- Tracker dùng khoảng cách pixel đơn giản, phù hợp demo; môi trường thực tế có thể cần thuật toán tracking mạnh hơn (DeepSORT, ByteTrack, …).
- Đặt file `traffic.mp4` cùng thư mục hoặc truyền đường dẫn đầy đủ qua `--video`.
