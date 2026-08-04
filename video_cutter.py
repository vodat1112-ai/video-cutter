#!/usr/bin/env python3
"""
video_cutter.py — Cắt video theo số giây mong muốn (dùng ffmpeg).

Hai chế độ:
  1) Cắt MỘT đoạn theo thời điểm bắt đầu/kết thúc (hoặc bắt đầu + thời lượng)
       python video_cutter.py cut  -i input.mp4 -s 10 -e 25
       python video_cutter.py cut  -i input.mp4 -s 10 -d 15
       python video_cutter.py cut  -i input.mp4 -s 10 -d 15 -o clip.mp4 --reencode

  2) CHIA cả video thành nhiều đoạn cùng độ dài N giây
       python video_cutter.py split -i input.mp4 -n 30
       python video_cutter.py split -i input.mp4 -n 30 -o out_dir --reencode

Yêu cầu: đã cài ffmpeg và có trong PATH (https://ffmpeg.org/download.html).
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "❌ Không tìm thấy ffmpeg trong PATH.\n"
            "   Cài đặt: https://ffmpeg.org/download.html\n"
            "   Ubuntu/Debian: sudo apt install ffmpeg\n"
            "   macOS (brew): brew install ffmpeg\n"
            "   Windows: winget install ffmpeg  hoặc  choco install ffmpeg"
        )


def get_duration(path: Path) -> float:
    """Lấy tổng thời lượng video (giây) bằng ffprobe."""
    if shutil.which("ffprobe") is None:
        sys.exit("❌ Không tìm thấy ffprobe (thường đi kèm ffmpeg).")
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def fmt_hms(seconds: float) -> str:
    """Định dạng số giây -> HH:MM:SS.mmm cho ffmpeg -ss/-to."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def run_ffmpeg_cut(
    src: Path, dst: Path, start: float, end: float, reencode: bool
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", fmt_hms(start),
        "-i", str(src),
        "-to", fmt_hms(max(end - start, 0)),
    ]
    if reencode:
        # Re-encode: cắt chính xác đến từng frame, nhưng chậm hơn.
        cmd += ["-c:v", "libx264", "-c:a", "aac", "-avoid_negative_ts", "make_zero"]
    else:
        # Copy stream: rất nhanh, nhưng điểm cắt có thể lệch tới keyframe gần nhất.
        cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
    cmd.append(str(dst))

    print(f"  → {dst.name}  [{fmt_hms(start)} → {fmt_hms(end)}]")
    subprocess.run(cmd, check=True, capture_output=True)


def cmd_cut(args: argparse.Namespace) -> None:
    src = Path(args.input)
    if not src.is_file():
        sys.exit(f"❌ Không tìm thấy file: {src}")

    start = args.start
    if args.end is not None:
        end = args.end
    elif args.duration is not None:
        end = start + args.duration
    else:
        sys.exit("❌ Cần chỉ định --end (-e) hoặc --duration (-d).")

    if end <= start:
        sys.exit("❌ Thời điểm kết thúc phải lớn hơn thời điểm bắt đầu.")

    out = Path(args.output) if args.output else src.with_name(
        f"{src.stem}_cut_{int(start)}s-{int(end)}s{src.suffix}"
    )

    print(f"Đang cắt: {src.name}")
    run_ffmpeg_cut(src, out, start, end, args.reencode)
    print(f"✅ Xong: {out}")


def cmd_split(args: argparse.Namespace) -> None:
    src = Path(args.input)
    if not src.is_file():
        sys.exit(f"❌ Không tìm thấy file: {src}")
    if args.seconds <= 0:
        sys.exit("❌ Số giây mỗi đoạn phải > 0.")

    total = get_duration(src)
    n_parts = math.ceil(total / args.seconds)
    out_dir = Path(args.output) if args.output else src.with_name(f"{src.stem}_parts")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Video dài {total:.2f}s → chia thành {n_parts} đoạn, mỗi đoạn {args.seconds}s")
    for i in range(n_parts):
        start = i * args.seconds
        end = min(start + args.seconds, total)
        dst = out_dir / f"{src.stem}_part{i + 1:03d}{src.suffix}"
        run_ffmpeg_cut(src, dst, start, end, args.reencode)

    print(f"✅ Xong: {n_parts} file trong thư mục {out_dir}/")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="video_cutter",
        description="Cắt video ra số giây mong muốn bằng ffmpeg.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # cut
    p_cut = sub.add_parser("cut", help="Cắt một đoạn theo thời điểm bắt đầu/kết thúc")
    p_cut.add_argument("-i", "--input", required=True, help="File video đầu vào")
    p_cut.add_argument("-s", "--start", type=float, default=0.0, help="Thời điểm bắt đầu (giây)")
    p_cut.add_argument("-e", "--end", type=float, default=None, help="Thời điểm kết thúc (giây)")
    p_cut.add_argument("-d", "--duration", type=float, default=None, help="Thời lượng đoạn cắt (giây), thay cho --end")
    p_cut.add_argument("-o", "--output", default=None, help="File video đầu ra")
    p_cut.add_argument("--reencode", action="store_true", help="Re-encode để cắt chính xác từng frame (chậm hơn)")
    p_cut.set_defaults(func=cmd_cut)

    # split
    p_split = sub.add_parser("split", help="Chia video thành nhiều đoạn cùng độ dài N giây")
    p_split.add_argument("-i", "--input", required=True, help="File video đầu vào")
    p_split.add_argument("-n", "--seconds", type=float, required=True, help="Độ dài mỗi đoạn (giây)")
    p_split.add_argument("-o", "--output", default=None, help="Thư mục chứa các đoạn đã cắt")
    p_split.add_argument("--reencode", action="store_true", help="Re-encode để cắt chính xác từng frame (chậm hơn)")
    p_split.set_defaults(func=cmd_split)

    return p


def main() -> None:
    check_ffmpeg()
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="ignore") if isinstance(e.stderr, bytes) else str(e.stderr)
        sys.exit(f"❌ ffmpeg lỗi:\n{stderr[-1500:]}")


if __name__ == "__main__":
    main()
