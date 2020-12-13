# inspired from https://stackoverflow.com/questions/30023763/how-to-make-an-interactive-2d-grid-in-a-window-in-python

from tkinter import *
from tkinter import ttk
import numpy as np

class Cell():
    FILLED_COLOR_BG = "blue"
    FILLED_COLOR_BORDER = "blue"

    OBSTACLE_COLOR_BG = "red"
    OBSTACLE_COLOR_BORDER = "red"

    EMPTY_COLOR_BG = "black"
    EMPTY_COLOR_BORDER = "white"


    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill= False
        self.obstacle = False

    def _switch(self):
        """ Switch if the cell is filled or not. """
        self.fill= not self.fill

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None :
            if self.obstacle:
                fill = Cell.OBSTACLE_COLOR_BG
                outline = Cell.OBSTACLE_COLOR_BORDER
            elif self.fill:
                fill = Cell.FILLED_COLOR_BG
                outline = Cell.FILLED_COLOR_BORDER
            else:
                fill = Cell.EMPTY_COLOR_BG
                outline = Cell.EMPTY_COLOR_BORDER

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill = fill, outline = outline)

class CellGrid(Canvas):
    def __init__(self, master, rowNumber, columnNumber, cellSize, gui_debug, *args, **kwargs):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        self.parent = master
        self.cellSize = cellSize

        self.g = []
        for row in range(rowNumber):

            line = []
            for column in range(columnNumber):
                line.append(Cell(self, column, row, cellSize))

            self.g.append(line)

        #memorize the cells that have been modified to avoid many switching of state during mouse motion.
        self.switched = []

        #bind click action
        self.bind("<Button-1>", self.handleMouseClick)  
        #bind moving while clicking
        self.bind("<B1-Motion>", self.handleMouseMotion)
        #bind release button action - clear the memory of modified cells.
        self.bind("<ButtonRelease-1>", lambda event: self.switched.clear())
        self.gui_debug = gui_debug
        self.draw()
        self.pack()

    def draw_romi(self):
        romi_x = self.cellSize*(self.parent.data.current_pos[0] - self.parent.data.top_left[0]) / self.parent.cell_to_world
        romi_y = self.cellSize*(self.parent.data.current_pos[1] - self.parent.data.top_left[1]) / self.parent.cell_to_world
        self.create_oval(romi_x-5, romi_y-5, romi_x+5, romi_y+5, outline="#f11", fill="#1f1", width=2)

    def draw(self):
        for row in self.g:
            for cell in row:
                cell.draw()
        if self.gui_debug:
            self.draw_romi()
            self.after(4000, self.draw)

    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def handleMouseClick(self, event):
        row, column = self._eventCoords(event)
        cell = self.g[row][column]
        x, y = self.grid_to_world(cell.abs, cell.ord)
        if not cell.obstacle:
            cell._switch()
            cell.draw()
            #add the cell to the list of cell switched during the click
            self.switched.append(cell)
            self.addTargetPos(x, y)
            self.addTargetGui(cell.ord, cell.abs)

        self.parent.coord_var.set("GUI: {}, {}\t CV: {}, {}".format(cell.ord, cell.abs, x, y))

    def handleMouseMotion(self, event):
        row, column = self._eventCoords(event)
        cell = self.g[row][column]

        if cell not in self.switched:
            cell._switch()
            cell.draw()
            self.switched.append(cell)
    
    def grid_to_world(self, abs, ord):
        x = int((abs + 0.5) * self.parent.cell_to_world) + self.parent.data.top_left[0]
        y = int((ord + 0.5) * self.parent.cell_to_world) + self.parent.data.top_left[1]
        return x, y
    
    def addTargetGui(self, row, col):
        self.parent.targets_gui.append((row, col))

    def addTargetPos(self, x, y):
        self.parent.data.target_pos.append((x, y))
    
    def update_obstacles(self):
        if len(self.parent.obstacle_gui) == 0:
            return
        
        for obs_row, obs_col in self.parent.obstacle_gui:
            cell = self.g[obs_row][obs_col]
            cell.obstacle = True 

        self.draw()


