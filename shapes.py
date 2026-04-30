# adds shapes to the grid

def rectangle(x0,y0,dx,dy, object_id, grid, material=1):
    for x in range(dx):
        for y in range(dy):
            grid[y+y0, x+x0] = (material,object_id)
    return(grid)


def triangle(x0,y0,dx,dy, object_id, grid, material=1):
    for x in range(dx):
        for y in range(dy):
            if x <= dx/2:
                if y<=(dy/(dx/2))*x:
                    grid[y+y0, x+x0] = (material,object_id)
            else:
                if y>=(dy/(dx/2))*x:
                    grid[y+y0, x+x0] = (material,object_id)
    return(grid)

def h_circle (x0,y0,r, object_id, grid, material=1):
    for x in range(int(2*r)):
        for y in range(int(r*sin(Arcos(x/r))):
            grid[y+y0,x+x0]=(material,object_id)
	return grid
