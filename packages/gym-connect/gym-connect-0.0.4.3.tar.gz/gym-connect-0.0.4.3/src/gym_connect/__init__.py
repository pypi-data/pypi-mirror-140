from gym.envs.registration import register

register(
    id='Connect-v0',
    entry_point='gym_connect.envs:ConnectEnv',
)
