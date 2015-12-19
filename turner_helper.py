#!/usr/bin/env python3
import sys
import pygame
import pygame.camera
from pygame.locals import *
import pygame.gfxdraw

pygame.init()
pygame.camera.init()

#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)



color_queue = [WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN]


WINDOWWIDTH = 800
WINDOWHEIGHT = 600


class TurnerHelper(object):

	def __init__(self):
		self.size = (WINDOWWIDTH, WINDOWHEIGHT)
		self.display = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
		self.fpsclock = pygame.time.Clock()
		self.clist = pygame.camera.list_cameras()
		self.pointything = PointyThing()
		self.colorchanger = ColorChanger()
		self.allsprites = pygame.sprite.RenderPlain((self.pointything, self.colorchanger))
		if not self.clist:
			raise ValueError("Sorry, no cameras detected.")
		self.cam = pygame.camera.Camera(self.clist[0], self.size)
		self.cam.start()
		self.snapshot = pygame.surface.Surface(self.size, 0, self.display)
		

	def get_and_flip(self, should_update):
		if self.cam.query_image():
			self.snapshot = self.cam.get_image(self.snapshot)

		self.display.blit(self.snapshot, (0,0))
		if should_update:
			pygame.display.flip()


	def main(self):
		mouse_drag_start_x, mouse_drag_start_y = (0, 0)
		mouse_drag_end_x, mouse_drag_end_y = (0, 0)
		going = True
		self.allsprites.remove(self.pointything)
		while going:
			events = pygame.event.get()
			for e in events:
				if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
					self.cam.stop()
					going = False
				elif e.type == MOUSEBUTTONDOWN:
					mouse_drag_start_x, mouse_drag_start_y = e.pos
					self.allsprites.remove(self.pointything)
				elif e.type == MOUSEBUTTONUP:
					mouse_drag_end_x, mouse_drag_end_y = e.pos				
					self.allsprites.add(self.pointything)

					hitrect = pygame.Rect(mouse_drag_start_x, mouse_drag_start_y, abs(mouse_drag_end_x-mouse_drag_start_x), abs(mouse_drag_end_y-mouse_drag_end_y))
					self.colorchanger.hit(hitrect)
				
			self.pointything.set_rect(mouse_drag_start_x, mouse_drag_start_y, mouse_drag_end_x, mouse_drag_end_y)		
			self.pointything.color = self.colorchanger.current_color
			self.allsprites.update()
			pygame.display.update()
			self.get_and_flip(False)

			
class ColorChanger(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		
		self.y = 10
		self.x = WINDOWWIDTH - 60
		self.height = 50
		self.width = 50 
		self.rect= pygame.Rect(self.x, self.y, self.width, self.height)
		self.current_color = color_queue[0]

	def hit(self, hitrect):
		if self.rect.colliderect(hitrect):
			color_queue.append(color_queue.pop(0))
			self.current_color = color_queue[0]

	def update(self):
		surface = pygame.display.get_surface()
		size = surface.get_size()
		box = pygame.gfxdraw.box(surface, self.rect, self.current_color ) 

class PointyThing(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.pointer_height = -1
		self.pointer_length = -1
		self.pointer_holder_length = -1
		self.pointer_holder_width = -1
		self.pointer_bar_width = -1
		self.x, self.y = (-1, -1)
		self.color = color_queue[0]

	def set_rect(self, start_x, start_y, end_x, end_y):

		self.pointer_height = abs(start_y - end_y) * 2
		self.pointer_length = int(abs(start_x - end_x) / 2)
		self.pointer_holder_length = int(abs(start_x - end_x) / 2)
		self.pointer_holder_width = int(max(10, self.pointer_height / 8))			
		self.pointer_bar_width = int(abs(start_x - end_x) / 8)
		self.x, self.y = (start_x, start_y)



	def update(self):
		pointer_bar_length = WINDOWHEIGHT - self.y 
		surface = pygame.display.get_surface()
		size = surface.get_size()
		pygame.gfxdraw.filled_polygon(surface, (
				 	#pointy part 
				    (self.x,self.y),
					#top of the thing 
				    (self.x + self.pointer_length, self.y - int(self.pointer_height/2)),	
					#down to the joint on the top of the pointy thing
				    (self.x + self.pointer_length, self.y - int(self.pointer_holder_width/2)),
					#to the far right corner
				    (self.x + self.pointer_length + self.pointer_holder_length, self.y - int(self.pointer_holder_width/2)),
				  	#down to the bottom right corner (touches bottom of screen)
				    (self.x + self.pointer_length + self.pointer_holder_length, self.y + pointer_bar_length),
					#down to bottom left corner of handle thing (touches bottom of screen)
				    (self.x + self.pointer_length + self.pointer_holder_length - self.pointer_bar_width, self.y + pointer_bar_length),
					#back up to the joint thing
				    (self.x + self.pointer_length + self.pointer_holder_length - self.pointer_bar_width, self.y + int(self.pointer_holder_width/2)),
					#THIS LINE IS MISSING!
					#over to the join on the bottom of the pointy thing
				    (self.x + self.pointer_length, self.y + int(self.pointer_holder_width/2)),
					#down to the bottom of the pointy thing
				    (self.x + self.pointer_length, self.y + int(self.pointer_height/2)),
					
					),

					self.color
					)

turner_helper = TurnerHelper()
turner_helper.main()
