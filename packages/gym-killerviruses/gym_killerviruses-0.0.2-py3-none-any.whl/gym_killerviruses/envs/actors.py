from pygame.image import load 
import random
import pygame 
import numpy as np
import os

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 520-100
image_path = 'image/'

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SPEED_PLAYER = 2.5



class SarsCovII(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

		IMAGE_JPG = os.path.join(DIR_PATH, image_path+'corvina.jpg')

		self.image = load(IMAGE_JPG).convert_alpha()
		self.rect = self.image.get_rect()
		self.velocity = [0, -0.5]

	def update(self, dt):

		self.rect.centerx += self.velocity[0]*dt
		self.rect.centery += self.velocity[1]*dt

		if self.rect.left < 0:
			self.velocity[0] = -self.velocity[0] #- random.random()
			self.rect.left = 0

		if self.rect.right > SCREEN_WIDTH - 10:
			self.velocity[0] = -self.velocity[0] #- random.random()
			self.rect.right = SCREEN_WIDTH - 10


		if self.rect.bottom < 15:
			self.velocity[1] = -self.velocity[1] #- random.random()
			self.rect.bottom = 15


		if self.rect.top > SCREEN_HEIGHT - 30:
			self.velocity[1] = -self.velocity[1] #- random.random()
			self.rect.top = SCREEN_HEIGHT - 30

		self.rect.move_ip(*self.velocity)

class Patient(pygame.sprite.Sprite):
    	
	def __init__(self):
		super().__init__()

		IMAGE_JPG = os.path.join(DIR_PATH, image_path+'zombie.jpg')

		self.image = load(IMAGE_JPG).convert_alpha()
		self.rect = self.image.get_rect()
		self.velocity = [0, 0]

	def update(self, dt):

		self.rect.centerx += self.velocity[0]*dt 
		self.rect.centery += self.velocity[1]*dt

		if self.rect.left < 0:
			#self.velocity[1] += -self.velocity[1]
			self.velocity[0] = - self.velocity[0]  
			self.rect.left = 0

		if self.rect.right > SCREEN_WIDTH - 10:
			#self.velocity[1] += - self.velocity[1]
			self.velocity[0] = - self.velocity[0]  
			self.rect.right = SCREEN_WIDTH - 10


		if self.rect.bottom < 20:
			self.velocity[1] = - self.velocity[1]
			#self.velocity[0] += - self.velocity[0]  
			self.rect.bottom = 20


		if self.rect.top > SCREEN_HEIGHT - 20:
			self.velocity[1] = - self.velocity[1]
			#self.velocity[0] += - self.velocity[0]  
			self.rect.top = SCREEN_HEIGHT - 20

		self.rect.move_ip(*self.velocity)

class Plant(pygame.sprite.Sprite):
    	
	def __init__(self):
		super().__init__()

		IMAGE_JPG = os.path.join(DIR_PATH, image_path+'Plant.jpg')

		self.image = load(IMAGE_JPG).convert_alpha()
		self.rect = self.image.get_rect()

	def reset_pos(self):
		self.rect.centerx  = random.randrange(5, SCREEN_WIDTH-self.image.get_width())
		self.rect.centery = random.randrange(5, SCREEN_HEIGHT-self.image.get_height())

	def update(self):
		if self.rect.left < 0:
			self.reset_pos()

		if self.rect.bottom < 5:
			self.reset_pos()
				
class Player(pygame.sprite.Sprite):
    
	def __init__(self):
		super().__init__()

		IMAGE_JPG = os.path.join(DIR_PATH, image_path+'boy.png')

		self.image = load(IMAGE_JPG).convert_alpha()
		self.rect = self.image.get_rect()
		self.velocity = [SPEED_PLAYER, SPEED_PLAYER]
		

	def update(self, dt):

		self.rect.centerx += self.velocity[0]*dt 
		self.rect.centery += self.velocity[1]*dt

		#keep the player on screen
		if self.rect.bottom > SCREEN_HEIGHT:
			self.rect.top = 0 

			

		if self.rect.right > SCREEN_WIDTH:
			self.rect.left = 0 
			

		if self.rect.top < 0:
			self.rect.bottom = SCREEN_HEIGHT
			 

		if self.rect.left < 0:
			self.rect.right = SCREEN_WIDTH
			

		self.rect.move_ip(*-np.array(self.velocity))