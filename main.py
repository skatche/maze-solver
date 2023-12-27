from tkinter import Tk, BOTH, Canvas
import time

# --- Main window class

class Window:
    def __init__(self, width, height):
        self.root_widget = Tk()
        self.root_widget.title = "Test"
        self.root_widget.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = Canvas(self.root_widget, width=width, height=height)
        self.canvas.pack()
        self.running = False
    
    def redraw(self):
        self.root_widget.update_idletasks()
        self.root_widget.update()
    
    def wait_for_close(self):
        self.running = True
        while self.running:
            self.redraw()
    
    def close(self):
        self.running = False
    
    # - Utlities
    
    def draw_line(self, line, fill_color):
        line.draw(self.canvas, fill_color)

    def draw_cell(self, cell, fill_color):
        cell.draw(self.canvas, fill_color)
    
    def draw_move(self, cell1, cell2, undo=False):
        cell1.draw_move(self.canvas, cell2, undo=undo)

# --- Geometry classes

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Line:
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2
    
    def draw(self, canvas, fill_color):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=fill_color, width=2)
        canvas.pack()

class Cell:
    def __init__(self, x1, x2, y1, y2):
        # (x1, y1) is top left, (x2, y2) is bottom right
        self.x1, self.x2 = min(x1, x2), max(x1, x2)
        self.y1, self.y2 = min(y1, y2), max(y1, y2)
        self.has_left_wall = self.has_right_wall = True
        self.has_top_wall = self.has_bottom_wall = True
    
    def draw(self, canvas, fill_color):
        top_left = Point(self.x1, self.y1)
        top_right = Point(self.x2, self.y1)
        bottom_left = Point(self.x1, self.y2)
        bottom_right = Point(self.x2, self.y2)

        lines = []
        if self.has_left_wall:
            lines.append(Line(top_left, bottom_left))
        if self.has_right_wall:
            lines.append(Line(top_right, bottom_right))
        if self.has_top_wall:
            lines.append(Line(top_left, top_right))
        if self.has_bottom_wall:
            lines.append(Line(bottom_left, bottom_right))
        
        for L in lines:
            L.draw(canvas, fill_color)

    def center(self):
        return Point((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)
    
    def draw_move(self, canvas, target, undo=False):
        line = Line(self.center(), target.center())
        line.draw(canvas, "gray" if undo else "red")

# --- Maze class

class Maze:
    def __init__(
        self,
        x1, y1,
        num_cols, num_rows,
        cell_size_x, cell_size_y,
        win
    ):
        self.x1, self.y1 = x1, y1
        self.num_rows, self.num_cols = num_rows, num_cols
        self.cell_size_x, self.cell_size_y = cell_size_x, cell_size_y
        self.win = win

        self._create_cells()
    
    def _create_cells(self):
        self.cells = []
        x_pos = [self.x1 + n * self.cell_size_x for n in range(self.num_cols + 1)]
        y_pos = [self.y1 + n * self.cell_size_y for n in range(self.num_rows + 1)]
        for x in range(self.num_cols):
            self.cells.append([])
            for y in range(self.num_rows):
                self.cells[x].append(Cell(x_pos[x], x_pos[x+1], y_pos[y], y_pos[y+1]))
        
        self._draw_cells()

    def _draw_cells(self):
        for col in self.cells:
            for c in col:
                self.win.draw_cell(c, fill_color="black")
                self._animate()
    
    def _animate(self):
        self.win.redraw()
        time.sleep(0.02)

# --- Main function

def main():
    win = Window(800, 600)
    maze = Maze(49, 49, 15, 11, 50, 50, win)

    win.wait_for_close()

main()