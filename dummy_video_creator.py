import cv2
import numpy as np

def create_dummy_video(output_path, width=640, height=480, fps=24, duration=5):
    """
    Simple video file banane ka code.
    """
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    total_frames = fps * duration

    for _ in range(total_frames):
        # Random color ke frames banata hai
        frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    print(f"Dummy video created successfully at {output_path}")

# Example Call
create_dummy_video("dummy_video.avi", duration=5)
