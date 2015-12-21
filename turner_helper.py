#!/usr/bin/env python3
import sys
import pygame
import pygame.camera
from pygame.locals import *
import pygame.gfxdraw
import math
import time
import configparser
import subprocess

pygame.init()
pygame.camera.init()

POINTER_ALPHA = 120

#            R    G    B
GRAY     = (100, 100, 100, POINTER_ALPHA)
NAVYBLUE = ( 60,  60, 100, POINTER_ALPHA)
WHITE    = (255, 255, 255, POINTER_ALPHA)
RED      = (255,   0,   0, POINTER_ALPHA)
GREEN    = (  0, 255,   0, POINTER_ALPHA)
BLUE     = (  0,   0, 255, POINTER_ALPHA)
YELLOW   = (255, 255,   0, POINTER_ALPHA)
ORANGE   = (255, 128,   0, POINTER_ALPHA)
PURPLE   = (255,   0, 255, POINTER_ALPHA)
CYAN     = (  0, 255, 255, POINTER_ALPHA)





WINDOWWIDTH = 800
WINDOWHEIGHT = 600

POINTYTHING_CONFIG_FILENAME = 'pointything.ini'

class TurnerHelper(object):

	def __init__(self):
		self.size = (WINDOWWIDTH, WINDOWHEIGHT)
		self.display = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
		self.fpsclock = pygame.time.Clock()
		self.clist = pygame.camera.list_cameras()
		self.pointything = PointyThing()
		self.pointything.load_from_file()
		self.colorchanger = ColorChanger()
		self.closebutton = CloseButton()

		self.allsprites = pygame.sprite.RenderPlain((self.pointything, self.colorchanger, self.closebutton))
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


	def process_events(self, events):
		for e in events:
			if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
				self.shutdown_when_done = True
				self.going = False
			if e.type == QUIT or (e.type == KEYDOWN and e.key == K_END):
				self.shutdown_when_done = False
				self.going = False
				
			elif e.type == MOUSEBUTTONDOWN:
				self.mouse_drag_start_x, self.mouse_drag_start_y = e.pos
				self.down_hitrect = pygame.Rect(self.mouse_drag_start_x, self.mouse_drag_start_y, 1, 1)
				self.colorchanger.mousedown(self.down_hitrect, self.pointything)
				self.mouse_down = True
			elif e.type == MOUSEBUTTONUP:
				self.mouse_down = False
				self.mouse_drag_end_x, self.mouse_drag_end_y = e.pos

				up_hitrect = pygame.Rect(self.mouse_drag_start_x, self.mouse_drag_start_y, abs(self.mouse_drag_end_x-self.mouse_drag_start_x), abs(self.mouse_drag_end_y- self.mouse_drag_end_y))
				if self.closebutton.click(up_hitrect):
					self.going = False
					self.shutdown_when_done = True		
				elif not self.colorchanger.click(up_hitrect, self.pointything):
					self.pointything.set_rect(self.mouse_drag_start_x, self.mouse_drag_start_y, self.mouse_drag_end_x, self.mouse_drag_end_y)

			
			elif e.type == KEYDOWN and e.key == K_LEFT:
				self.pointything.x -= 3
			elif e.type == KEYDOWN and e.key == K_UP:
				self.pointything.y -= 3
			elif e.type == KEYDOWN and e.key == K_RIGHT:
				self.pointything.x += 3
			elif e.type == KEYDOWN and e.key == K_DOWN:
				self.pointything.y += 3

		if self.mouse_down and self.down_hitrect:
			self.colorchanger.mousedown(self.down_hitrect, self.pointything)
			time.sleep(0.020)


	def main(self):
		self.mouse_drag_start_x, self.mouse_drag_start_y = (0, 0)
		self.mouse_drag_end_x, self.mouse_drag_end_y = (0, 0)
		self.mouse_down = False;
		self.going = True
		self.shutdown_when_done = False
		try:
			while self.going:
				events = pygame.event.get()
				self.process_events(events)
				self.allsprites.update()
				pygame.display.update()
				self.get_and_flip(False)
		finally:
			self.pointything.save_to_file()
			self.cam.stop()
			if self.shutdown_when_done:
				subprocess.call(["sudo", "shutdown", "-h", "now"])
BUTTON_PADDING = 10

