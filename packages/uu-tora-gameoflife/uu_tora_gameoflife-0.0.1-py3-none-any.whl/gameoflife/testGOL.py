import gameOfLife as gl
import numpy as np
import pytest

def test_updateCells():
    """Test that updateCells updates the grid correctly. 
    
    In a checkered grid, each cell has 4 live neighbours, i.e., all will die"""
    N = 32
    grid = np.array([])
    squareGrid = gl.squareGrid(N)
    zeroGrid = np.zeros((N,N))
    for i in range(1000):
        squareGrid = gl.updateCells(squareGrid, N)
    assert np.array_equal(squareGrid, zeroGrid)
