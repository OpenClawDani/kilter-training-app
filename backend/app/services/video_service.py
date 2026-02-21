import subprocess
import json
import os


async def extract_fragment(
    input_path: str,
    output_path: str,
    start: float,
    end: float,
) -> str:
    """
    Uses ffmpeg to extract a fragment from a video.
    Returns: output_path of the trimmed fragment.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output_path,
        ],
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    return output_path


async def get_video_info(file_path: str) -> dict:
    """
    Returns video metadata using ffprobe:
    {duration, width, height, fps, codec}
    """
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            file_path,
        ],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        return {}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

    video_stream = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
        {},
    )

    fmt = data.get("format", {})

    # Parse fps from r_frame_rate (e.g. "30/1")
    fps_str = video_stream.get("r_frame_rate", "0/1")
    try:
        num, den = fps_str.split("/")
        fps = float(num) / float(den) if float(den) else 0.0
    except (ValueError, ZeroDivisionError):
        fps = 0.0

    return {
        "duration": float(fmt.get("duration", 0.0)),
        "width": int(video_stream.get("width", 0)),
        "height": int(video_stream.get("height", 0)),
        "fps": round(fps, 2),
        "codec": video_stream.get("codec_name", "unknown"),
    }
