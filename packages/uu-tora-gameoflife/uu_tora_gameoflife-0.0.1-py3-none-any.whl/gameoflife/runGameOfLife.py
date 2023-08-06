import numpy as np
import matplotlib.pyplot as plt
import gameOfLife as gl

## Initializing parameters ##

# Create random and cross grids of size NxN
N = 32 
randomGrid = np.array([])
randomGrid = gl.randomGrid(N)
crossGrid = np.array([])
crossGrid = gl.crossGrid(N)

# Number of iterations 
steps = 100

### Create Game of Life for cross grid and random grid as initial seeds ###
for i in range(steps):
    crossGrid = gl.updateCells(crossGrid,N)
    randomGrid = gl.updateCells(randomGrid,N)

# Plot final configuration and save as .png
plt.figure(1)
plt.imshow(crossGrid)
plt.title('Initial pattern: Cross, 100 iterations')
plt.savefig('cross_100steps.png')

plt.figure(2)
plt.imshow(randomGrid)
plt.title('Initial pattern: random, 100 iterations')
plt.savefig('random_100steps.png')

