import pygame, sys, math, random
from pygame.locals import *
import random
from constants import *
import constants

def empty_grid():
    grid = {}
    for x in range(0,18):
        for y in range(0,18):
            grid[x,y] = 0;
    return grid



def can_place_tower(towers, grid, spawn_points, x, y):
    if constants.DEBUG:
        return True
    if len(towers) > MAX_TOWERS:
        return False
    if (x,y) in spawn_points:
        return False
    else:
        return grid[x,y] == 0

def get_spawn_points(generation, baddies):
        if generation > 4:
            return [(0,0), (0,16), (16,0), (16,16)]
        elif generation > 2:
            return [(8,17)]
        else:
            return [(8,0)]

def spawn_baddies(baddies, spawn_points):
	for point in spawn_points:
		baddies.append(Baddie(point[0],point[1]))

def get_finish(generation):
    if generation > 14:
        return [(0,8), (16,8), (8,0), (8,16)]
    if generation > 11:
        return [(0,8), (16,8)]
    if generation > 6:
        return [(0,8)]
    else:
        return [(8,8)]

class Missile():
	def __init__(self,x,y,baddie):
		self.x = x
		self.y = y
		self.baddie = baddie
		self.alive = True
		self.age = 0
	def paint(self, win):
		pygame.draw.circle(win, pygame.Color(255,255,255), (self.x, self.y) , 5, 0)
	def tick(self):
		if self.x > 2000 or self.y > 2000:
			self.alive = False

		self.age+=1
		if self.baddie.alive == False or self.age > 20:
			self.alive = False
			return

		bx = self.baddie.x + (float(UNIT)/2)
		by = self.baddie.y + (float(UNIT)/2)
		dx = float(bx - self.x)
		dy = float(by - self.y)
		sx = 1 if dx > 0 else -1
		sy = 1 if dy > 0 else -1

		if dx == 0:
			self.y += (sy*5)
		elif dy == 0:
			self.x += (sx*5)
		else:
			self.y += sy * int(5 * abs(dy/dx))
			self.x += sx * int(5 * abs(dx/dy))
		if ((self.x >= self.baddie.x) and (self.x <= (self.baddie.x + UNIT))
                    and (self.y >= self.baddie.y) and (self.y <= (self.baddie.y + UNIT))):
			self.baddie.hit(10)
			self.alive = False
		
		

class Tower():
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.tick_count = 0

        @staticmethod
        def static_paint(win,x,y):
		pygame.draw.rect(win, pygame.Color(32,32,32), (x*UNIT, y*UNIT, UNIT, UNIT))

	def paint(self, win):	
                Tower.static_paint(win, self.x, self.y)


	def tick(self, baddies):
            self.tick_count += 1

            if self.tick_count > 20 and len(baddies) > 0:

                closest = None
                distance = 0 
                for baddie in baddies:
                    new_distance = ((self.x*UNIT - baddie.x) ** 2) + ((self.y*UNIT - baddie.y) ** 2)
                    if new_distance < distance or distance == 0:
                        closest = baddie
                        distance = new_distance
                if distance < ((5 * 20) ** 2):
                    self.tick_count = 0
                    return [Missile(self.x*UNIT+UNIT/2, self.y*UNIT+UNIT/2, closest)]

            return []

