import math
import pygame
pygame.init()

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (200,200,200)
RED = (200,0,0)
BLUE = (0,0,200)
GREEN = (0,200,0)

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
        hovering = True
        if not self.x < mouse_pos[0] < self.x + self.width:
            hovering = False
        
        if not self.y < mouse_pos[1] < self.y + self.height:
            hovering = False
        
        self.updateImage(hovering)
        return hovering
    
    def updateImage(self,hovering):
        if hovering:
            self.image = self.image2
        else:
            self.image = self.image1
    
    def checkClicked(self,mouse_pos,mouse_pressed):
        if not self.checkHovering(mouse_pos):
            return False

        if not mouse_pressed[0]:
            return False
        return True
    
    def draw(self):
        self.window.blit(self.image,(self.x,self.y))

class Paddle:
    def __init__(self,window,x,y,width,height,dy,colour):
        self.window = window
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.dy = dy
        self.colour = colour
        self.points = 0
    
    
    def displayPaddle(self):
        win_y = self.window.get_height()
        if self.y + self.height > win_y:
            self.y = win_y - self.height
        
        if self.y < 0:
            self.y = 0

        pygame.draw.rect(self.window,self.colour,(self.x,self.y,self.width,self.height))
    

class Ball:
    def __init__(self,window,x,y,radius,dx,dy,colour):
        self.window = window
        self.x = x
        self.y = y
        self.radius = radius
        self.dx = dx
        self.dy = dy
        self.max_vel = BALL_MAX_VEL #max dy vel
        self.colour = colour

        self.player1_point = False
        self.player2_point = False
        self.hit_sound = pygame.mixer.Sound("hit_sound.wav")
    
    def updatePos(self):
        self.x = self.x + self.dx
        self.y = self.y + self.dy
    
    def adjustVelocity(self,paddle):
        self.dx *= -1
        middle_y = paddle.y + paddle.height / 2
        difference_y = middle_y - self.y
        percent_reduction = abs(difference_y) / (middle_y - paddle.y)
        new_vel = self.max_vel * percent_reduction
        if difference_y > 0:
            new_vel *= -1
        self.dy = new_vel
    

    def checkPaddleCollision(self, paddle):
        if self.dx < 0 and paddle.x > self.window.get_width() / 2:
            return
        
        if self.dx > 0 and paddle.x < self.window.get_width() / 2:
            return

        nx = max(min(paddle.x + paddle.width,self.x),paddle.x)
        ny = max(min(paddle.y + paddle.height,self.y),paddle.y)
        mag = math.sqrt(math.pow(nx - self.x, 2) + math.pow(ny - self.y, 2))
        if mag < self.radius:
            pygame.mixer.Sound.play(self.hit_sound)
            self.adjustVelocity(paddle)


    def displayBall(self):
        win_x = self.window.get_width()
        win_y = self.window.get_height()

        if self.x - self.radius > win_x:
            self.player1_point = True
        
        if self.x + self.radius < 0:
            self.player2_point = True
        
        if self.y + self.radius > win_y:
            self.y = win_y - self.radius
            self.dy *= -1
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.dy *= -1

        pygame.draw.circle(self.window,GREY,(self.x,self.y),self.radius)
        pygame.draw.circle(self.window,self.colour,(self.x,self.y),self.radius-2)
        
        self.updatePos()

