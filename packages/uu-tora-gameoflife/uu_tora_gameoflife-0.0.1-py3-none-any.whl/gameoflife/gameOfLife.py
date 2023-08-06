import numpy as np
import matplotlib.pyplot as plt

# Setting values for grid
live = 255
dead = 0
vals = [live,dead]

def squareGrid(N):
    """returns an NxN grid with every other cell alive"""
    a = np.array([vals,np.flipud(vals)]) # create repetative unit grid, [[live, dead],[dead, alive]]
    return np.tile(a,(int(N/2),int(N/2)))

def crossGrid(N):
    """returns an NxN grid with a cross shaped initial pattern"""
    a = np.zeros((N,N)) # all dead
    a[[int(N/2)],:] = live
    a[:,[int(N/2)]] = live
    return a

def randomGrid(N):
    """returns an NxN grid with random dead/alive positions"""
    return np.random.choice(vals, N*N, p=[0.5, 0.5]).reshape(N, N)

def updateCells(grid, N):
    """changes the grid according to Conway's rules"""
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # Calculate the sum of all neighbors
            neighborSum = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                     grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                     grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                     grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N])/255)
            
            # Decide fate depending on sum and Conway's rules
            # if current cell is alive and has anything but 2 or 3 neighbors, kill it
            if grid[i, j]  == live: 
                if (neighborSum < 2) or (neighborSum > 3):
                    newGrid[i, j] = dead
            # if current cell is dead and has exactly 3 neighbors, make it alive
            else:
                if neighborSum == 3:
                    newGrid[i, j] = live
        
    # update grid
    grid[:] = newGrid[:]
    return grid

#def main():
    # set grid size and initialize grid
    #N = 32
    #grid = np.array([])
    # try square grid
    #grid = squareGrid(N)
    #steps = 100
    
    ##for i in range(steps):
    ##    grid = updateCells(grid,N)
    ##    plt.imshow(grid)
    
    #grid = updateCells(grid, N)
    #plt.imshow(grid)
        
#if __name__ == '__main__':
    #main()
    
    