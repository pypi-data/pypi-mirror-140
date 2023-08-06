from gym.envs.registration import register

register(
    id='sarscov2-v0',
    entry_point='gym_killerviruses.envs:KillerVirusesEnv',
)