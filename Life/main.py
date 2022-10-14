import sys
import tkinter
from tkinter import Button, filedialog
import pygame
pygame.init()

class Colours:
    RED = (200,0,0)
    GREEN = (0,200,0)
    BLUE = (0,0,200)
    YELLOW = (255,255,0)
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    GREY = (100,100,100)


class Board:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.live_cells = []
    
    def getLiveNeighbours(self,coord):
        cell_x, cell_y = coord[0], coord[1]
        neighbours = []
        increments = [-1,0,1]
        for x_increment in increments:
            for y_increment in increments:
                if (x_increment,y_increment) == (0,0):
                    continue
                neighbour = (cell_x + x_increment,cell_y + y_increment)
                if neighbour not in neighbours and neighbour in self.live_cells:
                    neighbours.append(neighbour)
        return neighbours
    
    def updateCells(self):
        extension = 5
        updated_live_cells = [cell for cell in self.live_cells]
        for y in range(0-extension,self.y+extension):
            for x in range(0-extension,self.x+extension):
                coord = (x,y)
                live_neighbours = self.getLiveNeighbours(coord)
                live_count = len(live_neighbours)

                if coord in self.live_cells:
                    if 2 <= live_count <= 3:
                        pass
                    else:
                        updated_live_cells.remove(coord)
                
                else:
                    if live_count == 3:
                        updated_live_cells.append(coord)
        
        self.live_cells = updated_live_cells
    
    

                
class Button:
    def __init__(self,window,x,y,image1,image2):
        self.window = window
        self.x = x
        self.y = y
        self.image = image1
        self.image1 = image1
        self.image2 = image2
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def checkHovering(self,mouse_pos):
        if not self.x < mouse_pos[0] < self.x + self.width:
            return False
        
        if not self.y < mouse_pos[1] < self.y + self.height:
            return False
        
        return True
    
    def updateImage(self):
        if self.image == self.image1:
            self.image = self.image2
        else:
            self.image = self.image1
    
    def checkClicked(self,mouse_pos,mouse_pressed):
        if not mouse_pressed[0]:
            return False
        
        if not self.checkHovering(mouse_pos):
            return False
        
        self.updateImage()
        return True
    
    def draw(self):
        self.window.blit(self.image,(self.x,self.y))
        


