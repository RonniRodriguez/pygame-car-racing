import pygame 
import time 
import math 
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init() 

#importing image assets 
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5) 
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9) 

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER) 
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)
#display width and height = track image width and height
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

class GameInfo: 
    LEVELS = 3 
    def __init__(self, level =1): 
        self.level=level 
        self.started=False 
        self.level_start_time = 0 
    
    def next_level(self):
        self.level +=1 
        self.started=False 
    def reset(self): 
        self.level = 1 
        self.started = False 
        self.level_start_time=0 
    def game_finished(self): 
        return self.level > self.LEVELS 
    def start_level(self): 
        self.started = True 
        self.level_start_time - time.time() 
    def get_level_time(self): 
        if not self.started: 
            return 0 
        return round(time.time()-self.level_start_time) 
    
class AbstractCar: 
    IMG = RED_CAR 
    def __init__(self, max_vel, rotation_vel): 
        self.max_vel = max_vel 
        self.img = self.IMG
        self.vel = 0 
        self.rotation_vel = rotation_vel 
        self.angle = 0 
        self.x, self.y = self.START_POS
        self.acceleration = 0.2 

    def rotate(self, left=False, right = False): 
        if left: 
            self.angle += self.rotation_vel 
        elif right: 
            self.angle -= self.rotation_vel 
    def draw(self, win): 
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
    def move_forward(self): 
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()
    def move_backward(self): 
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move() 
    def move(self): 
        radians = math.radians(self.angle) 
        vertical = math.cos(radians)*self.vel 
        horizontal = math.sin(radians) * self.vel 
        self.y -= vertical 
        self.x -= horizontal
    def reduce_speed(self): 
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()  
    def collide(self, mask, x=0, y=0): 
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x-x), int(self.y-y))
        #point of intersection
        poi = mask.overlap(car_mask, offset) 
        return poi 
    def reset(self): 
        self.x, self.y = self.START_POS
        self.angle = 0 
        self.vel = 0 




class PlayerCar(AbstractCar): 
    IMG = RED_CAR
    START_POS = (180, 200)
    def bounce(self): 
        self.vel = -self.vel 
        self.move()

def draw(win, images, player_car, computer_car): 
    for img, pos in images: 
        win.blit(img, pos)
    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height()-70))

    time_text = MAIN_FONT.render(f"Time:  {game_info.get_level_time()}", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height()-40))

    vel_text = MAIN_FONT.render(f"Vel: {player_car.vel}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height()-10))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

class ComputerCar(AbstractCar): 
    IMG  = GREEN_CAR 
    START_POS = (150, 200) 
    def __init__(self, max_vel, rotation_vel, path=[]): 
        super().__init__(max_vel, rotation_vel)
        self.path = path 
        self.current_point = 0 
        self.vel = max_vel 
    def draw_points(self, win): 
        for point in self.path: 
            pygame.draw.circle(win, (255, 0, 0), point, 5)
    def draw(self, win): 
        super().draw(win)
        #only needed when creating new path
        #self.draw_points(win) 
    def calculate_angle(self): 
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x 
        y_diff = target_y - self.y 
        if y_diff == 0: 
            desired_radian_angle = math.pi/2 
        else: 
            desired_radian_angle = math.atan(x_diff/y_diff)
        
        if target_y > self.y: 
            desired_radian_angle += math.pi 
        difference_in_angle = self.angle - math.degrees(desired_radian_angle) 
        if difference_in_angle >= 180: 
            difference_in_angle -= 360 
        if difference_in_angle > 0: 
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else: 
            self.angle += min(self.rotation_vel, abs(difference_in_angle))
        
    def update_path_point(self): 
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target): 
            self.current_point += 1

    def move(self): 
        if self.current_point >= len(self.path): 
            return 
        self.calculate_angle() 
        self.update_path_point() 
        super().move() 
    def next_level(self, level): 
        self.reset() 
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0


def handle_collision(player_car, computer_car, game_info):
    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None: 
        print("Computer Wins")
        blit_text_center(WIN , MAIN_FONT, "You Lost")
        pygame.time.wait(5000)
        game_info.reset() 
        player_car.reset() 
        computer_car.reset()
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if  player_finish_poi_collide != None: 
        if player_finish_poi_collide[1]==0: 
            player_car.bounce()
        else: 
            print("player wins!")
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)       

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
PATH = [(168, 109), (99, 60), (51, 170), (75, 503), (292, 720), (412, 676), (423, 508), (509, 472), (591, 548), (600, 722), (741, 712), (732, 389), (615, 362), (405, 361), (443, 243), (704, 266), (741, 117), (560, 67), (289, 77), (291, 381), (159, 393), (175, 261)]
run = True 
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2, 2, PATH)
game_info = GameInfo()
#run game
while run: 
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car)
    
    while not game_info.started: 
        blit_text_center(WIN ,MAIN_FONT, f"Press any key to start level {game_info.level}")
        pygame.display.update() 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                pygame.quit() 
                break 
            if event.type == pygame.KEYDOWN: 
                game_info.start_level() 
     

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            run = False 
            break 
        
    keys = pygame.key.get_pressed() 
    moved = False
    if keys[pygame.K_a]: 
        player_car.rotate(left=True)
    if keys[pygame.K_d]: 
        player_car.rotate(right=True)
    if keys[pygame.K_w]: 
        moved = True
        player_car.move_forward() 
    if keys[pygame.K_s]:
        moved = True 
        player_car.move_backward()  
    if not moved: 
        player_car.reduce_speed() 

    computer_car.move() 

    if player_car.collide(TRACK_BORDER_MASK) != None: 
        print("COLLIDE")
        player_car.bounce()
    
    handle_collision(player_car, computer_car, game_info)

    if game_info.game_finished(): 
        blit_text_center(WIN , MAIN_FONT, "You Won The Game!")
        pygame.time.wait(5000)
        game_info.reset() 
        player_car.reset() 
        computer_car.reset()

print(computer_car.path)
pygame.quit()