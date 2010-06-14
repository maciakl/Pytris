#!/usr/bin/env python

# PyTris (c) Lukasz Grzegorz Maciak
# Licensed under GNU General Public License Version 3

import sys, pygame, random
from pygame.locals import *

pygame.init()

# useful constants
size = width, height = 400, 385
lines_per_level = 20
delay = 1000

# define colors
black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
white = 255, 255, 255
yellow = 255, 255, 0
purple = 160, 32, 240
cyan = 0, 255, 255
orange = 255, 165, 0
gray =  45, 45, 45

block_size = 15 	# each piece is 4 blocks
block_gap = 1		# distance between blocks

offset = block_size + block_gap

twidth = 10 * offset	
right_edge = twidth - block_size 

theight = 24 * offset
bottom_edge = theight - block_size

start_point = twidth/2 - block_size, 0
next_point = twidth+125, 100


# Block object exists mostly to allow us to break a piece into individual
# components once it is locked in place. This is why the color information
# is redundant
class Block(object):
	""" Represents a rectangular Tetris block """

	def __init__(self, x, y, color):

		self.x = x
		self.y = y
		self.color = color

	def draw(self):

		pygame.draw.rect(screen, self.color, self.rect)

	@property
	def rect(self):
		return (self.x, self.y, block_size, block_size)

class Piece(object):
	""" A Tetris Piece - composed of 4 blocks """

	def __init__(self,x,y):

		self.x = x
		self.y = y
		self.mobile = True

		self.rotation = 0 # defines which of the members of self.positions to use for this object

		# set of offsets that is applied to coordinates of each block in this piece
		self.positions = None 


	def get_blocks(self):
		""" Returns an array of 4 blocks which make up this piece; each block has it's own coordinates and draw function """

		blocks = []

		for i in range(4):
			blocks.append( Block(self.x + self.positions[self.rotation][i][0], self.y + self.positions[self.rotation][i][1], self.color) )
		
		return blocks
		
	def draw(self):
		""" Draw all the blocks of this piece to the screen """
		
		blocks = self.get_blocks()

		for b in blocks:
			pygame.draw.rect(screen, self.color, b.rect)

	# calling flip repeatedly cycles through all available positions and goes back to the first one
	def flip(self):
		if(self.rotation < len(self.positions) -1): 
			self.rotation += 1
		else:
			self.rotation = 0

	def set_point(self, x, y):
		self.x = x
		self.y = y


# Define different piece types: Z, S, O, T, I, L, J

class ZPiece(Piece):

	def __init__(self,x,y):

		super(ZPiece, self).__init__(x, y)

		self.color = red

		self.positions = 	[ 
						( (0,0), (offset, 0), (offset, offset), (2*offset, offset) 	),
						( (0,0), (0, offset), (-offset, offset), (-offset, 2*offset) 	)
					]
class SPiece(Piece):

	def __init__(self,x,y):

		super(SPiece, self).__init__(x, y)

		self.color = green

		self.positions = 	[ 
						( (0,0), (-offset, 0), (-offset, offset), (-2*offset, offset) 	),
						( (0,0), (0, offset), (offset, offset), (offset, 2*offset) 	)
					]


class OPiece(Piece):

	def __init__(self, x, y):
		
		super(OPiece, self).__init__(x,y)

		self.color = yellow

		self.positions = 	[ 
						( (0,0), (offset, 0), (offset, offset), (0, offset) 	)
					]


class TPiece(Piece):

	def __init__(self,x,y):

		super(TPiece, self).__init__(x, y)

		self.color = purple

		self.positions = 	[ 
						( (0,0), (0, offset), (-offset, offset), (offset, offset) 	),
						( (0,0), (0, offset), (offset, offset), (0, 2*offset) 	),
						( (0,0), (-offset, 0), (offset, 0), (0, offset) 	),
						( (0,0), (0, offset), (-offset, offset), (0, 2*offset) 	),
					]


class IPiece(Piece):

	def __init__(self,x,y):

		super(IPiece, self).__init__(x, y)

		self.color = cyan

		self.positions = 	[ 
						( (0,0), (0, offset), (0, 2*offset), (0, 3*offset) 	),
						( (0,0), (offset, 0), (2*offset, 0), (3*offset, 0) 	)
					]


class LPiece(Piece):

	def __init__(self,x,y):

		super(LPiece, self).__init__(x, y)

		self.color = orange

		self.positions = 	[ 
						( (0,0), (0, offset), (0, 2*offset), (offset, 2*offset) 	),
						( (0,0), (0, offset), (offset, 0), (2*offset, 0) 	),
						( (0,0), (-offset, 0), (0, offset), (0, 2*offset) 	),
						( (0,0), (0, offset), (-offset, offset), (-2*offset, offset) 	),
					]

