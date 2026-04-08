# adds shapes to the grid

def rectangle(x0,y0,dx,dy, grid, material=1):
    for x in range(dx):
        for y in range(dy):
            grid[y+y0, x+x0] = material # solid
    return(grid)