class Gui(Tk):
    def __init__(self, data, gui_debug):
        Tk.__init__(self)
        self.data = data
        self.cell_to_world = 30
        # self.cell_to_world = min(data.width, data.height) // 6
        self.num_rows = data.height // self.cell_to_world
        self.num_cols = data.width // self.cell_to_world
        # self.num_rows = int(np.ceil(data.height / self.cell_to_world))
        # self.num_cols = int(np.ceil(data.width / self.cell_to_world))
        max_x = self.num_cols * self.cell_to_world + self.data.top_left[0]
        max_y = self.num_rows * self.cell_to_world + self.data.top_left[1]
        self.data.gui_bottom_right = [max_x, max_y]

        self.obstacle_grid = np.zeros((self.num_rows, self.num_cols), dtype=int)
        self.obstacle_gui = []
        self.targets_gui = []
        self.widgets(self.num_rows, self.num_cols, gui_debug)

    
    def widgets(self, num_rows, num_cols, gui_debug):
        self.grid_widget = CellGrid(self, num_rows, num_cols, 50, gui_debug)
        self.l1 = ttk.Label(self, text="Coordinates")
        self.coord_var = StringVar()
        self.coord_var.set("GUI: {}, {}\t CV: {}, {}".format(0,0,0,0))
        self.l2 = ttk.Label(self, textvariable=self.coord_var)
        
        self.grid_widget.grid(row=0, column=0, columnspan=2)
        self.l1.grid(row=1, column=0)
        self.l2.grid(row=1, column=1)
    
    def world_to_grid(self, x, y):
        row = (int) (y - self.data.top_left[1]) // self.cell_to_world
        col = (int) (x - self.data.top_left[0]) // self.cell_to_world
        return row, col
    
    def world_to_grid_clipped(self, x, y):
        row = (int) (y - self.data.top_left[1]) // self.cell_to_world
        col = (int) (x - self.data.top_left[0]) // self.cell_to_world
        row = min(max(0, row), self.num_rows - 1)
        col = min(max(0, col), self.num_cols - 1)
        return row, col
    
    def grid_to_world(self, row, col):
        x = int((col + 0.5) * self.cell_to_world) + self.data.top_left[0]
        y = int((row + 0.5) * self.cell_to_world) + self.data.top_left[1]
        return x, y
    
    def display_obstacles_old(self):
        if len(self.data.obstacle_pos) == 0:
            return
        
        for obs_pos in self.data.obstacle_pos:
            if obs_pos[0] < self.data.gui_bottom_right[0] and obs_pos[1] < self.data.gui_bottom_right[1]:
                obs_row, obs_col = self.world_to_grid(obs_pos[0], obs_pos[1])
                # obs_row = (obs_pos[1] - self.data.top_left[1]) // self.cell_to_world
                # obs_col = (obs_pos[0] - self.data.top_left[0]) // self.cell_to_world
                self.obstacle_grid[obs_row][obs_col] = 1
                self.obstacle_gui.append((obs_row, obs_col))
        self.grid_widget.update_obstacles()
    
    def display_obstacles(self):
        if len(self.data.obstacle_pos) == 0:
            return
        
        for obs_pos in self.data.obstacle_pos:
            x, y, w, h = obs_pos
            top_left_gui = self.world_to_grid_clipped(x, y)
            bottom_right_gui = self.world_to_grid_clipped(x + w, y + h)
            for row_i in range(top_left_gui[0], bottom_right_gui[0] + 1):
                for col_j in range(top_left_gui[1], bottom_right_gui[1] + 1):
                    self.obstacle_grid[row_i][col_j] = 1
                    self.obstacle_gui.append((row_i, col_j))

        self.grid_widget.update_obstacles()
        
    def reroute(self):
        new_targets_gui = []
        cur_pos_gui = self.world_to_grid(self.data.current_pos[0], self.data.current_pos[1])
        cur_targets = [cur_pos_gui] + self.targets_gui
        # print(cur_targets)
        for i in range(len(cur_targets) - 1):
            start = cur_targets[i]
            end = cur_targets[i + 1]
            path = astar(self.obstacle_grid, start, end)
            # print(path)
            pruned_path = self.prune_paths(path)
            # print(pruned_path)
            new_targets_gui += pruned_path
        
        new_targets_world = []
        for t in new_targets_gui:
            new_targets_world.append(self.grid_to_world(t[0], t[1]))
        print("Old Targets World:", self.data.target_pos)
        print("Old Targets Gui:", self.targets_gui)
        print("New Targets Gui:", new_targets_gui)
        print("New Targets World:", new_targets_world)
        self.data.target_pos = new_targets_world
    
    def prune_paths(self, path):
        if len(path) < 3:
            return path
        pruned_path = []
        for i in range(1, len(path) - 1):
            cur = path[i]
            prv = path[i-1]
            nxt = path[i+1]
            if cur[0] == prv[0] and cur[0] == nxt[0]:
                continue
            elif cur[1] == prv[1] and cur[1] == nxt[1]:
                continue
            else:
                pruned_path.append(cur)
        
        # append last element 
        # (first element is ignored since its added by prev call to prune)
        pruned_path.append(path[-1])
        return pruned_path

# Credit for this: Nicholas Swift
# as found at https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
from warnings import warn
import heapq

class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
    
    def __repr__(self):
      return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
      return self.f < other.f
    
    # defining greater than for purposes of heap queue
    def __gt__(self, other):
      return self.f > other.f

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path


def astar(maze, start, end, allow_diagonal_movement = False):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    :param maze:
    :param start:
    :param end:
    :return:
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list) 
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (len(maze[0]) * len(maze) // 2)

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    if allow_diagonal_movement:
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1

        if outer_iterations > max_iterations:
          # if we hit this point return the path such as it is
          # it will not contain the destination
          warn("giving up on pathfinding too many iterations")
          return return_path(current_node)       
        
        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Generate children
        children = []
        
        for new_position in adjacent_squares: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    warn("Couldn't get a path to destination")
    return None

