# inspired from https://stackoverflow.com/questions/30023763/how-to-make-an-interactive-2d-grid-in-a-window-in-python

from tkinter import *
from tkinter import ttk
import numpy as np

class Cell():
    FILLED_COLOR_BG = "blue"
    EMPTY_COLOR_BG = "black"
    FILLED_COLOR_BORDER = "blue"
    EMPTY_COLOR_BORDER = "white"

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill= False

    def _switch(self):
        """ Switch if the cell is filled or not. """
        self.fill= not self.fill

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None :
            fill = Cell.FILLED_COLOR_BG
            outline = Cell.FILLED_COLOR_BORDER

            if not self.fill:
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
        self.draw_romi()
        if self.gui_debug:
            self.after(4000, self.draw)

    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def handleMouseClick(self, event):
        row, column = self._eventCoords(event)
        cell = self.g[row][column]
        cell._switch()
        cell.draw()
        #add the cell to the list of cell switched during the click
        self.switched.append(cell)
        self.addTargetPos(cell.abs, cell.ord)

    def handleMouseMotion(self, event):
        row, column = self._eventCoords(event)
        cell = self.g[row][column]

        if cell not in self.switched:
            cell._switch()
            cell.draw()
            self.switched.append(cell)
    
    def addTargetPos(self, abs, ord):
        x = int((abs + 0.5) * self.parent.cell_to_world) + self.parent.data.top_left[0]
        y = int((ord + 0.5) * self.parent.cell_to_world) + self.parent.data.top_left[1]
        self.parent.data.target_pos.append((x, y))
        self.parent.coord_var.set("GUI:{}, {} CV: {}, {}".format(abs, ord, x, y))


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
        self.widgets(self.num_rows, self.num_cols, gui_debug)

    
    def widgets(self, num_rows, num_cols, gui_debug):
        self.grid_widget = CellGrid(self, num_rows, num_cols, 50, gui_debug)
        self.l1 = ttk.Label(self, text="Coordinates")
        self.coord_var = StringVar()
        self.coord_var.set("0, 0")
        self.l2 = ttk.Label(self, textvariable=self.coord_var)
        
        self.grid_widget.grid(row=0, column=0, columnspan=2)
        self.l1.grid(row=1, column=0)
        self.l2.grid(row=1, column=1)
