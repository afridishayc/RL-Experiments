import pygame
import threading
from gym import Env, spaces


class VecnaWarehouseEnv(Env):

	def __init__(self, start_position=None, goal_position=None, obstacle_position=None):
		super(VecnaWarehouseEnv, self).__init__()

		self.current_position = start_position
		self.goal_position = goal_position
		self.obstacle_position = obstacle_position

		self.action_space = spaces.Discrete(4)
		self.observation_space = spaces.MultiDiscrete([12, 12, 13])
		self.world_dims = (3, 4)

		self.world_map = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]
		self.left_edges = [0, 4, 8]
		self.right_edges = [3, 7, 11]

		self.walls = [(1, 5), (5, 1), (5, 9), (9, 5), (6, 7), (7, 6)]

		self.th = None
		pygame.init()

	def step(self, action):
		temp_next_position = self.current_position
		collision = False
		reward = -1
		done = False

		if self.current_position != self.goal_position:

			if action == 0:
				# Top
				temp_next_position = self.current_position - self.world_dims[1]
				if temp_next_position < 0:
					collision = True
					temp_next_position = self.current_position
			elif action == 1:
				# Bottom
				temp_next_position = self.current_position + self.world_dims[1]
				if temp_next_position > 11:
					collision = True
					temp_next_position = self.current_position
			elif action == 2:
				# Left
				temp_next_position = self.current_position - 1
				if self.current_position in self.left_edges:
					collision = True
					temp_next_position = self.current_position

			elif action == 3:
				# Right
				temp_next_position = self.current_position + 1
				if self.current_position in self.right_edges:
					collision = True
					temp_next_position = self.current_position

			# Check for wall collisions
			if (self.current_position, temp_next_position) in self.walls:
				temp_next_position = self.current_position
				collision = True		

			# Check for obstacle collisions
			if temp_next_position == self.obstacle_position:
				temp_next_position = self.current_position
				collision = True

			self.current_position = temp_next_position
			if self.current_position == self.goal_position:
				reward = 10
				done = True

		return self.get_current_state(), reward, done, {} 

	def reset(self):
		while True:
			random_state = self.observation_space.sample()
			if self.validate_state(random_state):
				self.current_position = random_state[0]
				self.goal_position = random_state[1]
				self.obstacle_position = random_state[2]
				break

		return self.get_current_state()

	def reset_seq(self, seq, idx):
		self.current_position = seq[idx][0]
		self.goal_position = seq[idx][1]
		self.obstacle_position = seq[idx][2]
		return self.get_current_state()

	def get_current_state(self):
		return (self.current_position, self.goal_position, self.obstacle_position)

	def validate_state(self, random_state):
		if (random_state[0] != random_state[1]) and (random_state[1] != random_state[2]):
			return True
		return False

	def render(self):
		self.th = threading.Thread(target=self.draw_world)
		self.th.start()

	def draw_world(self):
		self.screen = pygame.display.set_mode([400, 300])
		self.clock = pygame.time.Clock()
		robot_img = pygame.image.load("robot.png").convert()
		default_object_side = 80
		running = True
		centre = [150, 0]
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

			self.screen.fill((255, 255, 255))
			# Draw border
			border_rectange = pygame.Rect(0, 0, 400, 300)
			pygame.draw.rect(self.screen, (0, 0, 0), border_rectange, 10)
			# Draw walls
			pygame.draw.line(self.screen, (140, 0, 0), (100, 100), (200, 100), 10)
			pygame.draw.line(self.screen, (140, 0, 0), (100, 200), (200, 200), 10)
			pygame.draw.line(self.screen, (140, 0, 0), (300, 100), (300, 200), 10)

			# Draw obstacle
			if self.obstacle_position < 12:
				obstacle_centre_coordinates = self.get_coordinates_from_state(self.obstacle_position)
				obstacle_rectangle = pygame.Rect(obstacle_centre_coordinates[0] - (default_object_side / 2), obstacle_centre_coordinates[1] - (default_object_side / 2), 80, 80)
				pygame.draw.rect(self.screen, (0, 0, 0), obstacle_rectangle)

			# Draw goal position
			goal_centre_coordinates = self.get_coordinates_from_state(self.goal_position)
			pygame.draw.circle(self.screen, (1, 140, 18), goal_centre_coordinates, 15)

			# Draw robot
			robot_coordinates = self.get_coordinates_from_state(self.current_position)
			self.screen.blit(robot_img, (robot_coordinates[0] - (default_object_side / 2), robot_coordinates[1] - (default_object_side / 2)))
			
			pygame.display.flip()
			centre[1] = centre[1] + 10
			self.clock.tick(60)

	def get_coordinates_from_state(self, position):
		x_position = (2 * ((position) % 4) + 1) * 50 
		y_position = 100 * int(position / 4) + 50
		return x_position, y_position

	def stop_render(self):
		if self.th:
			self.th.join()
		pygame.quit()

	def __del__(self):
		self.stop_render()

# vw = VecnaWarehouseEnv()
# vw.render()
