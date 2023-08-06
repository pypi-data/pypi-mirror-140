from gym.envs.registration import register

register(
    id='Connect-v0',
    entry_point='src.gym_connect.envs:ConnectEnv',
)
