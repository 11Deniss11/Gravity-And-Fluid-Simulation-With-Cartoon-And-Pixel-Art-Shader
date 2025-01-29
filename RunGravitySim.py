import numpy as np
from numba import njit, prange
import os
from PIL import Image
import time

# Settings
size = np.array([1920, 1080])
numParticles = 1000
numSteps = 10000
saveInterval = 3

gravityCeof = 1
universalAttractorCoef = 0.000003  # 0.000001
universalDragCoef = 0.99999
bounceCoef = 0
maxSpeed = 20
particleSize = 2
maxRandomStartSpeed = 0.001
notRandomStartSpeed = 0.4

# Initialize positions of particles
positions = np.zeros((numParticles, 2))
for i in range(numParticles):
    randomX = 0
    randomY = 0
    while True:
        randomX = np.random.uniform(-size[1] / 2, size[1] / 2)
        randomY = np.random.uniform(-size[1] / 2, size[1] / 2)
        randomRadius = np.sqrt(randomX**2 + randomY**2)
        if randomRadius < size[1] / 2:
            break
    positions[i] = np.array([randomX, randomY])

# Initialize velocities of particles perpendicular to center with random offset
velocities = np.zeros((numParticles, 2))
for i in range(numParticles):
    radius = np.linalg.norm(positions[i])
    if radius != 0:
        # Calculate the perpendicular vector (clockwise)
        perpendicular = np.array([-positions[i][1], positions[i][0]])
        perpendicular /= np.linalg.norm(
            perpendicular
        )  # Normalize the perpendicular vector
        # Apply start speed (option to make faster closer to origin)
        start_speed = notRandomStartSpeed  # * (1 / np.sqrt(radius + 20))
        velocities[i] = perpendicular * start_speed
        velocities[i] += np.random.uniform(-maxRandomStartSpeed, maxRandomStartSpeed, 2)


# Should run the loop in parallel on CPU
@njit(parallel=True, fastmath=True)
def calculateFrame(positions, velocities):
    image = np.zeros((size[1], size[0]), dtype=np.uint8)
    averagePosition = np.zeros(2)

    # calculate average position of all particles
    for k in range(2):
        averagePosition[k] = np.sum(positions[:, k]) / numParticles

    # This segment runs in parallel I think, the prange
    for i in prange(numParticles):
        for j in range(numParticles):
            if i != j:
                r = positions[j] - positions[i]
                if r[0] > 200 or r[1] > 200:
                    continue
                rhat = r / np.linalg.norm(r)
                r = rhat * (
                    np.linalg.norm(r) + 9
                )  # putting a minimum distance to avoid division by close to zero which causes unwanted behavior

                if np.linalg.norm(r) < particleSize * 2:
                    # if collision occures:
                    v = velocities[j] - velocities[i]
                    vhat = v / np.linalg.norm(v)
                    avgVelocity = (velocities[i] + velocities[j]) / 2
                    # average the velocities
                    velocities[i] = avgVelocity
                    velocities[j] = avgVelocity
                    # apply bounce (assuming not all averaged)
                    velocities[i] += v * np.dot(vhat, -rhat) * bounceCoef
                    velocities[j] += v * np.dot(vhat, rhat) * bounceCoef
                    # move the particles apart
                    positions[i] -= rhat * (particleSize / 2 + 0.1)
                    positions[j] += rhat * (particleSize / 2 + 0.1)
                else:
                    # apply gravity
                    gravityForce = gravityCeof * rhat / np.linalg.norm(r) ** 2
                    velocities[i] += gravityForce

        # Apply universal attractor toward average position
        velocities[i] += universalAttractorCoef * (averagePosition - positions[i])
        velocities[i] *= universalDragCoef
        if np.linalg.norm(velocities[i]) > maxSpeed:
            velocities[i] = velocities[i] / np.linalg.norm(velocities[i]) * maxSpeed
        positions[i] += velocities[i]

        x, y = positions[i]

        # write pixel to image
        x, y = (
            int(x + size[0] / 2 - averagePosition[0]),
            int(y + size[1] / 2 - averagePosition[1]),
        )
        if 0 <= x < size[0] and 0 <= y < size[1] and np.linalg.norm(velocities[i]) < 19:
            image[y, x] = 255
    return image


def main():
    start_time = time.time()

    # make output parent folder in current directory if not exists
    if not os.path.exists("Animations"):
        os.makedirs("Animations")

    # find next available folder index
    folder_index = 0
    while os.path.exists(f"Animations/{folder_index}"):
        folder_index += 1

    # make the output folder
    output_folder = f"Animations/{folder_index}"
    os.makedirs(output_folder)

    # run simulation
    frameNum = 0
    for i in range(numSteps):
        print(f"Step {i}/{numSteps}")
        if i % saveInterval == 0:
            image = calculateFrame(positions, velocities)
            # save frame as image in output folder
            Image.fromarray(image).save(f"{output_folder}/{frameNum}.png")
            frameNum += 1
        else:
            calculateFrame(positions, velocities)

    # render frames as a video
    render_folder = f"Animations/{folder_index}/render"
    os.makedirs(render_folder)
    os.system(
        f"ffmpeg -r 60 -i {output_folder}/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p {render_folder}/output.mp4"
    )

    print(f"--- {time.time() - start_time} seconds ---")
    print(f"--- {(time.time() - start_time) / 60} minutes ---")
    print(f"--- {(time.time() - start_time) / 3600} hours ---")


if __name__ == "__main__":
    main()