class Game:
    def __init__(self,win_x,win_y,end_game):
        self.win_x = win_x
        self.win_y = win_y
        self.end_game = end_game
        self.curr_turn = 1
        self.window = pygame.display.set_mode((self.win_x,self.win_y))

        paddle_offset = 0.05
        paddle_centre1 = (paddle_offset * self.win_x - PADDLE_W, 0.25 * self.win_y)
        paddle_centre2 = ((1-paddle_offset) * self.win_x, 0.25 * self.win_y)
        ball_centre = (win_x // 2, win_y // 2)
        self.paddle1 = Paddle(self.window,paddle_centre1[0],paddle_centre1[1],PADDLE_W, PADDLE_H, PADDLE_DY, PADDLE_COLOUR)
        self.paddle2 = Paddle(self.window,paddle_centre2[0],paddle_centre2[1],PADDLE_W, PADDLE_H, PADDLE_DY, PADDLE_COLOUR)
        self.ball = Ball(self.window,ball_centre[0],ball_centre[1],BALL_R, BALL_DX, BALL_DY, BALL_COLOUR)
        self.win_sound = pygame.mixer.Sound("win_sound.wav")
        self.use_mouse = True
        self.AI_mode = False
    
    def drawDivider(self):
        centre_r = 100
        pygame.draw.circle(self.window,WHITE, (self.win_x // 2, self.win_y // 2), centre_r)
        pygame.draw.circle(self.window,BLACK, (self.win_x // 2, self.win_y // 2), centre_r-5)

        dividor_w = 7.5
        dividor_h = 18.75

        starting_x = (self.win_x // 2) - (0.5 * dividor_w)
        starting_y = 0
        increment = int(dividor_h)

        skip = False
        for i in range(starting_y, self.win_y, increment):
            if skip:
                skip = False
                continue
            pygame.draw.rect(self.window, self.paddle1.colour, (starting_x,i, dividor_w,dividor_h))
            skip = True
        
    
    def displayScores(self):
        score1_str = str(self.paddle1.points)
        score2_str = str(self.paddle2.points)
        font = pygame.font.SysFont('courier',50,True)
        score1_text = font.render(score1_str, False, WHITE)
        score2_text = font.render(score2_str, False, WHITE)
        text_rect1 = score1_text.get_rect()
        text_rect2 = score2_text.get_rect()
        text_rect1.center = (self.win_x * 0.25, self.win_y * 0.1)
        text_rect2.center = (self.win_x * 0.75, self.win_y * 0.1)
        self.window.blit(score1_text,text_rect1)
        self.window.blit(score2_text,text_rect2)
    
    def resetBall(self):
        self.ball.x = self.win_x // 2
        self.ball.y = self.win_y // 2
        self.ball.dy = BALL_DY
        pygame.time.delay(100)
    
    def resetGame(self):
        self.resetBall()
        self.paddle1.points = 0
        self.paddle2.points = 0
    
    def AIControl(self,paddle):
        bally = self.ball.y
        centrey = paddle.y + (0.5 * paddle.height)
        diffy = bally - centrey 
        mult = AI_DIFFICULTY
        paddle.y += max(min(diffy,paddle.dy*mult),-paddle.dy*mult)
    
    def displayMainMenu(self):
        self.playai_btn.draw()
        self.playhuman_btn.draw()

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.playai_btn.checkClicked(mouse_pos, mouse_pressed):
            self.AI_mode = True
            self.main_menu = False

        if self.playhuman_btn.checkClicked(mouse_pos, mouse_pressed):
            self.AI_mode = False
            self.main_menu = False
        
        pygame.display.update()
        self.window.fill(BLACK)

    
    def startGame(self):
        play_ai_img1 = pygame.image.load("playai_btn1.png")
        play_ai_img2 = pygame.image.load("playai_btn2.png")
        self.playai_btn = Button(self.window,0.5 * self.win_x - (play_ai_img1.get_width()/2), 0.1  * self.win_y, play_ai_img1,play_ai_img2)

        play_human_img1 = pygame.image.load("playhuman_btn1.png")
        play_human_img2 = pygame.image.load("playhuman_btn2.png")
        self.playhuman_btn = Button(self.window,0.5 * self.win_x - (play_ai_img1.get_width()/2), self.playai_btn.y + self.playai_btn.width + 10, play_human_img1, play_human_img2)


        self.main_menu = True
        start_game = False
        quit_game = False
        self.ball.dx = 0
        while not quit_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game = True

                if self.main_menu:
                    continue 

                if event.type == pygame.MOUSEBUTTONDOWN and not self.AI_mode:
                    self.use_mouse = not self.use_mouse
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not start_game:
                        start_game = True
                        self.ball.dx = BALL_DX
            
            if self.main_menu:
                self.displayMainMenu()
                continue
            
            if self.AI_mode:
                ai_player = 1
                if ai_player == 1:
                    self.AIControl(self.paddle1)
                else:
                    self.use_mouse = False
                    self.AIControl(self.paddle2)
            
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_w]:
                self.paddle1.y -= self.paddle1.dy
            
            if keys_pressed[pygame.K_s]:
                self.paddle1.y += self.paddle1.dy
            
            if keys_pressed[pygame.K_UP]:
                self.paddle2.y -= self.paddle2.dy
            
            if keys_pressed[pygame.K_DOWN]:
                self.paddle2.y += self.paddle2.dy
            
            if self.use_mouse:
                mouse_pos = pygame.mouse.get_pos()
                self.paddle2.y = mouse_pos[1]
            
            
            self.drawDivider()
            self.displayScores()
                
            self.paddle1.displayPaddle()
            self.paddle2.displayPaddle()
            self.ball.displayBall()

            self.ball.checkPaddleCollision(self.paddle1)
            self.ball.checkPaddleCollision(self.paddle2)

            if self.ball.player1_point:
                self.paddle1.points += 1
                self.ball.player1_point = False
                self.resetBall()
            
            if self.ball.player2_point:
                self.paddle2.points += 1
                self.ball.player2_point = False
                self.resetBall()

            if self.paddle1.points == self.end_game or self.paddle2.points == self.end_game:
                pygame.mixer.Sound.play(self.win_sound)
                winner = "Player 1" if self.paddle1.points == self.end_game else "Player 2"
                gameover_font = pygame.font.SysFont("courier",30,True)
                gameover_msg = f"{winner} wins!"
                gameover_text = gameover_font.render(gameover_msg,False,WHITE)
                gameover_rect = gameover_text.get_rect()
                gameover_rect.center = (self.win_x / 2, self.win_y / 2)
                self.window.fill(BLACK)
                self.window.blit(gameover_text,gameover_rect)
                pygame.display.update()
                pygame.time.delay(1000)
                self.resetGame()

            pygame.display.update()
            self.window.fill(BLACK)

AI_DIFFICULTY= 1.4
PADDLE_W = 20
PADDLE_H = 160
PADDLE_DY = 0.4
PADDLE_COLOUR = WHITE

BALL_R = 12 
BALL_MAX_VEL = 0.85
BALL_DX = BALL_MAX_VEL
BALL_DY = 0
BALL_COLOUR = WHITE

WIN_X = 1000
WIN_Y = 600
END_GAME = 5

WIN_X = 1000
WIN_Y = 600
END_GAME = 5


def main():
    game = Game(WIN_X,WIN_Y,END_GAME)
    game.startGame()

if __name__ == "__main__":
    main()
