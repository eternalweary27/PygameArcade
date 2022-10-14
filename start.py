import os
import threading
from tkinter import *


WIN_X = 1000
WIN_Y = 600

ICONS_DIR = "./GameIcons"
GAME_NAMES = ["Pong","Shooter","Dino","Snake","Life","Typing"]
ROW_SIZE = 3

def runCommand(directory):
    command_str = "cd {} & python main.py".format(directory)
    os.system(command_str)

def onButtonClick(directory):
    new_thread = threading.Thread(target = runCommand,args=(directory,))
    new_thread.start()


def main():
    win = Tk()
    win.title("Pygame Arcade")
    win.geometry("{}x{}".format(WIN_X,WIN_Y))
    win.config(background = "#092147")

    title_img = PhotoImage(file = "./GameIcons/Title.png")
    title_lable = Label(win,image=title_img,borderwidth=0)
    title_lable.pack(side = TOP)

    starting_x = curr_x = 0.35 * WIN_X
    starting_y = curr_y = 0.25 * WIN_Y

    game_images =[]
    button_funcs = []
    for game_name in GAME_NAMES:
        image_path = "{}/{}.png".format(ICONS_DIR,game_name)
        button_arg = "./{}".format(game_name)
        game_images.append(PhotoImage(file = image_path))
        button_funcs.append(lambda button_arg = button_arg: onButtonClick(button_arg))


    for index,game_name in enumerate(GAME_NAMES):
        game_image = game_images[index]
        button_func = button_funcs[index]
        game_button = Button(win,image=game_image,command = button_func).place(x = curr_x, y = curr_y)
        curr_x += game_image.width()
        if index == ROW_SIZE-1:
            curr_x = starting_x
            curr_y += game_image.height()



    mainloop()




if __name__ == "__main__":
    main()