class Baddie():
	def __init__(self,x,y):
		self.next_x = x
		self.next_y = y
		self.current_x = 0
		self.current_y = 0
		self.mov = 10
		self.alive = True
                self.health = 100



	def choose_next_grid(self, paths, grid):
		options = []
		x = self.current_x
		y = self.current_y
		options.append((x-1,y))
		options.append((x+1,y))
		options.append((x,y-1))
		options.append((x,y+1))
                if x > 0 and y > 0 and grid[x-1,y] <> 2 and grid[x,y-1] <> 2:
                    options.append((x-1,y-1))
                if x > 0 and y < 16 and grid[x-1,y] != 2 and grid[x,y+1] != 2:
                    options.append((x-1,y+1))
                if x < 16 and y > 0 and  grid[x+1,y] != 2 and grid[x,y-1] != 2:
                    options.append((x+1,y-1))
                if x < 16 and y < 16 and grid[x+1,y] != 2 and grid[x,y+1] != 2:
                    options.append((x+1,y+1))
		options.append((x,y))
		options = [ option for option in options if option in paths ]
		
		if len(options) == 0:
			self.alive = False
		else:
			random.shuffle(options)
			chosen_option = options[0];
			for option in options:
				if (paths[chosen_option] > paths[option]):
					chosen_option = option
			self.next_x = chosen_option[0]
			self.next_y = chosen_option[1]
	def tick(self, paths, grid):
		if (self.mov == 10):
			self.current_x = self.next_x
			self.current_y = self.next_y
			self.mov = 0
			self.choose_next_grid(paths, grid)

		else:
			self.mov += 1
	def paint(self,win):
		pygame.draw.rect(win, pygame.Color(128,128,128), (self.x, self.y, UNIT, UNIT))

	def kill(self):
		self.alive = False
        def hit(self, amount):
                self.health -= amount;
                if (self.health < 0):
                    self.alive = False
	
	@property
	def x(self):
		return (self.current_x + ((self.mov /10.0) * (self.next_x - self.current_x))) * UNIT
	
	@property
	def y(self):
		return (self.current_y + ((self.mov /10.0) * (self.next_y - self.current_y))) * UNIT
		
def update_paths(finishes,grid):
	node_dict = {}
        for x in xrange(0,GRID_SIZE):
            for y in xrange(0,GRID_SIZE):
                node_dict[x,y] = A_REALLY_BIG_NUMBER

	paths = [(n[0],n[1],0) for n in finishes]

	for key in paths:
		current = key[2]
		new_process = []
		if key[0] > 0:
                    new_process.append((key[0]-1, key[1], current+1))
		if key[1] > 0:
                    new_process.append((key[0], key[1]-1, current+1))
		if key[0] < 16:
                    new_process.append((key[0]+1, key[1], current+1))
		if key[1] < 16:
                    new_process.append((key[0], key[1]+1, current+1))
                if key[0] > 0 and key[1] > 0 and grid[key[0], key[1]-1] != 2 and grid[key[0]-1, key[1]] != 2:
                    new_process.append((key[0]-1, key[1]-1, current+1.4))
                if key[0] > 0 and key[1] < 16 and grid[key[0], key[1]+1] != 2 and grid[key[0]-1, key[1]] != 2:
                    new_process.append((key[0]-1, key[1]+1, current+1.4))
                if key[0] < 16 and key[1] > 0 and grid[key[0], key[1]-1] != 2 and grid[key[0]+1, key[1]] != 2:
                    new_process.append((key[0]+1, key[1]-1, current+1.4))
                if key[0] < 16 and key[1] < 16 and grid[key[0], key[1]+1] != 2 and grid[key[0]+1, key[1]] != 2:
                    new_process.append((key[0]+1, key[1]+1, current+1.4))


		for new_node in new_process:
			coords = (new_node[0], new_node[1])
			if not coords in grid or grid[(new_node[0], new_node[1])] != 2:
				add_it = True 
				for old_node in paths:
					if (old_node[0] == new_node[0] and old_node[1] == new_node[1]):
						if old_node[2] > new_node[2]:
							paths.remove(old_node);
							add_it = True
						else:
							add_it = False
				if add_it:
					paths.append(new_node)

	for node in paths:
            node_dict[(node[0], node[1])] = node[2]
        for node in node_dict:
            if node_dict[node] == A_REALLY_BIG_NUMBER and grid[node] != 2:
                return False

	return node_dict	

