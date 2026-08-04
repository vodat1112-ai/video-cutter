# video-cutter

> 🌐 Trang giới thiệu: `https://<your-username>.github.io/video-cutter/` (bật GitHub Pages, xem mục **Website** bên dưới)

Công cụ dòng lệnh (CLI) đơn giản để **cắt video ra số giây mong muốn**, dùng [ffmpeg](https://ffmpeg.org/) làm engine xử lý.

Hỗ trợ 2 chế độ:

| Chế độ  | Mô tả                                                        |
|---------|---------------------------------------------------------------|
| `cut`   | Cắt **một đoạn** video theo thời điểm bắt đầu / kết thúc (hoặc bắt đầu + thời lượng) |
| `split` | **Chia** cả video thành nhiều đoạn nhỏ, mỗi đoạn cùng độ dài N giây |

## Yêu cầu

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/download.html) đã cài và có trong `PATH`

Cài ffmpeg:

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows
winget install ffmpeg
```

Không cần cài thêm thư viện Python nào khác (chỉ dùng thư viện chuẩn).

## Cài đặt

```bash
git clone https://github.com/<your-username>/video-cutter.git
cd video-cutter
```

## Cách dùng

### 1. Cắt một đoạn video

```bash
# Cắt từ giây 10 đến giây 25
python video_cutter.py cut -i input.mp4 -s 10 -e 25

# Cắt từ giây 10, dài 15 giây (tương đương ví dụ trên)
python video_cutter.py cut -i input.mp4 -s 10 -d 15

# Chỉ định file đầu ra
python video_cutter.py cut -i input.mp4 -s 10 -d 15 -o clip.mp4

# Cắt chính xác từng frame (re-encode, chậm hơn nhưng chuẩn hơn)
python video_cutter.py cut -i input.mp4 -s 10 -d 15 --reencode
```

### 2. Chia video thành nhiều đoạn bằng nhau

```bash
# Chia thành các đoạn 30 giây/đoạn
python video_cutter.py split -i input.mp4 -n 30

# Chỉ định thư mục đầu ra
python video_cutter.py split -i input.mp4 -n 30 -o out_dir

# Re-encode để cắt chính xác từng frame
python video_cutter.py split -i input.mp4 -n 30 --reencode
```

Kết quả mặc định được lưu trong thư mục `<tên_file>_parts/`, đặt tên
`<tên_file>_part001.mp4`, `<tên_file>_part002.mp4`, ...

## Về `--reencode`

- **Không dùng `--reencode` (mặc định):** ffmpeg copy stream trực tiếp (`-c copy`) — cực nhanh, không giảm chất lượng, nhưng điểm cắt có thể bị lệch tới keyframe gần nhất (sai lệch thường dưới 1 giây tuỳ video).
- **Dùng `--reencode`:** ffmpeg giải mã và mã hoá lại (`libx264` + `aac`) — cắt chính xác đến từng frame, nhưng chậm hơn và có thể giảm nhẹ chất lượng/tăng dung lượng.

## Website

Repo có sẵn trang giới thiệu tĩnh trong thư mục [`docs/`](docs/index.html).
Cách bật GitHub Pages cho trang này:

1. Đẩy repo lên GitHub (xem hướng dẫn ở trên).
2. Vào repo trên GitHub → **Settings** → mục **Pages** (bên trái).
3. Ở **Build and deployment → Source**, chọn **Deploy from a branch**.
4. Ở **Branch**, chọn `main` và thư mục `/docs`, bấm **Save**.
5. Đợi khoảng 1 phút, trang sẽ chạy tại:
   `https://<your-username>.github.io/video-cutter/`

Muốn sửa nội dung trang, chỉnh trực tiếp file `docs/index.html` (HTML/CSS/JS thuần, không cần build).

## Giấy phép

[MIT](LICENSE)
