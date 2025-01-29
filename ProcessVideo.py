import os
import numpy as np
from numba import njit, prange
import cv2

# settings (kernal size must be odd)
kernalSize = 51
afterKernalSize = 0
numColours = 10
gradientOffset = 1.25

gradient_start = 0xCBE7F7
gradient_end = 0x0E2054


# apply gradient to the grayscale image
@njit(parallel=True)
def apply_gradient(gray_frame, gradient_start, gradient_end):
    # Extract RGB components of the gradient start and end colors
    start_r = (gradient_start >> 16) & 0xFF
    start_g = (gradient_start >> 8) & 0xFF
    start_b = gradient_start & 0xFF

    end_r = (gradient_end >> 16) & 0xFF
    end_g = (gradient_end >> 8) & 0xFF
    end_b = gradient_end & 0xFF

    # Initialize color frame
    color_frame = np.zeros(
        (gray_frame.shape[0], gray_frame.shape[1], 3), dtype=np.uint8
    )

    # Apply the gradient
    for i in prange(gray_frame.shape[0]):
        for j in range(gray_frame.shape[1]):
            gray_value = gray_frame[i, j]
            if gray_value == 0:
                color_frame[i, j] = [0, 0, 0]
            else:
                r = start_r + (end_r - start_r) * gray_value * gradientOffset / 255
                g = start_g + (end_g - start_g) * gray_value * gradientOffset / 255
                b = start_b + (end_b - start_b) * gray_value * gradientOffset / 255
                r = min(max(r, 0), 255)
                g = min(max(g, 0), 255)
                b = min(max(b, 0), 255)
                color_frame[i, j] = [b, g, r]

    return color_frame


def main(kernalSize, gradient_start, gradient_end):

    # Find most recent animation
    folder_index = 0
    while os.path.exists(f"Animations/{folder_index + 1}"):
        folder_index += 1

    output_folder = f"Animations/{folder_index}/render"

    input_video_path = os.path.join(output_folder, "output.mp4")
    output_video_path = os.path.join(
        output_folder,
        f"processed_output_{kernalSize}_{numColours}_{gradientOffset}.mp4",
    )

    # Open input video
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Could not open video at", input_video_path)
        return

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Create VideoWriter object
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    previous_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        print("Processing frame", cap.get(cv2.CAP_PROP_POS_FRAMES), end="")
        print(f"/{cap.get(cv2.CAP_PROP_FRAME_COUNT)}")

        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply blur to the frame
        blurred_frame = cv2.GaussianBlur(gray_frame, (kernalSize, kernalSize), 0)

        # increase contrast
        contrast_frame = cv2.normalize(
            blurred_frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX
        )

        # do additional blur to smooth colours
        if afterKernalSize != 0:
            contrast_frame = cv2.GaussianBlur(
                contrast_frame, (afterKernalSize, afterKernalSize), 0
            )

        # reduce number of colours to 5
        blurred_frame = cv2.normalize(
            blurred_frame, None, alpha=0, beta=numColours, norm_type=cv2.NORM_MINMAX
        )

        # scale back to 0-255
        blurred_frame = cv2.normalize(
            blurred_frame, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX
        )

        # Apply gradient to grayscale image
        color_frame = apply_gradient(contrast_frame, gradient_start, gradient_end)

        # Average with the previous frame if it exists
        if previous_frame is not None:
            color_frame = cv2.addWeighted(color_frame, 0.7, previous_frame, 0.3, 0)

        # Write the final frame to the output video
        out.write(color_frame)

        # Update the previous frame
        previous_frame = color_frame

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main(kernalSize, gradient_start, gradient_end)
