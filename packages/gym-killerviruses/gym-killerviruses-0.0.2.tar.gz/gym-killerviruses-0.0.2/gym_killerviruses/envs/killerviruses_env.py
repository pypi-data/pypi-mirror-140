import gym 
from gym import spaces
from gym_killerviruses.envs.pandemic import Covid19Outbreak
import numpy as np

SPEED_PLAYER = 5.0

class KillerVirusesEnv(gym.Env):

	metadata = {"render.modes": ['human']}

	def __init__(self):
		super(KillerVirusesEnv, self).__init__()

		self.game = Covid19Outbreak()

		self.size = self.game.size

		self.action_space = spaces.Discrete(9)
		self.observation_space = spaces.Box(low=0, high=255,
			shape=(self.size[0], self.size[1], 3), dtype=np.uint8)


	def step(self, action):

		if action == 0:
			self.game.player.velocity = [0, 0]
			

		elif action == 1:
			self.game.player.velocity = [SPEED_PLAYER, 0]
			

		elif action == 2:
			self.game.player.velocity = [-SPEED_PLAYER, 0]
			

		elif action == 3:
			self.game.player.velocity = [0, SPEED_PLAYER]
			

		elif action == 4:
			self.game.player.velocity = [0, -SPEED_PLAYER]
			
		elif action == 5:
			self.game.player.velocity = [-SPEED_PLAYER, SPEED_PLAYER]
			

		elif action == 6:
			self.game.player.velocity = [SPEED_PLAYER, SPEED_PLAYER]
			

		elif action == 7:
			self.game.player.velocity = [SPEED_PLAYER, -SPEED_PLAYER]
			

		else:
			self.game.player.velocity = [-SPEED_PLAYER, -SPEED_PLAYER]

		#game.update(action)
		done = self.game.is_over
		reward = self.game.getReward()
		observation = self.game.getObservation()
		info = {}
		return observation, reward, done, info


	def reset(self):
		self.game.reset_game()
		return self.game.getObservation()

	def render(self, mode="human"):
		return self.game.update(mode)

	def close(self):
		self.game.quit_game()