COLOR_BOX_WIDTH = 50
COLOR_BOX_HEIGHT = 50
COLOR_BOX_X = WINDOWWIDTH - (COLOR_BOX_WIDTH + BUTTON_PADDING)
COLOR_BOX_Y = BUTTON_PADDING

TOOL_DEPTH_MORE_BUTTON_WIDTH = 25
TOOL_DEPTH_MORE_BUTTON_HEIGHT = 20
TOOL_DEPTH_MORE_BUTTON_X = WINDOWWIDTH - (TOOL_DEPTH_MORE_BUTTON_WIDTH + BUTTON_PADDING)
TOOL_DEPTH_MORE_BUTTON_Y = COLOR_BOX_Y + COLOR_BOX_HEIGHT + BUTTON_PADDING

TOOL_DEPTH_LESS_BUTTON_WIDTH = 25
TOOL_DEPTH_LESS_BUTTON_HEIGHT = 20
TOOL_DEPTH_LESS_BUTTON_X = WINDOWWIDTH - (TOOL_DEPTH_MORE_BUTTON_WIDTH + TOOL_DEPTH_LESS_BUTTON_WIDTH + BUTTON_PADDING)
TOOL_DEPTH_LESS_BUTTON_Y = COLOR_BOX_Y + COLOR_BOX_HEIGHT + BUTTON_PADDING

TOOL_ANGLE_MORE_BUTTON_WIDTH = 25
TOOL_ANGLE_MORE_BUTTON_HEIGHT = 20
TOOL_ANGLE_MORE_BUTTON_X = WINDOWWIDTH - (TOOL_ANGLE_MORE_BUTTON_WIDTH + BUTTON_PADDING)
TOOL_ANGLE_MORE_BUTTON_Y = COLOR_BOX_Y + TOOL_DEPTH_MORE_BUTTON_Y + BUTTON_PADDING

TOOL_ANGLE_LESS_BUTTON_WIDTH = 25
TOOL_ANGLE_LESS_BUTTON_HEIGHT = 20
TOOL_ANGLE_LESS_BUTTON_X = WINDOWWIDTH - (TOOL_ANGLE_MORE_BUTTON_WIDTH + TOOL_ANGLE_LESS_BUTTON_WIDTH + BUTTON_PADDING)
TOOL_ANGLE_LESS_BUTTON_Y = COLOR_BOX_Y + TOOL_DEPTH_LESS_BUTTON_Y + BUTTON_PADDING

BAR_1_WIDTH_MORE_BUTTON_WIDTH = 25
BAR_1_WIDTH_MORE_BUTTON_HEIGHT = 20
BAR_1_WIDTH_MORE_BUTTON_X = WINDOWWIDTH - (BAR_1_WIDTH_MORE_BUTTON_WIDTH + BUTTON_PADDING)
BAR_1_WIDTH_MORE_BUTTON_Y = COLOR_BOX_Y + TOOL_ANGLE_MORE_BUTTON_Y + BUTTON_PADDING

BAR_1_WIDTH_LESS_BUTTON_WIDTH = 25
BAR_1_WIDTH_LESS_BUTTON_HEIGHT = 20
BAR_1_WIDTH_LESS_BUTTON_X = WINDOWWIDTH - (BAR_1_WIDTH_MORE_BUTTON_WIDTH + BAR_1_WIDTH_LESS_BUTTON_WIDTH + BUTTON_PADDING)
BAR_1_WIDTH_LESS_BUTTON_Y = COLOR_BOX_Y + TOOL_ANGLE_LESS_BUTTON_Y + BUTTON_PADDING

BAR_2_WIDTH_MORE_BUTTON_WIDTH = 25
BAR_2_WIDTH_MORE_BUTTON_HEIGHT = 20
BAR_2_WIDTH_MORE_BUTTON_X = WINDOWWIDTH - (BAR_2_WIDTH_MORE_BUTTON_WIDTH + BUTTON_PADDING)
BAR_2_WIDTH_MORE_BUTTON_Y = COLOR_BOX_Y + BAR_1_WIDTH_MORE_BUTTON_Y + BUTTON_PADDING

BAR_2_WIDTH_LESS_BUTTON_WIDTH = 25
BAR_2_WIDTH_LESS_BUTTON_HEIGHT = 20
BAR_2_WIDTH_LESS_BUTTON_X = WINDOWWIDTH - (BAR_2_WIDTH_MORE_BUTTON_WIDTH + BAR_2_WIDTH_LESS_BUTTON_WIDTH + BUTTON_PADDING)
BAR_2_WIDTH_LESS_BUTTON_Y = COLOR_BOX_Y + BAR_1_WIDTH_LESS_BUTTON_Y + BUTTON_PADDING

