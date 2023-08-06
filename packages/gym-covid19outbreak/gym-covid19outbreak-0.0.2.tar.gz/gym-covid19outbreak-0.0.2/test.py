import gym
import gym_covid19outbreak

env = gym.make('covid19Attack-v0')



for i in range(10):
	env.reset()
	done = False
	total_reward = 0

	while not done:

		action = env.action_space.sample()

		obs, reward, done, info = env.step(action)
		total_reward += reward
		env.render()

	print(f'Episode: {i+1}/{10}', f'reward: {total_reward}', f'done: {done}')

env.close()