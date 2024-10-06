import pygame 
import time 
import math 
def scale_image(image, factor): 
    size = round(image.get_width() * factor), round (image.get_height() * factor)
    return pygame.transform.scale(image, size)

def blit_rotate_center(win, image, top_left, angle): 
    rotated_image = pygame.transform.rotate(image, angle) 
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft = top_left).center)
    win.blit(rotated_image, new_rect.topleft) 

def blit_text_center(win, font, text): 
    render = font.render(text, 1, (200, 200, 200)) 
    win.blit(render, (win.get_width() / 2 - render.get_width()/2, win.get_height()/2 - render.get_height()/2))

#for creating paths for the computer car to follow 
#def create_path(): 
    #if event.type == pygame.MOUSEBUTTONDOWN: 
            #pos = pygame.mouse.get_pos() 
            #computer_car.path.append(pos) 
    # when exiting gamne, print(computer_car.path)