import os
import numpy as np
from numba import njit, prange
import cv2

# Get paths
video_path = input("Enter Input Path: ")
output_folder = input("Enter Output Folder: ")

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Open video file
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Create VideoWriter object
output_path = os.path.join(output_folder, "pixel_art_video.mp4")
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))


def reduce_colors(image, k=8):
    # Reshape image to be a list of pixels
    pixels = image.reshape((-1, 3))

    # Convert to float
    pixels = np.float32(pixels)

    # Define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, palette = cv2.kmeans(
        pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )

    # Convert back to 8 bit values
    palette = np.uint8(palette)

    # Map labels to the palette colors
    quantized = palette[labels.flatten()]

    # Reshape back to original image shape
    quantized = quantized.reshape(image.shape)

    return quantized


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame to 192x108 to create pixel art effect
    small_frame = cv2.resize(frame, (192, 108), interpolation=cv2.INTER_LINEAR)

    # Reduce the number of colors to 8
    small_frame = reduce_colors(small_frame, k=16)

    # Scale back to 1920x1080
    pixel_art_frame = cv2.resize(
        small_frame, (frame_width, frame_height), interpolation=cv2.INTER_NEAREST
    )

    # Write frame to the output video
    out.write(pixel_art_frame)

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Pixel art video saved to {output_path}")
