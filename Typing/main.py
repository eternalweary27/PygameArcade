import time
import datetime
import random
import os
import pygame
pygame.init()
pygame.mixer.init()

class Colours:
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    GREY = (80,80,80)
    LIGHT_GREY = (120,120,120)
    RED = (200,0,0)
    GREEN = (0,200,0)
    BLUE = (0,0,200)
    YELLOW = (200,200,0)
    PINK = (255,20,147)



class Word:
    def __init__(self,window,x,y,dx,string,colour):
        self.window = window
        self.x = x
        self.y = y
        self.dx = dx
        self.string = string
        self.colour = colour

        self.font = pygame.font.SysFont("Consolas",20,True)
        self.font_surf = self.font.render(self.string,False,self.colour)
        self.width = self.font_surf.get_width()
        self.height = self.font_surf.get_height()
    
    def updatePos(self):
        self.x += self.dx
    
    def draw(self):
        self.font_surf = self.font.render(self.string,False,self.colour)
        font_rect = self.font_surf.get_rect()
        font_rect.center = (self.x,self.y)
        self.window.blit(self.font_surf,font_rect)
        self.updatePos()


class Game:
    def __init__(self,win_x,win_y):
        self.win_x = win_x
        self.win_y = win_y
        self.window = pygame.display.set_mode((self.win_x,self.win_y))
        self.background_stars = self.createBackGround()

        self.panel_x = 0
        self.panel_y = PANEL_Y * self.win_y
        self.panel_w = self.win_x
        self.panel_h = self.win_y - self.panel_y

        self.txt_x = self.panel_x + 5
        self.txt_y = self.panel_y + 5
        self.txt_w = self.panel_w * 0.3
        self.txt_h = self.panel_h * 0.3

        self.string_buffer = ""
        self.score = 0
        self.max_lives = MAX_LIVES
        self.lives = self.max_lives

        self.last_press = 0

        self.filename = FILENAME
        self.word_len = WORD_LEN
        self.all_words = self.getAllWords()
        self.last_spawn = None
        self.no_obstacles = NO_OBSTACLES
        self.word_obstacles = []

        self.correct_sound = pygame.mixer.Sound("correct_word.mp3")
        self.incorrect_sound = pygame.mixer.Sound("incorrect_word.mp3")
        self.setRandomTune()

        self.highscorescreen = False

        self.fps = FPS
    
    def createBackGround(self):
        background_stars = []
        for i in range(20):
            new_star = {"x": random.randint(0,self.win_x), "y": random.randint(0,PANEL_Y * self.win_y), "radius": random.uniform(0.5,3)}
            background_stars.append(new_star)
        return background_stars
    
    def updateBackGround(self):
        star_dx = 2.5
        for star in self.background_stars:
            if star["x"] > int(star["radius"]) + self.win_x:
                star["x"] = -int(star["radius"])
                continue
            star["x"] += star_dx
    
    def drawBackGround(self):
        for star in self.background_stars:
            pygame.draw.circle(self.window,Colours.WHITE,(int(star["x"]),int(star["y"])),int(star["radius"]))
        self.updateBackGround()
    
    def setRandomTune(self):
        rand_filename = "background_sounds/" + random.choice(os.listdir("background_sounds"))
        self.background_sound = pygame.mixer.music.load(rand_filename)
        print("MUSIC: " + str(rand_filename))
        pygame.mixer.music.play(-1,0.0)
        pygame.mixer.music.set_volume(0.25)
    
    def reset(self):
        self.string_buffer = ""
        self.score = 0
        self.lives = self.max_lives
        self.last_press = 0
        self.last_spawn = None
        self.word_obstacles = []
        self.background_stars = self.createBackGround()
        self.setRandomTune()
    
    def getAllWords(self):
        words_arr = []
        with open(self.filename,mode="r") as read_file:
            lines = read_file.readlines()
            for line in lines:
                for word in line.split(" "):
                    if len(word) <= self.word_len:
                        words_arr.append(word.rstrip())
            read_file.close()
        return words_arr
    
    def spawnObstacles(self):

        if self.last_spawn == None or time.perf_counter() - self.last_spawn > 5:
            self.last_spawn = time.perf_counter()

            min_x, max_x = self.win_x, self.win_x * 2
            min_y, max_y = 20, self.panel_y - 20

            for i in range(self.no_obstacles):

                valid_coords = False
                while not valid_coords:
                    x = random.uniform(min_x,max_x)
                    y = random.uniform(min_y,max_y)
                    valid_coords = True
                    for word in self.word_obstacles:
                        if word.x - 0.5 * word.width < x < word.x + 0.5 * word.width:
                            if word.y - 0.5 * word.height < y < word.y + 0.5 * word.height:
                                valid_coords = False
                                break

                dx = WORD_SPEED
                string = random.choice(self.all_words)
                colour = (0,200,0)
                new_word = Word(self.window,x,y,dx,string,colour)
                self.word_obstacles.append(new_word)

    def detectKeyBoard(self,events,keys_pressed):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.string_buffer = self.string_buffer[0:-1]
                
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.string_buffer = ""
                else:
                    self.string_buffer += event.unicode
        
        if time.perf_counter() - self.last_press > 0.1:
            self.last_press = time.perf_counter()
            if keys_pressed[pygame.K_BACKSPACE]:
                self.string_buffer = self.string_buffer[0:-1]
    
    
    def displayPanel(self):
        pygame.draw.rect(self.window,Colours.BLUE,(self.panel_x,self.panel_y,self.panel_w,self.panel_h))
        pygame.draw.rect(self.window,Colours.GREY,(self.txt_x,self.txt_y,self.txt_w,self.txt_h))


        font = pygame.font.SysFont("Consolas",20,True)

        write_str = "Type Here..." if len(self.string_buffer) == 0 else self.string_buffer
        write_surf = font.render(write_str,False,Colours.LIGHT_GREY)
        write_rect = write_surf.get_rect()
        write_x = self.txt_x + (0.5 * write_surf.get_width())
        write_y = self.txt_y + (0.5 * write_surf.get_height())
        write_rect.center = (write_x,write_y)
        self.window.blit(write_surf,write_rect)

        score_str = "Score: {}".format(self.score)
        score_surf = font.render(score_str,False,Colours.RED)
        score_rect = score_surf.get_rect()
        score_x = self.txt_x + (0.5 * score_surf.get_width())
        score_y = self.txt_y + self.txt_h + (0.5 * score_surf.get_height()) + 5
        score_rect.center = (score_x,score_y)
        self.window.blit(score_surf,score_rect)

        lives_str = "Lives: {}".format(self.lives)
        lives_surf = font.render(lives_str,False,Colours.GREEN)
        lives_rect = lives_surf.get_rect()
        lives_x = self.txt_x + (0.5 * lives_surf.get_width())
        lives_y = score_y + score_surf.get_height() + (0.5 * lives_surf.get_height()) + 5
        lives_rect.center = (lives_x,lives_y)
        self.window.blit(lives_surf,lives_rect)
    
    def checkWordInput(self):
        self.string_buffer.rstrip()
        invalid_word = True
        for word in self.word_obstacles:
            if self.string_buffer == word.string:
                self.score += len(word.string)
                self.word_obstacles.remove(word)
                invalid_word = False
                break
        if not invalid_word:
            pygame.mixer.Sound.play(self.correct_sound)
            self.string_buffer = ""
    

    def displayGameOver(self):
        pygame.mixer.music.stop()
        font = pygame.font.SysFont("Consolas",50,True)
        gameover_str = "Game Over! Score: {}".format(self.score)
        gameover_surf = font.render(gameover_str,False,Colours.RED)
        gameover_rect = gameover_surf.get_rect()
        gameover_rect.center = (self.win_x / 2, self.win_y / 2)
        self.window.blit(gameover_surf,gameover_rect)
        pygame.display.update()
        pygame.time.delay(1500)

    def saveScore(self):
        with open("scores.txt",mode="a") as write_file:
            score_str = "Date: {}, Score: {}".format(datetime.datetime.today().strftime('%Y-%m-%d'),self.score)
            write_file.write(score_str + "\n")
            write_file.close()
        print("score saved.")
    
    def getHighScores(self,limit):
        score_records = []
        with open("scores.txt", mode = "r") as read_file:
            lines = [line.split(",") for line in read_file.readlines()]
            for line in lines:
                date_value = line[0].split(":")[1]
                score_value = line[1].split(":")[1].rstrip()
                record = {"Date": date_value, "Score": score_value}
                score_records.append(record)
            read_file.close()
        
        score_records = sorted(score_records, key = lambda record: int(record["Score"]), reverse = True)[0:limit]
        for index, record in enumerate(score_records):
            ranked_record = {**{"Rank":index+1},**record}
            score_records[index] = ranked_record
        return score_records
    
    def displayScores(self):
        self.window.fill(Colours.BLACK)
        top_scores = self.getHighScores(10)
        self.window.fill(Colours.BLACK)

        starting_x = self.win_x * 0.5
        starting_y = self.win_y * 0.15

        highlighted = False
        for score_record in top_scores:
            if int(score_record["Score"]) == self.score and not highlighted:
                score_colour = Colours.PINK
                highlighted = True
            else:
                score_colour = Colours.GREEN
            font = pygame.font.SysFont("Consolas",25,True)
            score_str = "Rank: {} | Date: {} | Score: {}".format(score_record["Rank"],score_record["Date"],score_record["Score"])
            font_surf = font.render(score_str,False,score_colour)
            font_rect = font_surf.get_rect()
            font_rect.center = (starting_x,starting_y)
            self.window.blit(font_surf,font_rect)
            starting_y += font_surf.get_height() 
        pygame.display.update()

    def startGame(self):
        clock = pygame.time.Clock()
        quit_game = False
        while not quit_game:
            clock.tick(self.fps)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    quit_game = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.reset()
                        self.highscorescreen = False
            
            self.drawBackGround()
            
            if self.highscorescreen:
                self.displayScores()
                continue;
            
            
            keys_pressed = pygame.key.get_pressed()
            self.detectKeyBoard(events,keys_pressed)

            self.spawnObstacles()
            for word in self.word_obstacles:
                if word.x < -word.width:
                    self.word_obstacles.remove(word)
                    self.lives -= 1
                    continue

                if word.x < self.win_x / 2:
                    word.colour = Colours.YELLOW
                
                if word.x < self.win_x / 4:
                    word.colour = Colours.RED 
                
                word.draw()
        
            self.checkWordInput()
            self.displayPanel()

            if self.lives <= 0:
                pygame.mixer.Sound.play(self.incorrect_sound)
                self.displayGameOver()
                self.saveScore()

                top_scores = self.getHighScores(10)
                if self.score > int(top_scores[-1]["Score"]):
                    self.highscorescreen = True
                else:
                    self.reset()
        
            pygame.display.update()
            self.window.fill(Colours.BLACK)
        
        
        print("program exited.")
        pygame.quit()


WIN_X = 1000
WIN_Y = 700
FPS = 60

PANEL_Y = 0.85

MAX_LIVES = 3

NO_OBSTACLES = 10
FILENAME = "simple_english.txt"
WORD_LEN = 8
WORD_SPEED = -1.5

g = Game(WIN_X,WIN_Y)
g.startGame()