class JPiece(Piece):

	def __init__(self,x,y):

		super(JPiece, self).__init__(x, y)

		self.color = blue

		self.positions = 	[ 
						( (0,0), (0, offset), (0, 2*offset), (-offset, 2*offset) 	),
						( (0,0), (offset, 0), (2*offset, 0), (2*offset, offset) 	),
						( (0,0), (offset, 0), (0, offset), (0, 2*offset) 	),
						( (0,0), (0, offset), (offset, offset), (2*offset, offset) 	),
					]



class Grid(object):

	def __init__(self):

		self.current = None
		self.next = None
		self.blocks = []

		self.next_piece()

		self.total_cleared_lines = 0
		self.cleared_lines = 0
		self.level = 1
		self.score = 0

		self.lines_til_next_level = lines_per_level

		self.delay = delay

		self.game_over = False

		self.next_rect = pygame.Rect(150, 90, 300, 300)

		# this is for multiplying scores
		self.multiplier = 	{
						0 : 0, 		# no lines cleared
						1 : 40,		# single line cleared
						2 : 100,	# two lines cleared
						3 : 300,	# three lines cleared
						4 : 1200	# TETRIS
					}

		self.nfont = pygame.font.Font(None, 24)
		self.largefont = pygame.font.Font(None, 40)
		self.smallfont = pygame.font.Font(None, 14)

	
	def random_piece(self):

		pcs = 	{
				0 : ZPiece(*next_point),
				1 : OPiece(*next_point),
				2 : SPiece(*next_point),
				3 : TPiece(*next_point),
				4 : IPiece(*next_point),
				5 : LPiece(*next_point),
				6 : JPiece(*next_point)
			}

		c = random.choice(xrange(len(pcs)))

		return pcs[c]


	def next_piece(self):

		if not self.next:
			self.next = self.random_piece()
			self.current = self.random_piece()
		else:
			self.current = self.next
			self.next = self.random_piece()

		self.current.set_point(*start_point)

	def move_down(self):

		if(self.current.y < theight): 
			self.current.y += offset

			if self.has_overlap(): 
				self.current.y -= offset
				self.current.mobile = False
		else:
			self.current.mobile = False

		if self.current.mobile == False and self.current.y == 0:
			self.game_over = True

	# this is a hard drop - just go all the way down until you hit something
	def drop_down(self):

		while(self.current.mobile): self.move_down()

	def move_right(self):
		if(self.current.mobile): self.current.x += offset

		if self.has_overlap(): self.current.x -= offset

	def move_left(self):
		if(self.current.mobile): self.current.x -= offset
		if self.has_overlap(): self.current.x += offset

	# TODO: wall kick logic needed
	def rotate(self):
		self.current.flip()

		while self.has_overlap(): self.current.flip()

	# Saves individual blocks of the current piece - they become part of the grid
	# Automatically check for lines
	def remember_block_positions(self):

		self.blocks.extend(self.current.get_blocks())
		self.next_piece()

		self.blocks = sorted(self.blocks, key= lambda block: block.y)

		self.check_for_lines()

		#for b in self.blocks: print str(b.y)+", "

	def draw_blocks(self):
		
		for b in self.blocks:
			b.draw()

	# check if current piece overlaps with walls or with other pieces
	def has_overlap(self):

		blocks = self.current.get_blocks()

		for b in blocks:
			if b.x < 0 or b.x > right_edge  or b.y < 0 or b.y > bottom_edge: return True

		# TODO: optimize the shit out of this
		for b in self.blocks:
			for c in self.current.get_blocks():
				if b.x == c.x and b.y == c.y: return True
		
		return False

	# TODO: there ought to be a better way to do this
	def check_for_lines(self):

		lines = {}

		for b in self.blocks:

			if b.y in lines:
				lines[b.y] +=1
			else:
				lines[b.y] = 1

		lines_to_be_destroyed = []
		
		for ln in lines:
			if lines[ln] == 10:
				self.total_cleared_lines += 1
				self.cleared_lines += 1
				lines_to_be_destroyed.append(ln)
				
		for l in lines_to_be_destroyed:
			self.destroy_line(l)

		copy_of_blocks = self.blocks[:]

		if len(lines_to_be_destroyed) > 0:
			self.collapse_hovering_blocks(min(lines_to_be_destroyed), len(lines_to_be_destroyed))
			
			#for ln in lines_to_be_destroyed:
				#self.collapse_hovering_blocks(ln, copy_of_blocks)

		self.calculate_score()


	def destroy_line(self, ln):

		# note the slice notation - I'm iterating over a copy of self.blocks but removing
		# from the original
		for b in self.blocks[:]:
			if b.y == ln: self.blocks.remove(b)



	def collapse_hovering_blocks(self, ln, total):
		""" drop down all the blocks that are hovering """

		for i,b in enumerate(self.blocks):
			if b.y < ln:
				self.blocks[i].y += offset * total
				
		

	def block_overlaps(self, block, block_list):


		for b in block_list:
			if block.y == b.y and block.x == b.x:
				return True

		return False
		


	def calculate_score(self):

		# score is calculated like so: M * ( N + 1 ) where:
		# M is multiplier (see self.multiplier)
		# N is level (self.level)

		self.score += self.multiplier[self.cleared_lines] * (self.level + 1)

		tmp = self.lines_til_next_level - self.cleared_lines

		if tmp <= 0:
			self.level +=1
			self.lines_til_next_level = lines_per_level + tmp

			self.delay -= self.level * 30

			if self.delay < 10: self.delay = 10

		else:
			self.lines_til_next_level = tmp

		self.cleared_lines = 0
		self.draw_text()


	# redraws the whole UI - we should really be bliting this shit
	def draw_ui(self):
		
		pygame.draw.rect(screen, gray, (0,0, right_edge+offset, bottom_edge+offset))

		for i in xrange(10): pygame.draw.line(screen, black, (i*offset, 0), (i*offset, theight+offset))
		for i in xrange(24): pygame.draw.line(screen, black, (0, i*offset), (twidth+offset, i*offset))

		self.draw_text()


	# I really dislike the default font in pygame
	def draw_text(self):

		msg = self.nfont.render("NEXT PIECE:", 1, white)
		screen.blit(msg, (250, 50))

		pygame.draw.rect(screen, black, (250, 200, 200, 100))

		sc = self.nfont.render("SCORE: " + str(self.score), 1, white)
		screen.blit(sc, (250, 200))

		sc = self.nfont.render("LINES: " + str(self.total_cleared_lines), 1, white)
		screen.blit(sc, (250, 230))

		sc = self.nfont.render("LEVEL: " + str(self.level), 1, white)
		screen.blit(sc, (250, 260))



		msg = self.smallfont.render("Left, Right Arrow to move", 1, white)
		screen.blit(msg, (230, 290))

		msg = self.smallfont.render("Up Arrow to flip", 1, white)
		screen.blit(msg, (230, 300))

		msg = self.smallfont.render("Down Arrow to move downw", 1, white)
		screen.blit(msg, (230, 310))

		msg = self.smallfont.render("Space or Enter to drop down", 1, white)
		screen.blit(msg, (230, 320))

		msg = self.smallfont.render("Esc to pause, F1 for new game", 1, white)
		screen.blit(msg, (230, 330))

		screen.blit(self.smallfont.render("ver 0.2", 1, white), (230, 350))

	def draw_game_over(self):

		msg = self.largefont.render("GAME OVER", 1, red)
		screen.blit(msg, (195,95))

		msg2 = self.nfont.render("PRESS F1 TO PLAY AGAIN", 1, red)
		screen.blit(msg2, (175, 130))

	


