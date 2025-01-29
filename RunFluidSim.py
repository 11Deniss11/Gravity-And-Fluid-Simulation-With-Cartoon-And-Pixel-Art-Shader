import numpy as np
from numba import njit, prange
import os
from PIL import Image
import time

# Settings
size = np.array([1920, 1080])
numParticles = 2000
numSteps = 1500
saveInterval = 2

gravityCeof = 0.2
particleRepulsionCoef = 4
wallRepulsionCoef = 4
wallRepulsionForce = 4
cornerRepulsionForce = 2
cornerRadius = 15
wallBounceCoef = 0.1
globalDragCoef = 0.99
minParticlesForTotalFriction = 150
maxSpeed = 21

containerWidth = size[0] / 1
containerHeight = size[1]

spawnBoxWidth = 900
spawnBoxHeight = 1000
spawnBoxLocation = np.array([size[0] / 3 - 30, size[1] / 2])

# Initialize positions of particles
positions = np.zeros((numParticles, 2))
for i in range(numParticles):
    randomX = 0
    randomY = 0
    randomX = np.random.uniform(
        spawnBoxLocation[0] - spawnBoxWidth / 2,
        spawnBoxLocation[0] + spawnBoxWidth / 2,
    )
    randomY = np.random.uniform(
        spawnBoxLocation[1] - spawnBoxHeight / 2,
        spawnBoxLocation[1] + spawnBoxHeight / 2,
    )
    positions[i] = np.array([randomX, randomY])

# Initialize velocities of particles
velocities = np.zeros((numParticles, 2))


# Should run the loop in parallel on CPU
@njit(parallel=True, fastmath=True)
def calculateFrame(positions, velocities):
    image = np.zeros((size[1], size[0]), dtype=np.uint8)
    # keeping track of density and average velocity for a second loop
    numParticlesInRangeOfEachParticle = np.zeros(numParticles)
    avgVelocityOfParticlesInRangeOfEachParticle = np.zeros((numParticles, 2))
    for i in prange(numParticles):
        for j in range(numParticles):
            if i != j:
                r = positions[j] - positions[i]
                rMagnitude = np.linalg.norm(r)
                # repulsion between particles and calculating density and avg velocity
                if rMagnitude != 0 and rMagnitude < 15:
                    r /= rMagnitude
                    velocities[i] -= (r * particleRepulsionCoef) / np.power(
                        rMagnitude, 1
                    )
                    numParticlesInRangeOfEachParticle[i] += 1
                    avgVelocityOfParticlesInRangeOfEachParticle[i] += velocities[j]

        # wall repulsion (treated as one particle)
        def wallRepulsion(position, wall):
            r = wall - position
            rMagnitude = np.linalg.norm(r)
            if rMagnitude != 0 and rMagnitude < 15:
                r /= rMagnitude
                velocities[i] -= r * wallRepulsionCoef / np.power(rMagnitude, 1)
                return 1  # minParticlesForTotalFriction / 40
            return 0

        # calculating wall repulsion but not for more than 1 wall
        wallFrictionParticlesInRange = 0
        wallFrictionParticlesInRange += wallRepulsion(
            positions[i],
            np.array([-containerWidth / 2 + size[0] / 2, positions[i][1]]),
        )
        if wallFrictionParticlesInRange == 0:
            wallFrictionParticlesInRange += wallRepulsion(
                positions[i],
                np.array([containerWidth / 2 + size[0] / 2, positions[i][1]]),
            )
        if wallFrictionParticlesInRange == 0:
            wallFrictionParticlesInRange += wallRepulsion(
                positions[i],
                np.array([positions[i][0], 5]),
            )
        if wallFrictionParticlesInRange == 0:
            wallFrictionParticlesInRange += wallRepulsion(
                positions[i],
                np.array([positions[i][0], containerHeight]),
            )

        numParticlesInRangeOfEachParticle[i] += wallFrictionParticlesInRange

    # second loop to apply friction
    for i in prange(numParticles):

        if numParticlesInRangeOfEachParticle[i] != 0:
            avgVelocityOfParticlesInRangeOfEachParticle[
                i
            ] /= numParticlesInRangeOfEachParticle[i]
            frictionPercentage = (
                numParticlesInRangeOfEachParticle[i] / minParticlesForTotalFriction
            )
            frictionPercentage = min(1, frictionPercentage)
            velocities[i] = (
                velocities[i] * (1 - frictionPercentage)
                + avgVelocityOfParticlesInRangeOfEachParticle[i] * frictionPercentage
            )

        # gravity and drag
        velocities[i] += np.array([0, gravityCeof])
        velocities[i] *= globalDragCoef

        # speed limit
        if np.linalg.norm(velocities[i]) > maxSpeed:
            velocities[i] /= np.linalg.norm(velocities[i]) * maxSpeed
        positions[i] += velocities[i]

        # wall collision
        if positions[i][0] < -containerWidth / 2 + size[0] / 2:
            positions[i][0] = -containerWidth / 2 + size[0] / 2 + 3
            velocities[i][0] = (
                -velocities[i][0] * wallBounceCoef
            )  # + wallRepulsionForce
        elif positions[i][0] > containerWidth / 2 + size[0] / 2:
            positions[i][0] = containerWidth / 2 + size[0] / 2 - 3
            velocities[i][0] = (
                -velocities[i][0] * wallBounceCoef
            )  # - wallRepulsionForce
        if positions[i][1] < 5:
            positions[i][1] = 5 + 3
            velocities[i][1] = (
                -velocities[i][1] * wallBounceCoef
            )  # + wallRepulsionForce
        elif positions[i][1] > containerHeight:
            positions[i][1] = containerHeight - 3
            velocities[i][1] = (
                -velocities[i][1] * wallBounceCoef
            )  # - wallRepulsionForce

        # corner repulsion (to reduce bugs in the corners)
        if (
            np.linalg.norm(
                positions[i] - np.array([-containerWidth / 2 + size[0] / 2, 5])
            )
            < cornerRadius
        ):
            velocities[i] += np.array([cornerRepulsionForce, cornerRepulsionForce])
        elif (
            np.linalg.norm(
                positions[i] - np.array([containerWidth / 2 + size[0] / 2, 5])
            )
            < cornerRadius
        ):
            velocities[i] += np.array([-cornerRepulsionForce, cornerRepulsionForce])
        elif (
            np.linalg.norm(
                positions[i]
                - np.array([-containerWidth / 2 + size[0] / 2, containerHeight])
            )
            < cornerRadius
        ):
            velocities[i] += np.array([cornerRepulsionForce, -cornerRepulsionForce])
        elif (
            np.linalg.norm(
                positions[i]
                - np.array([containerWidth / 2 + size[0] / 2, containerHeight])
            )
            < cornerRadius
        ):
            velocities[i] += np.array([-cornerRepulsionForce, -cornerRepulsionForce])

        # write pixel to image
        x = int(positions[i][0])
        y = int(positions[i][1])
        if x >= 0 and x < size[0] and y >= 0 and y < size[1]:
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
