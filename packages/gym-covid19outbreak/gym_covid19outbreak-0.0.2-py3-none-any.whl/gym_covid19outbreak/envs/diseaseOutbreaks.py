from pygame.image import load 
from pygame.surfarray import pixels_alpha
from itertools import cycle
import random
import pygame 
import numpy as np
from PIL import Image
from gym_covid19outbreak.envs.actors import SarsCovII, Plant, Player, Patient

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 520
ENEMY_COUNT = 5
FREINDS_COUNT = 7
PLANT_COUNT = 5


class DiseaseOutbreaks:


	def __init__(self, enable_render=True):

		init_result = pygame.init()

		if init_result[1] != 0:
			print('pygame not installed properly.')
			return 
		else:
			print('\nPygame successfully.')

		self.fps_clock = pygame.time.Clock()
		self.fps = 30 
		self.dt = 1/self.fps_clock.tick(self.fps)
		self.score = None  
		self.collect_plant =  None
		self.zombie_saved = None
		self.is_over= None
		self.life = None
		self.decay = 0.01
		self.font = pygame.font.Font(None, 24)
		self.reward = 0.0
		self.gif = 0 
		self.images = []

		self.__game_over = False
		self.__enable_render = enable_render

		self.size = [SCREEN_WIDTH, SCREEN_HEIGHT]

		if self.__enable_render:

			self.surface = pygame.display.set_mode(self.size)
			pygame.display.set_caption('Gym-Covid19Outbreaks')

			self.enemies_list = None
			self.plants = None
			self.all_enemies = None #pygame.sprite.Group()
			self.plant_list = None #pygame.sprite.Group()
			self.all_zombie = None #pygame.sprite.Group()
			self.background = pygame.Surface(self.surface.get_size()).convert()
			self.background.fill((255, 255, 255)) # color background

			self.board = pygame.Surface(self.surface.get_size()).convert_alpha()
			self.board.fill((10,60,50)) # color board
			

	def reset_game(self):

		self.score = 0  
		self.collect_plant =  0
		self.zombie_saved = 0
		self.is_over = False
		self.life = 0.1
		self.reward = 0.0
		self.enemies_list = []
		self.plants = []
		self.all_enemies = pygame.sprite.Group()
		self.plant_list = pygame.sprite.Group()
		self.all_zombie = pygame.sprite.Group()

		for _ in range(ENEMY_COUNT):
			sars = SarsCovII()
			sars.scale = 0.25
			sars.rect.centerx = random.randrange(100, SCREEN_WIDTH - sars.image.get_width())
			sars.rect.centery = random.randrange(0, 50 - sars.image.get_height())

			sars.velocity[0] = random.randint(-1, 1)
			sars.velocity[1] = random.randint(-1, 1)
			self.enemies_list.append(sars)
			self.all_enemies.add(sars)

		for _ in range(FREINDS_COUNT):
			zombie = Patient()
			zombie.scale=0.255
			zombie.rect.centerx = random.randrange(0, (SCREEN_WIDTH - zombie.image.get_width())//2)
			zombie.rect.centery = random.randrange(0, 50 - zombie.image.get_height())

			zombie.velocity[0] = random.randint(-1, 1)
			zombie.velocity[1] = random.randint(-1, 1)
			self.all_zombie.add(zombie)

		for _ in range(PLANT_COUNT):
			plant = Plant()
			plant.scale=0.25
			plant.rect.centerx = random.randrange(SCREEN_WIDTH - plant.image.get_width())
			plant.rect.centery = random.randrange(SCREEN_HEIGHT - plant.image.get_height()-100)

			self.plant_list.add(plant)
			self.plants.append(plant)

		self.player = Player()
		self.scale=0.25
		self.player.rect.centerx = (SCREEN_WIDTH - self.player.image.get_width())/2 
		self.player.rect.centery = SCREEN_HEIGHT - self.player.image.get_height() - 100



		self.__on_draw()
		#pygame.display.flip()


	def __view_update(self, mode='human'):		

		#/1000 
		if not self.__game_over:

			self.reward = -0.0001

			for i, sprite in enumerate(self.enemies_list):
				#  enemies hit together
				others = self.enemies_list[i-1]
				vx = sprite.velocity[0]
				vy = sprite.velocity[1]

				if 1000*self.dt%5 != 0.0:

					if sprite.rect.colliderect(others) == 1:
						sprite.velocity[1] = others.velocity[0] 
						sprite.velocity[0] = others.velocity[1]

						others.velocity[0] = vy - random.random()
						others.velocity[1] = vx - random.random()
						others.update(self.dt)
				else:
					if sprite.rect.collidelist(self.enemies_list):
						sprite.velocity[1] = sprite.velocity[0] 
						sprite.velocity[0] = sprite.velocity[1]

				sprite.update(self.dt)

			# ****************** PLAYER HIT ENEMIES **************************************************
			# Player kill Sars Cov II if he have plant otherwise he contaminate environment.
			hit_enemies = pygame.sprite.spritecollide(self.player, self.all_enemies, True)
			for _ in hit_enemies:
				if self.collect_plant > 0:
					self.collect_plant -= 1
					self.reward = (self.decay + self.collect_plant) -  2
					#This reward says to agent that kill sars-cov II is necessary
					#but not priority.
				else:
					self.life -= self.decay
					for _ in range(3):
						sars = SarsCovII()
						sars.scale = 0.25
						sars.rect.centerx = random.randrange(100, SCREEN_WIDTH - sars.image.get_width())
						sars.rect.centery = random.randrange(0, 50 - sars.image.get_height())

						sars.velocity[0] = random.randint(-1, 1)
						sars.velocity[1] = random.randint(-1, 1)
						self.enemies_list.append(sars)
						self.all_enemies.add(sars)
					self.reward = -(3.0 + self.decay)
					

			# ************************* PLAYER SAVES PATIENT **********************************************
			# Player collects plant and save patient.
			if self.collect_plant > 0:
				zombie_hit = pygame.sprite.spritecollide(self.player, self.all_zombie, True)
				for hit in zombie_hit:
					self.score += 1
					self.collect_plant -= 1
					self.zombie_saved += 1
					self.reward = 1.0 + self.zombie_saved 
					

			# *************************** ENEMIES COLLIDES WITH PATIENT *************************************
			# collision between enemies and patient  increases unstability.
			enemies_patient_collision = pygame.sprite.groupcollide(self.all_zombie, self.enemies_list, False, False)
			for sprite1, sprite2 in enemies_patient_collision.items():
				speed = np.array([0, 0])
				for u in sprite2:
					speed += random.randint(-1, 1)
				sprite1.velocity = speed/len(sprite2)


			self.all_zombie.update(self.dt)
			self.player.update()


			# *************************** PLAYER COLLIDES PLANTS **********************************************
			plant_hit = pygame.sprite.spritecollide(self.player, self.plant_list, False)
			for flower in plant_hit:
				flower.reset_pos()
				self.score += 2
				self.collect_plant += 1
				self.reward = 1.0 + self.collect_plant + self.decay

			self.plant_list.update()	
			
			self.is_over = (self.life < 0) or (self.zombie_saved == FREINDS_COUNT) or (len(self.all_enemies) <= 0.0)
		
			
			self.__on_draw()
		if mode == "human":	
			pygame.display.flip()
			self.fps_clock.tick(self.fps)


	def __controller_update(self):
		if not self.__game_over:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.__game_over = True
					self.quit_game()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
					elif event.key == pygame.K_g:
						self.gif = 60
		# else:
		# 	pygame.quit()
				

	def quit_game(self):
		try:
			self.__game_over = True
			if self.__enable_render is True:
				pygame.display.quit()
				pygame.quit()
		except Exception:
			pass

	def update(self, mode="human"):

		try:
			self.__view_update(mode)
			self.__controller_update()
		except Exception as e:
			self.__game_over = True
			self.quit_game()
			raise e
		else:
			return 

	def __on_draw(self):

		self.surface.blit(self.background, (0, 0))
		self.surface.blit(self.board, (0,0))
		self.all_enemies.draw(self.surface)
		self.all_zombie.draw(self.surface)
		self.plant_list.draw(self.surface)
		self.surface.blit(self.player.image, self.player.rect.center)

		self.display_message(f'Collected plant: {self.collect_plant}', [10, SCREEN_HEIGHT - 100])
		self.display_message(f'Score: {self.score}', [10, SCREEN_HEIGHT - 50] )
		self.display_message(f'Sars Cov II: {len(self.all_enemies)}', [SCREEN_WIDTH-150, SCREEN_HEIGHT - 100])
		self.display_message(f'Life: {round(self.life*100, 2)}', [SCREEN_WIDTH-150, SCREEN_HEIGHT - 50])
		self.display_message(f'Patient: {len(self.all_zombie)}', [SCREEN_WIDTH//2-50, SCREEN_HEIGHT - 75] )


	def display_message(self, message, y_pos):

		shadow = self.font.render(message, True, (0, 0, 0))
		text = self.font.render(message, True, (255, 255, 255))
		text_position = y_pos
		text_position[0] += 5
		text_position[1] += 5
		self.surface.blit(shadow, text_position)
		self.surface.blit(text, text_position)

	def getObservation(self):
		return pygame.surfarray.array3d(pygame.display.get_surface()).astype(np.uint8)


	def getReward(self):
		return self.reward

	def make_gif(self):
		if self.gif > 0:
			strFormat = 'RGBA'
			raw_str = pygame.image.tostring(self.surface, strFormat, False)
			image = Image.frombytes(
				strFormat, self.surface.get_size(),
				raw_str)
			self.images.append(image)
			self.gif -= 1  
			if self.gif == 0: 
				self.images[0].save('covid19outbreak.gif', 
					save_all=True, append_images = self.images[1:],
					optimize=True, duration=1000//self.fps,
					loop=0)
				self.images=[]



# if __name__ == '__main__':

# 	env = Covid19Outbreaks()
# 	#env.reset_game() 

# 	while True:
# 		action = random.choices([i for i in range(1, 8)])[0]
# 		env.update(action)