# magic
screen = pygame.display.set_mode(size)
pygame.key.set_repeat(100, 150)

#pygame.time.set_timer(USEREVENT+1, delay)

grid = Grid()
clock = pygame.time.Clock()

paused = False

time_elapsed = 0

while 1:

	if not paused and not grid.game_over:

		time_elapsed += clock.tick()

		#print str(grid.delay)

		# timed block drop
		if time_elapsed > grid.delay: 
			time_elapsed = 0
			grid.move_down()

		# check if a line was created and remove it
		grid.check_for_lines()

		# clear the next piece area
		pygame.draw.rect(screen, black, grid.next_rect)

		# draw the gridlines
		grid.draw_ui()

		# if the current piece is locked in place memorize it's position
		if not grid.current.mobile:
			grid.remember_block_positions()

		# draw the memorized blocks
		grid.draw_blocks()


	for event in pygame.event.get():

		if event.type == pygame.QUIT: sys.exit()


		if event.type == KEYDOWN:
			
			if event.key == K_ESCAPE: paused = not paused

			if event.key == K_F1: 
				grid = Grid()
				clock = pygame.time.Clock()
				paused = False
				time_elapsed = 0

			if not paused and not grid.game_over:
				if event.key == K_RIGHT: grid.move_right()
				if event.key == K_LEFT: grid.move_left()
				if event.key == K_DOWN: grid.move_down()
				if event.key == K_UP: grid.rotate()
				if event.key == K_SPACE: grid.drop_down()
				if event.key == K_RETURN: grid.drop_down()



	if not paused and not grid.game_over:

		grid.current.draw() 	# draw current piece
		grid.next.draw()	# draw the next piece
		
		pygame.display.flip()

	# draw game over message
	if grid.game_over:
		grid.draw_game_over()
		pygame.display.flip()