class Game:
    def __init__(self,win_x,win_y,square_size):
        no_columns = win_x // square_size
        no_rows = win_y // square_size
        self.win_x = no_columns * square_size
        self.header = (50 // square_size) * square_size
        self.win_y = (no_rows * square_size) + self.header
        self.square_size = square_size
        self.window = pygame.display.set_mode((self.win_x,self.win_y))

        self.board = Board(no_columns, no_rows)
        self.square_colour = Colours.YELLOW

        self.live_count = 0
        self.dead_count = 0
        pause_img = pygame.image.load("pause.png")
        unpause_img = pygame.image.load("unpause.png")
        self.pause_btn = Button(self.window,0,0,pause_img,unpause_img)
        self.paused = True

        speedup_img = pygame.image.load("speedup.png")
        slowdown_img = pygame.image.load("slowdown.png")
        self.speedup_btn = Button(self.window,0.65 * self.win_x,0,speedup_img,speedup_img)
        self.slowdown_btn = Button(self.window, self.speedup_btn.x + self.speedup_btn.width,0,slowdown_img,slowdown_img)

        loadfile_img = pygame.image.load("loadfile.png")
        savefile_img = pygame.image.load("savefile.png")
        self.loadfile_btn = Button(self.window,self.slowdown_btn.x + self.slowdown_btn.width, 0, loadfile_img,loadfile_img)
        self.savefile_btn = Button(self.window,self.loadfile_btn.x + self.loadfile_btn.width + 5, 0, savefile_img,savefile_img)
        self.fps_mult = 1
    
    def drawGrid(self):
        pygame.draw.rect(self.window,Colours.BLUE,(0,0,self.win_x,self.header))
        y_pos = self.header
        x_pos = 0
        for y in range(0,self.board.y):
            x_pos = 0
            for x in range(0,self.board.x):
                pygame.draw.rect(self.window,Colours.GREEN,(x_pos,y_pos,self.square_size,self.square_size))
                pygame.draw.rect(self.window,Colours.BLACK,(x_pos,y_pos,self.square_size-1,self.square_size-1))
                x_pos += self.square_size
            y_pos += self.square_size

    
    def drawLiveCells(self):
        self.live_count = 0
        for live_cell in self.board.live_cells:
            cell_x = live_cell[0] * self.square_size
            cell_y = live_cell[1] * self.square_size + self.header

            if not 0 <= cell_x <= self.win_x:
                continue

            if not self.header <= cell_y <= self.win_y:
                continue
            pygame.draw.rect(self.window,self.square_colour,(cell_x, cell_y, self.square_size-1, self.square_size-1))
            self.live_count += 1
        self.dead_count = (self.board.x * self.board.y) - self.live_count

    def placeLiveCell(self,mouse_pos,mouse_pressed):
        if mouse_pos[1] < self.header:
            return

        if not self.paused:
            print("pause to place cells")
            return
        
        coordx = mouse_pos[0] // self.square_size
        coordy = (mouse_pos[1] // self.square_size) - (self.header // self.square_size)
        new_cell = (coordx,coordy)

        if mouse_pressed[0]:
            if new_cell in self.board.live_cells:
                return
            self.board.live_cells.append(new_cell)
        
        if mouse_pressed[2]:
            if new_cell not in self.board.live_cells:
                return
            self.board.live_cells.remove(new_cell)
        
        print("Target: " + str(new_cell))

    def displayCellCount(self):
        live_str = "Live Cells: {}".format(self.live_count)
        dead_str = "Dead Cells: {}".format(self.dead_count)
        self.displayText(live_str,18,True,Colours.GREEN,(0.5 * self.win_x, 0.02 * self.win_y))
        self.displayText(dead_str,18,True,Colours.RED,(0.5 * self.win_x, 0.05 * self.win_y))
    
    def displayText(self,text,text_size,bold,text_colour,text_centre):
        font = pygame.font.SysFont("Consolas",text_size,bold)
        text_surf = font.render(text,False,text_colour)
        text_rect = text_surf.get_rect()
        text_rect.center = (text_centre)
        self.window.blit(text_surf,text_rect)
    
    def selectFile(self):
        top = tkinter.Tk()
        top.withdraw()  # hide window
        file_name = tkinter.filedialog.askopenfilename(parent=top)
        top.destroy()
        return file_name
        
    def loadFile(self,filename):
        if ".txt" not in filename:
            filename += ".txt"
        with open(filename,mode="r") as read_file:
            lines = read_file.readlines()
            read_file.close()
        
        for line in lines:
            line = line.split(",")
            x_comp = int(line[0].strip()[1:])
            y_comp = int(line[1].strip()[0:-1])
            coord = (x_comp,y_comp)
            self.board.live_cells.append(coord)
    
    def getFileName(self):
        self.top = tkinter.Tk()
        self.filename_entry = tkinter.Entry(self.top)
        self.filename_entry.pack()
        self.filename_entry.focus_set()
        button = tkinter.Button(self.top,text="enter",command=self.saveFile)
        button.pack()
        self.top.mainloop()
    
    def saveFile(self):
        entered_filename = self.filename_entry.get() + ".txt"
        self.top.destroy()
        with open(entered_filename,mode="w",encoding="utf-8") as write_file:
            for coord in self.board.live_cells:
                write_file.write(str(coord) + "\n")
            write_file.close()

    
    def startSim(self):
        clock = pygame.time.Clock()
        quit_sim = False
        while not quit_sim:
            pause_btn_clicked = False
            speedup_btn_clicked = slowdown_btn_clicked = False
            loadfile_btn_clicked = savefile_btn_clicked = False
            clock.tick(FPS * self.fps_mult)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_sim = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        self.pause_btn.updateImage()
                        print("Paused: " + str(self.paused))
                    
                    if event.key == pygame.K_c:
                        self.board.live_cells = []
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_pressed = pygame.mouse.get_pressed()
                    self.placeLiveCell(mouse_pos,mouse_pressed)
                    pause_btn_clicked = self.pause_btn.checkClicked(mouse_pos,mouse_pressed)
                    speedup_btn_clicked = self.speedup_btn.checkClicked(mouse_pos,mouse_pressed)
                    slowdown_btn_clicked = self.slowdown_btn.checkClicked(mouse_pos,mouse_pressed)
                    loadfile_btn_clicked = self.loadfile_btn.checkClicked(mouse_pos,mouse_pressed)
                    savefile_btn_clicked = self.savefile_btn.checkClicked(mouse_pos,mouse_pressed)
            

            self.drawGrid()
            self.pause_btn.draw()
            self.speedup_btn.draw()
            self.slowdown_btn.draw()
            self.loadfile_btn.draw()
            self.savefile_btn.draw()
            self.drawLiveCells()
            self.displayCellCount()

            if pause_btn_clicked:
                self.paused = not self.paused
                print("Paused: " + str(self.paused)) 

            if not self.paused:
                self.board.updateCells()
            
            if speedup_btn_clicked:
                self.fps_mult *= 1.15
                print("Increasing speed...")

            if slowdown_btn_clicked:
                self.fps_mult *= 0.85
                print("Decreasing speed...")
            
            if loadfile_btn_clicked:
                self.paused = True
                selected_filename = self.selectFile()
                try:
                    self.loadFile(selected_filename)
                except:
                    print("Error - File Not Loaded")
            
            if savefile_btn_clicked:
                self.getFileName()
                print("Current state saved.")
            
            pygame.display.update()
            self.window.fill(Colours.BLACK)
        
        pygame.quit()
        print("program ended")

WIN_X = 800
WIN_Y = 500
SQUARE_SIZE = 10
FPS = 20

if __name__ == "__main__":
    commandline_args = sys.argv
    g = Game(WIN_X,WIN_Y,SQUARE_SIZE)
    if len(commandline_args) == 1:
        g.startSim()
    else:
        filename = commandline_args[1]
        g.loadFile(filename)
        g.startSim()