CLOSE_BOX_X = 10
CLOSE_BOX_Y = 10
CLOSE_BOX_WIDTH = 25
CLOSE_BOX_HEIGHT = 25

INITIAL_COLOR = WHITE

class CloseButton(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.close_box_rect = pygame.Rect(CLOSE_BOX_Y, CLOSE_BOX_Y, CLOSE_BOX_WIDTH, CLOSE_BOX_HEIGHT)

	def click(self, hitrect):
		if self.close_box_rect.colliderect(hitrect):
			return True
		
	
	def update(self):
		surface = pygame.display.get_surface()
		pygame.gfxdraw.box(surface, self.close_box_rect, GRAY )
		pygame.gfxdraw.line(surface, self.close_box_rect.topright[0], self.close_box_rect.topright[1], self.close_box_rect.bottomleft[0], self.close_box_rect.bottomleft[1], RED)
		pygame.gfxdraw.line(surface, self.close_box_rect.topleft[0], self.close_box_rect.topleft[1], self.close_box_rect.bottomright[0], self.close_box_rect.bottomright[1], RED)


class ColorChanger(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.label_font = pygame.font.SysFont("sans", 10)
		self.color_queue = [INITIAL_COLOR, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN]

		#COLOR FOR TOOL
		self.color_box_rect= pygame.Rect(COLOR_BOX_X, COLOR_BOX_Y, COLOR_BOX_WIDTH, COLOR_BOX_HEIGHT)

		#TOOL DEPTH BUTTON
		self.tool_depth_more_button_rect = pygame.Rect(TOOL_DEPTH_MORE_BUTTON_X, TOOL_DEPTH_MORE_BUTTON_Y, TOOL_DEPTH_MORE_BUTTON_WIDTH, TOOL_DEPTH_MORE_BUTTON_HEIGHT)
		self.tool_depth_less_button_rect = pygame.Rect(TOOL_DEPTH_LESS_BUTTON_X, TOOL_DEPTH_LESS_BUTTON_Y, TOOL_DEPTH_LESS_BUTTON_WIDTH, TOOL_DEPTH_LESS_BUTTON_HEIGHT)

		#ANGLE BUTTON
		self.tool_angle_more_button_rect = pygame.Rect(TOOL_ANGLE_MORE_BUTTON_X, TOOL_ANGLE_MORE_BUTTON_Y, TOOL_ANGLE_MORE_BUTTON_WIDTH, TOOL_ANGLE_MORE_BUTTON_HEIGHT)
		self.tool_angle_less_button_rect = pygame.Rect(TOOL_ANGLE_LESS_BUTTON_X, TOOL_ANGLE_LESS_BUTTON_Y, TOOL_ANGLE_LESS_BUTTON_WIDTH, TOOL_ANGLE_LESS_BUTTON_HEIGHT)

		#BAR 1 WIDTH (holder part)
		self.bar_1_width_more_button_rect = pygame.Rect(BAR_1_WIDTH_MORE_BUTTON_X, BAR_1_WIDTH_MORE_BUTTON_Y, BAR_1_WIDTH_MORE_BUTTON_WIDTH, BAR_1_WIDTH_MORE_BUTTON_HEIGHT)
		self.bar_1_width_less_button_rect = pygame.Rect(BAR_1_WIDTH_LESS_BUTTON_X, BAR_1_WIDTH_LESS_BUTTON_Y, BAR_1_WIDTH_LESS_BUTTON_WIDTH, BAR_1_WIDTH_LESS_BUTTON_HEIGHT)

		#BAR 2 WIDTH (other thing)
		self.bar_2_width_more_button_rect = pygame.Rect(BAR_2_WIDTH_MORE_BUTTON_X, BAR_2_WIDTH_MORE_BUTTON_Y, BAR_2_WIDTH_MORE_BUTTON_WIDTH, BAR_2_WIDTH_MORE_BUTTON_HEIGHT)
		self.bar_2_width_less_button_rect = pygame.Rect(BAR_2_WIDTH_LESS_BUTTON_X, BAR_2_WIDTH_LESS_BUTTON_Y, BAR_2_WIDTH_LESS_BUTTON_WIDTH, BAR_2_WIDTH_LESS_BUTTON_HEIGHT)

	def mousedown(self, hitrect, pointything):
		if self.color_box_rect.colliderect(hitrect):
			return True

		if self.tool_depth_more_button_rect.colliderect(hitrect):
			pointything.increase_tool_depth()
			return True

		if self.tool_depth_less_button_rect.colliderect(hitrect):
			pointything.decrease_tool_depth()
			return True

		if self.tool_angle_more_button_rect.colliderect(hitrect):
			pointything.decrease_tool_angle_dividend()
			return True

		if self.tool_angle_less_button_rect.colliderect(hitrect):
			pointything.increase_tool_angle_dividend()
			return True

		if self.bar_1_width_more_button_rect.colliderect(hitrect):
			pointything.increase_bar_1_width()
			return True

		if self.bar_1_width_less_button_rect.colliderect(hitrect):
			pointything.decrease_bar_1_width()
			return True



	def click(self, hitrect, pointything):
		if self.color_box_rect.colliderect(hitrect):
			self.color_queue.append(self.color_queue.pop(0))
			pointything.color = self.color_queue[0]
			return True

		if self.tool_depth_more_button_rect.colliderect(hitrect):
			return True

		if self.tool_depth_less_button_rect.colliderect(hitrect):
			return True

		if self.tool_angle_more_button_rect.colliderect(hitrect):
			return True

		if self.tool_angle_less_button_rect.colliderect(hitrect):
			return True

		if self.bar_1_width_more_button_rect.colliderect(hitrect):
			return True

		if self.bar_1_width_less_button_rect.colliderect(hitrect):
			return True



	def update(self):
		surface = pygame.display.get_surface()
		pygame.gfxdraw.box(surface, self.color_box_rect, self.color_queue[0] )

		plus_A = self.tool_depth_more_button_rect.midright
		line_length = int(self.tool_depth_more_button_rect.width / 6)
		plus_B = (plus_A[0] - int(self.tool_depth_more_button_rect.width / 3), plus_A[1])
		plus_C = (plus_A[0] - line_length, plus_A[1] - line_length)
		plus_D = (plus_A[0] - line_length, plus_A[1] + line_length)
		pygame.gfxdraw.line(surface, plus_A[0], plus_A[1], plus_B[0], plus_B[1], GREEN)
		pygame.gfxdraw.line(surface, plus_C[0], plus_C[1], plus_D[0], plus_D[1], GREEN)
		minus_A = self.tool_depth_less_button_rect.midleft
		minus_B = (minus_A[0] + int(self.tool_depth_more_button_rect.width / 3), minus_A[1])
		pygame.gfxdraw.line(surface, minus_A[0], minus_A[1], minus_B[0], minus_B[1], GREEN)

		tool_depth_label = self.label_font.render("Depth", 1, (200, 0, 200, 200))
		tool_depth_label_rect = tool_depth_label.get_rect()
		tool_depth_label_rect.center = self.tool_depth_more_button_rect.midleft
		surface.blit(tool_depth_label, tool_depth_label_rect.topleft)


		plus_A = self.tool_angle_more_button_rect.midright
		line_length = int(self.tool_angle_more_button_rect.width / 6)
		plus_B = (plus_A[0] - int(self.tool_angle_more_button_rect.width / 3), plus_A[1])
		plus_C = (plus_A[0] - line_length, plus_A[1] - line_length)
		plus_D = (plus_A[0] - line_length, plus_A[1] + line_length)
		pygame.gfxdraw.line(surface, plus_A[0], plus_A[1], plus_B[0], plus_B[1], GREEN)
		pygame.gfxdraw.line(surface, plus_C[0], plus_C[1], plus_D[0], plus_D[1], GREEN)
		minus_A = self.tool_angle_less_button_rect.midleft
		minus_B = (minus_A[0] + int(self.tool_angle_more_button_rect.width / 3), minus_A[1])
		pygame.gfxdraw.line(surface, minus_A[0], minus_A[1], minus_B[0], minus_B[1], GREEN)


		tool_angle_label = self.label_font.render("Angle", 1, (200, 0, 200, 200))
		tool_angle_label_rect = tool_angle_label.get_rect()
		tool_angle_label_rect.center = self.tool_angle_more_button_rect.midleft
		surface.blit(tool_angle_label, tool_angle_label_rect.topleft)


		plus_A = self.bar_1_width_more_button_rect.midright
		line_length = int(self.bar_1_width_more_button_rect.width / 6)
		plus_B = (plus_A[0] - int(self.bar_1_width_more_button_rect.width / 3), plus_A[1])
		plus_C = (plus_A[0] - line_length, plus_A[1] - line_length)
		plus_D = (plus_A[0] - line_length, plus_A[1] + line_length)
		pygame.gfxdraw.line(surface, plus_A[0], plus_A[1], plus_B[0], plus_B[1], GREEN)
		pygame.gfxdraw.line(surface, plus_C[0], plus_C[1], plus_D[0], plus_D[1], GREEN)
		minus_A = self.bar_1_width_less_button_rect.midleft
		minus_B = (minus_A[0] + int(self.bar_1_width_more_button_rect.width / 3), minus_A[1])
		pygame.gfxdraw.line(surface, minus_A[0], minus_A[1], minus_B[0], minus_B[1], GREEN)

		bar_1_width_label = self.label_font.render("Bar Width", 1, (200, 0, 200, 200))
		bar_1_width_label_rect = bar_1_width_label.get_rect()
		bar_1_width_label_rect.center = self.bar_1_width_more_button_rect.midleft
		surface.blit(bar_1_width_label, bar_1_width_label_rect.topleft)

		pygame.gfxdraw.box(surface, self.tool_depth_more_button_rect, GRAY)
		pygame.gfxdraw.box(surface, self.tool_depth_less_button_rect, GRAY)
		pygame.gfxdraw.box(surface, self.tool_angle_more_button_rect, GRAY)
		pygame.gfxdraw.box(surface, self.tool_angle_less_button_rect, GRAY)
		pygame.gfxdraw.box(surface, self.bar_1_width_more_button_rect, GRAY)
		pygame.gfxdraw.box(surface, self.bar_1_width_less_button_rect, GRAY)


TOOL_ANGLE_INCREMENT = 0.5
TOOL_DEPTH_INCREMENT = 2
BAR_1_WIDTH_INCREMENT = 2

INITIAL_X = int(WINDOWHEIGHT / 2)
INITIAL_Y = int(WINDOWWIDTH / 2)
INITIAL_DELTA_X = 100
INITIAL_DELTA_Y = 10
INITIAL_TOOL_DEPTH = 20
INITIAL_BAR_1_WIDTH = 10
INITIAL_TOOL_ANGLE_DIVIDEND = 9
INITIAL_UPSIDE_DOWN = False
INITIAL_POINTING_RIGHT = False

class PointyThing(pygame.sprite.Sprite):
	def __init__(self, x = INITIAL_X, y = INITIAL_Y,
			tool_angle_dividend = INITIAL_TOOL_ANGLE_DIVIDEND,
			tool_depth = INITIAL_TOOL_DEPTH ,
			bar_1_width = INITIAL_BAR_1_WIDTH,
			delta_x = INITIAL_DELTA_X,
			delta_y = INITIAL_DELTA_Y,
			color = INITIAL_COLOR,
			upside_down = INITIAL_UPSIDE_DOWN,
			pointing_right = INITIAL_POINTING_RIGHT):
		pygame.sprite.Sprite.__init__(self)
		self.x, self.y = (x, y)
		self.tool_angle_dividend = tool_angle_dividend
		self.tool_depth = tool_depth
		self.bar_1_width = bar_1_width
		self.delta_x = delta_x
		self.delta_y = delta_y
		self.color = color
		self.pointing_right = pointing_right
		self.upside_down = upside_down



	def set_rect(self, start_x, start_y, end_x, end_y):

		self.pointing_right = start_x > end_x
		self.upside_down = start_y < end_y
		self.x, self.y = (start_x, start_y)
		self.delta_x = abs(start_x - end_x)
		self.delta_y = abs(start_y - end_y)


	def increase_tool_angle_dividend(self):
		if self.tool_angle_dividend <= 32:
			self.tool_angle_dividend += TOOL_ANGLE_INCREMENT
			if self.tool_angle_dividend == 0:
				self.tool_angle_dividend += 1


	def decrease_tool_angle_dividend(self):
		if self.tool_angle_dividend >= 4:
			self.tool_angle_dividend -= TOOL_ANGLE_INCREMENT
			if self.tool_angle_dividend == 0:
				self.tool_angle_dividend += 1

	def increase_tool_depth(self):
		if self.tool_depth <= 200:
			self.tool_depth += TOOL_DEPTH_INCREMENT

	def decrease_tool_depth(self):
		if self.tool_depth >= 1:
			self.tool_depth -= TOOL_DEPTH_INCREMENT

	def increase_bar_1_width(self):
		if self.bar_1_width <= 200:
			self.bar_1_width += BAR_1_WIDTH_INCREMENT

	def decrease_bar_1_width(self):
		if self.bar_1_width >= 1:
			self.bar_1_width -= BAR_1_WIDTH_INCREMENT

	def save_to_file(self, filename=POINTYTHING_CONFIG_FILENAME):
		config = configparser.ConfigParser()
		config['SETTINGS'] = {'x': self.x,
					'y' : self.y,
					'tool_angle_dividend' : self.tool_angle_dividend,
					'tool_depth' : self.tool_depth,
					'bar_1_width' : self.bar_1_width,
					'delta_x' : self.delta_x,
					'delta_y' : self.delta_y,
					'color_r' : self.color[0],
					'color_g' : self.color[1],
					'color_b' : self.color[2],
					'color_a' : self.color[3],
					'pointing_right' : self.pointing_right,
					'upside_down' : self.upside_down}
		with open (filename, 'w+') as configfile:
			config.write(configfile)

	def load_from_file(self, filename=POINTYTHING_CONFIG_FILENAME):
		config = configparser.ConfigParser()
		config.read(filename)
		if 'SETTINGS' in config:
			settings = config['SETTINGS']
		else:
			settings = {}
		self.x = int(settings.get('x', INITIAL_X))
		self.y = int(settings.get('y', INITIAL_Y))
		self.tool_angle_dividend = float(settings.get('tool_angle_dividend', INITIAL_TOOL_ANGLE_DIVIDEND))
		self.tool_depth = int(settings.get('tool_depth', INITIAL_TOOL_DEPTH))
		self.bar_1_width = int(settings.get('bar_1_width', INITIAL_BAR_1_WIDTH))
		self.delta_x = int(settings.get('delta_x', INITIAL_DELTA_X))
		self.delta_y = int(settings.get('delta_y', INITIAL_DELTA_Y))
		color_r = int(settings.get('color_r', INITIAL_COLOR[0]))
		color_g = int(settings.get('color_g', INITIAL_COLOR[1]))
		color_b = int(settings.get('color_b', INITIAL_COLOR[2]))
		color_a = int(settings.get('color_a', INITIAL_COLOR[3]))
		self.color = (color_r, color_g, color_b, color_a)

		self.upside_down = settings.get('upside_down', INITIAL_UPSIDE_DOWN) == 'True'
		self.pointing_right = settings.get('pointing_right', INITIAL_POINTING_RIGHT) == 'True'


	def update(self):
		pointer_bar_length = WINDOWHEIGHT - self.y
		surface = pygame.display.get_surface()

		if self.upside_down:
			bar_end = 0
		else:
			bar_end = WINDOWHEIGHT

		A = (self.x, self.y)

		if self.pointing_right:
			a = -self.tool_depth
			delta_x = -self.delta_x
		else:
			a = self.tool_depth
			delta_x = self.delta_x
		#tool_angle should skip 0
		tool_angle = math.pi / self.tool_angle_dividend
		#probably should care if tool angle is pi
		d = math.tan(tool_angle) * self.tool_depth
		B = ((A[0] + a), (A[1] - d))
		C = ((A[0] + a), (A[1] - self.delta_y))


		D = ((A[0] + delta_x), (A[1] - self.delta_y))

		E = ((A[0] + delta_x), (bar_end))
		F = (((A[0] + delta_x) - self.bar_1_width), (bar_end))

		if self.upside_down ^ self.pointing_right:
			tmp_F = F
			F = E
			E = tmp_F

		G = (((A[0] + delta_x) - self.bar_1_width), (A[1] + self.delta_y))

		if self.upside_down ^ self.pointing_right:
			tmp_d = D
			D = (G[0], G[1] - (self.delta_y * 2))
			G = (tmp_d[0], tmp_d[1] + (self.delta_y * 2))

		H = ((A[0] + a), (A[1] + self.delta_y))
		I = ((A[0] + a), (A[1] + d))


		pygame.gfxdraw.filled_polygon(surface, (A, B, C, D, E, F, G, H, I), self.color )



turner_helper = TurnerHelper()
turner_helper.main()
