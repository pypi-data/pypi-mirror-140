from gym.envs.registration import register

register(
    id='covid19Attack-v0',
    entry_point='gym_covid19outbreak.envs:Covid19OutbreakEnv',
)