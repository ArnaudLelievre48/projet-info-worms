# adds shapes to the grid

Nx, Ny = 200, 100

def rectangle(x0,y0,dx,dy, object_id, grid, material=1, texture=1):
    for x in range(dx):
        for y in range(dy):
            grid[y+y0][x+x0] = (material,object_id, texture)
    return(grid)


def triangle(x0,y0,dx,dy, object_id, grid, material=1, texture=1):
    for x in range(dx):
        for y in range(dy):
            if x <= dx/2:
                if y<=(dy/(dx/2))*x:
                    grid[y+y0][x+x0] = (material, object_id, texture)
            else:
                if y<=2*dy - (dy/(dx/2))*x:
                    grid[y+y0][x+x0] = (material, object_id, texture)
    return(grid)

def h_circle(x0,y0,r, object_id, grid, material=1, texture=1):
    for x in range(2*r):
        for y in range(r):
            if y**2 + (x-r)**2 <= r**2:
                grid[y+y0][x+x0-r]=(material, object_id, texture)
    return grid

def transform(grid, x_0, y_0, radius, material):
    for x in range(Nx):
        for y in range(Ny):
            if ( (x - x_0)**2 + (y - y_0)**2 ) < ( radius**2) :
                if grid[y][x][0] != 0:
                    grid[y][x][0] = material
                    grid[y][x][2] = material
                    if material == 0:
                        grid[y][x][1] = 0
    return grid


