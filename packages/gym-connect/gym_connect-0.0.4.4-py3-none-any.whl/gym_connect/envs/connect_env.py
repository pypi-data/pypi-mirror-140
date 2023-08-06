import gym
import numpy as np


class ConnectEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.action_space = gym.spaces.Discrete(board.width)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(board.height, board.width), dtype=np.int32)

    @property
    def state(self):
        return self.board.board

    def step(self, action):
        try:
            reward = self.board.play(action, self.player)
        except AssertionError:
            reward = -1  # full column!! not allowed
        done = True
        info = {}
        return self.state, reward, done, info

    def reset(self, **kwargs):
        self.board.reset_board()
        return self.state

    def render(self, mode='human'):
        print(self.board)
