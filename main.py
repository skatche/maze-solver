from tkinter import Tk, BOTH, Canvas
import time, random

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

    def draw_cell(self, cell, fill_color="black"):
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

        self.visited = False
    
    def draw(self, canvas, fill_color="black"):
        top_left = Point(self.x1, self.y1)
        top_right = Point(self.x2, self.y1)
        bottom_left = Point(self.x1, self.y2)
        bottom_right = Point(self.x2, self.y2)

        lines = []
        left_color = fill_color if self.has_left_wall else "white"
        right_color = fill_color if self.has_right_wall else "white"
        top_color = fill_color if self.has_top_wall else "white"
        bottom_color = fill_color if self.has_bottom_wall else "white"
        lines.append((Line(top_left, bottom_left), left_color))
        lines.append((Line(top_right, bottom_right), right_color))
        lines.append((Line(top_left, top_right), top_color))
        lines.append((Line(bottom_left, bottom_right), bottom_color))
        
        for (L, color) in lines:
            L.draw(canvas, color)

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
        win=None
    ):
        self.x1, self.y1 = x1, y1
        self.num_rows, self.num_cols = num_rows, num_cols
        self.cell_size_x, self.cell_size_y = cell_size_x, cell_size_y
        self.win = win

        self._create_cells()
        self._break_entrance_and_exit()
        self.break_walls()
        self._reset_visited()
        self.solve()
    
    def _create_cells(self):
        self.cells = []
        x_pos = [self.x1 + n * self.cell_size_x for n in range(self.num_cols + 1)]
        y_pos = [self.y1 + n * self.cell_size_y for n in range(self.num_rows + 1)]
        for x in range(self.num_cols):
            self.cells.append([])
            for y in range(self.num_rows):
                self.cells[x].append(Cell(x_pos[x], x_pos[x+1], y_pos[y], y_pos[y+1]))
        
        if self.win is not None:
            self._draw_cells()

    def _draw_cells(self):
        for col in self.cells:
            for c in col:
                self.win.draw_cell(c, fill_color="black")
                self._animate()
    
    def _animate(self):
        self.win.redraw()
        time.sleep(0.02)
    
    def _break_entrance_and_exit(self):
        self.cells[0][0].has_left_wall = False
        self.win.draw_cell(self.cells[0][0])
        self.cells[self.num_cols - 1][self.num_rows - 1].has_right_wall = False
        self.win.draw_cell(self.cells[self.num_cols - 1][self.num_rows - 1])
    
    def break_walls(self):
        self._break_walls_r(0, 0)

    def _break_walls_r(self, i, j):
        self.cells[i][j].visited = True
        while True:
            neighbors = [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]
            # filter first for bounds, second for visited
            neighbors = list(filter(lambda pos: 0 <= pos[0] < self.num_cols and 0 <= pos[1] < self.num_rows, neighbors))
            neighbors = list(filter(lambda pos: not self.cells[pos[0]][pos[1]].visited, neighbors))

            if len(neighbors) == 0:
                self.win.draw_cell(self.cells[i][j])
                self._animate()
                return
            
            dir = random.choice(neighbors)
            dx, dy = dir[0] - i, dir[1] - j
            match (dx, dy):
                case (1, 0):
                    self.cells[i][j].has_right_wall = False
                    self.cells[i+1][j].has_left_wall = False
                case (-1, 0):
                    self.cells[i][j].has_left_wall = False
                    self.cells[i-1][j].has_right_wall = False
                case (0, 1):
                    self.cells[i][j].has_bottom_wall = False
                    self.cells[i][j+1].has_top_wall = False
                case (0, -1):
                    self.cells[i][j].has_top_wall = False
                    self.cells[i][j-1].has_bottom_wall = False
            self.win.draw_cell(self.cells[i][j])
            self._animate()
            self._break_walls_r(dir[0], dir[1])

    def _reset_visited(self):
        for col in self.cells:
            for cell in col:
                cell.visited = False
    
    def solve(self):
        return self._solve_r (0, 0)

    def _solve_r(self, i, j):
        self.cells[i][j].visited = True

        if (i, j) == (self.num_cols - 1, self.num_rows - 1):
            return True
        
        neighbors = [(i+1, j), (i, j+1), (i-1, j), (i, j-1)]
        neighbors = list(filter(lambda pos: 0 <= pos[0] < self.num_cols and 0 <= pos[1] < self.num_rows, neighbors))
        neighbors = list(filter(lambda pos: not self.cells[pos[0]][pos[1]].visited, neighbors))

        if len(neighbors) == 0:
            return False
        
        for n in neighbors:
            dx, dy = n[0] - i, n[1] - j
            match (dx, dy):
                case (1, 0):
                    visitable = not self.cells[i][j].has_right_wall
                case (-1, 0):
                    visitable = not self.cells[i][j].has_left_wall
                case (0, 1):
                    visitable = not self.cells[i][j].has_bottom_wall
                case (0, -1):
                    visitable = not self.cells[i][j].has_top_wall
            print (f"Attempting to move to ({n[0]}, {n[1]}). Visitable: {visitable}")
            if visitable:
                self.win.draw_move (self.cells[i][j], self.cells[n[0]][n[1]])
                self._animate()
                if self._solve_r(n[0], n[1]):
                    return True
                self.win.draw_move (self.cells[n[0]][n[1]], self.cells[i][j], undo=True)
                self._animate()
        return False

# --- Main function

def main():
    win = Window(800, 600)
    maze = Maze(49, 49, 15, 11, 50, 50, win)

    win.wait_for_close()

main()