def main():
	pygame.init()

        pygame.mixer.music.load('backing_music.ogg')
        pygame.mixer.music.play(-1, 0.0)


        game_status = GAME_UNPLAYED

	fpsClock = pygame.time.Clock()

	win = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
	pygame.display.set_caption('game')
	font = pygame.font.Font(None, 20)

	baddies = []
	towers = {}
	missiles = []
	grid = {}
        spawn_points = []
        generation = 0
	survived = 0
	ticks = 100
        playing = False

	while True:
            win.fill(pygame.Color(0,0,0))
            if not playing:
                Tower.static_paint(win,8,8)
                if game_status == GAME_LOST:
                    scoreText = font.render("YOU LOSE", True, pygame.Color(255,255,255)) 
                    win.blit(scoreText, (400, 400))                    
                elif game_status == GAME_WON:
                    scoreText = font.render("YOU WIN! Next time why not try hitting p for potato", True, pygame.Color(255,255,255)) 
                    win.blit(scoreText, (400, 400)) 
		for event in pygame.event.get():
                    if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        playing = True
                        grid = empty_grid()
                        finishes = get_finish(generation)
                        paths = update_paths(finishes,grid)	
                        baddies = []
                        towers = {}
                        missiles = []
                        spawn_points = []
                        generation = 0
                        survived = 0
                        ticks = 100
            else:

		ticks += 1	

		if ticks > 100:
                    spawn_points = get_spawn_points(generation, baddies)
                    spawn_baddies(baddies, spawn_points)
                    finishes = get_finish(generation)
                    generation+=1
                    paths = update_paths(finishes,grid)

                pos = pygame.mouse.get_pos()
                x = pos[0] / UNIT
                y = pos[1] / UNIT
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONUP:
                                delete_tower = False
                                if grid[x,y] == 2:
                                    delete_tower = True
                                elif can_place_tower(towers, grid, spawn_points, x, y):	
                                    grid[x,y] = 2
                                    towers[x,y] = Tower(x,y)
                                    paths = update_paths(finishes,grid)
                                    delete_tower = (paths == False)
                                if delete_tower:
                                    grid[x,y] = 0
                                    del towers[x,y]
                                    paths = update_paths(finishes,grid)
                                    if paths == False:
                                        grid[x,y] = 2
                                        towers[x,y] = Tower(x,y)
                                        paths = update_paths(finishes,grid)
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_p:
                                constants.DEBUG = not constants.DEBUG


		keys = pygame.key.get_pressed()
                if constants.DEBUG:
                    for node in paths:
                            pygame.draw.rect(win, pygame.Color(max(0,255 -int(8*paths[node])),0,0), (node[0]*UNIT, node[1]*UNIT, UNIT, UNIT))

		for baddie in baddies:
			baddie.tick(paths,grid)
			baddie.paint(win)
			if (baddie.current_x, baddie.current_y) in finishes:
				survived+=1
				baddie.kill()
		
		for tower in towers:
			missiles += towers[tower].tick(baddies)
			towers[tower].paint(win)

	        for finish in finishes:	
                    pygame.draw.rect(win, pygame.Color(255,255,255), (finish[0]*UNIT, finish[1]*UNIT, UNIT, UNIT))
                    if survived > 0:
                        pygame.draw.rect(win, pygame.Color(0,0,0),  (finish[0]*UNIT+1, finish[1]*UNIT+1, UNIT-2, min(16,survived)*(UNIT-2)/16))

		for missile in missiles:
			missile.paint(win)
			missile.tick()

		baddies = [b for b in baddies if b.alive]
		missiles = [m for m in missiles if m.alive]

		if ticks > 100:
			ticks = 0

                if survived >= 16 and not constants.DEBUG:
                    playing = False
                    game_status = GAME_LOST
                elif generation >= 20 and not constants.DEBUG:
                    playing = False
                    game_status = GAME_WON


                if can_place_tower(towers, grid, spawn_points, x, y):
                    pygame.draw.rect(win, pygame.Color(32,32,32), (x*UNIT, y*UNIT, UNIT, UNIT),4)
                elif (x,y) in grid and grid[x,y] == 2:
                    dx = 5
                    points = [ (x*UNIT-5, y*UNIT), (x*UNIT,y*UNIT-5), ((x+1)*UNIT+5, (y+1)*UNIT), ((x+1)*UNIT, (y+1)*UNIT+5) ]
                    pygame.draw.polygon(win, CROSS_COLOR, points); 
                    points = [ ((x+1)*UNIT, y*UNIT-5), ((x+1)*UNIT+5, y*UNIT), (x*UNIT, (y+1)*UNIT+5), (x*UNIT-5, (y+1)*UNIT) ]    
                    pygame.draw.polygon(win, CROSS_COLOR, points); 

            pygame.display.update()
            fpsClock.tick(30)



main()
