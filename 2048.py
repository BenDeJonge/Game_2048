# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#------------------------------------------------------------------------------

import tkinter as tk  # Drawing root window.
import random         # Placing new cells.
import colors  as c   # Fonts and colors.
import ctypes         # Respect resolution.
import numpy   as np

#------------------------------------------------------------------------------

class Game(tk.Frame):
    def __init__(self):
        # Create a root Frame for the application.
        tk.Frame.__init__(self)
        self.grid()
        self.master.title('2048')
        # Create a frame to house the cells with padding for the score header.
        self.main_grid = tk.Frame(self,
                                  bg=c.GRID_COLOR,
                                  bd=3, 
                                  width=400, 
                                  height=400)
        self.main_grid.grid(pady=(100,0)) 
        self.make_GUI()
        self.start_game()
        # Bind the arrow keys to movement functions.
        self.master.bind("<Left>", self.left)
        self.master.bind("<Right>", self.right)
        self.master.bind("<Up>", self.up)
        self.master.bind("<Down>", self.down)
        # Start the eventloop.
        self.mainloop()
        
    #--------------------------------------------------------------------------
    
    def make_GUI(self):
        '''
        -self.cells: contains a 4x4 2d list of cells. Every element contains dict
                     of the cell frame (the tk object that is moved around) and the
                     cell number (a tk label pasted in each cell).'''
        self.cells = []
        # Populate the board with cells at index (i,j).
        self.cells = np.zeros(dtype='O', shape=(4,4))
        for i in range(4):
            for j in range(4):
                cell_frame = tk.Frame(self.main_grid,
                                      bg=c.EMPTY_CELL_COLOR,
                                      width=150, 
                                      height=150)
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                cell_number = tk.Label(self.main_grid, bg=c.EMPTY_CELL_COLOR)
                cell_number.grid(row=i, column=j)
                cell_data = {"frame": cell_frame, "number": cell_number}
                self.cells[i][j] = cell_data
        # Make a header to display the score.
        score_frame = tk.Frame(self)
        score_frame.place(relx=0.5, rely=0.05, anchor='center')
        # tk.Label(text='Score',
        #           font=c.SCORE_LABEL_FONT,
        #           ).grid(row=0)
        self.score_label = tk.Label(master=score_frame,
                                    text="0",
                                    font=c.SCORE_FONT)
        self.score_label.grid(row=1)
    
    #--------------------------------------------------------------------------
        
    def start_game(self):
        '''Generate a 4x4 matrix. Spawn 2 twos at random locations.'''
        self.matrix = np.zeros(shape=(4,4), dtype=np.uint16)
        self.find_empty_cells()
        for pos in random.sample(self.empty,2):
            self.place_new_value(*pos)
        self.find_empty_cells()
        self.score = 0
    
    #--------------------------------------------------------------------------
    
    def find_empty_cells(self):
        '''Generate a set of the empty cells in the matrix.'''
        self.empty = list( zip(*np.where(self.matrix==0)) )

    #--------------------------------------------------------------------------
    
    def place_new_value(self, row, col, value=2):
        '''Place a number of any value in a cell.'''
        self.matrix[row][col] = value
        self.cells[row][col]['frame'].configure(bg=c.CELL_COLORS[value])
        self.cells[row][col]['number'].configure(
            bg=c.CELL_COLORS[value],
            fg=c.CELL_NUMBER_COLORS[value],
            font=c.CELL_NUMBER_FONTS[value],
            text=str(value))

    #--------------------------------------------------------------------------
    
    def stack(self):
        '''Compress all non-zero numbers to one side of the board, compressing
        all gaps. The function is written in the left direction.'''
        new_matrix = np.zeros(shape=(4,4))
        for i in range(4):
            fill_position = 0
            for j in range(4):
                if self.matrix[i][j] != 0:
                    new_matrix[i][fill_position] = self.matrix[i][j]
                    fill_position += 1
        self.matrix = new_matrix
    
    #--------------------------------------------------------------------------
    
    def combine(self):
        '''Add up all horizontally adjacent non-zero numbers and merges them in
        the left position if they are of equal value.'''
        for i in range(4):
            for j in range(3):
                if self.matrix[i][j] != 0 and self.matrix[i][j] == self.matrix[i][j+1]:
                    self.matrix[i][j] *= 2
                    self.matrix[i][j+1] = 0
                    self.score += int(self.matrix[i][j])
    
    #--------------------------------------------------------------------------
    
    def reverse(self):
        '''Flip the matrix over the vertical axis.'''
        self.matrix = np.fliplr(self.matrix)
     
    #--------------------------------------------------------------------------
    
    def transpose(self):
        '''Transpose the matrix i.e., set M[i][j] to M[j][i].'''
        self.matrix = self.matrix.T
    
    #--------------------------------------------------------------------------
    
    def add_new_tile(self):
        '''Place a 2 or 4 in a random empty cell and update the list of empty cells.'''
        value = random.choice([2,4])
        pos = random.choice(self.empty)
        self.place_new_value(*pos ,value=value)
        self.find_empty_cells()
        
    #--------------------------------------------------------------------------
    
    def update_gui(self):
        '''Display the background and text for every empty or occupied cell.'''
        for i in range(4):
            for j in range(4):
                cell_value = int(self.matrix[i][j])
                if cell_value == 0:
                    self.cells[i][j]['frame'].configure(bg=c.EMPTY_CELL_COLOR)
                    self.cells[i][j]['number'].configure(bg=c.EMPTY_CELL_COLOR, text='')
                else:
                    self.cells[i][j]['frame'].configure(bg=c.CELL_COLORS[cell_value])
                    self.cells[i][j]['number'].configure(bg=c.CELL_COLORS[cell_value],
                                                         fg=c.CELL_NUMBER_COLORS[cell_value],
                                                         font=c.CELL_NUMBER_FONTS[cell_value],
                                                         text=str(cell_value)
                                                         )
        self.score_label.configure(text=self.score)
        self.update_idletasks()

    #--------------------------------------------------------------------------

    def move(self, matrix_mod=None):
        '''Template for a move function. Execute matrix modifications if needed.'''
        old_matrix = self.matrix.copy()
        if matrix_mod:
            for fun in matrix_mod:
                fun()
        self.stack()
        self.combine()
        self.stack()
        if matrix_mod:
            for fun in matrix_mod[::-1]:
                fun()
        if not np.all(np.equal(self.matrix, old_matrix)):
            self.find_empty_cells()
            self.add_new_tile()
        self.update_gui()
        self.game_over()

    #--------------------------------------------------------------------------

    def left(self, *args):
        self.move()

    #--------------------------------------------------------------------------

    def right(self, *args):
        self.move([self.reverse])

    #--------------------------------------------------------------------------

    def up(self, *args):
        self.move([self.transpose])

    #--------------------------------------------------------------------------

    def down(self, *args):
        self.move([self.transpose, self.reverse])

    #--------------------------------------------------------------------------

    def valid_move_exists(self):
        '''Check if any matrix element is equal to a neighbor.'''
        for i in range(3):
            for j in range(3):
                if self.matrix[i][j] == self.matrix[i][j+1] or self.matrix[i][j] == self.matrix[i+1][j]:
                    return True
                    break
        return False

    #--------------------------------------------------------------------------

    def game_over(self):
        if np.any(self.matrix>=2048):
            game_over_frame = tk.Frame(self.main_grid, borderwidth=2)
            game_over_frame.place(relx=0.5, rely=0.5, anchor='center')
            tk.Label(game_over_frame,
            text='You win!',
            bg=c.WINNER_BG,
            fg=c.GAME_OVER_FONT_COLOR,
            font=c.GAME_OVER_FONT).pack()
            self.master.after(3000, self.master.destroy)
        elif not np.any(self.matrix == 0) and not self.valid_move_exists():
            game_over_frame = tk.Frame(self.main_grid, borderwidth=2)
            game_over_frame.place(relx=0.5, rely=0.5, anchor='center')
            tk.Label(game_over_frame,
            text='You lose!',
            bg=c.LOSER_BG,
            fg=c.GAME_OVER_FONT_COLOR,
            font=c.GAME_OVER_FONT).pack()
            self.master.after(3000, self.master.destroy)

#------------------------------------------------------------------------------

ctypes.windll.shcore.SetProcessDpiAwareness(2)

def main():
    g = Game()

if __name__ == '__main__':
    main()