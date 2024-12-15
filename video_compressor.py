import subprocess
import os

def compress_video(input_path, output_path, crf=23):
    """
    Compress a video file using FFmpeg.
    """
    ffmpeg_path = r"C:\Users\HP\Desktop\imgvid\ffmpeg-7.1-full_build\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
    try:
        # Ensure output path directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        command = [
            ffmpeg_path,
            "-y",  # Overwrite existing output file
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", str(crf),
            output_path
        ]

        print("Running FFmpeg Command:", " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("FFmpeg Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Error compressing video:", e.stderr)
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False
