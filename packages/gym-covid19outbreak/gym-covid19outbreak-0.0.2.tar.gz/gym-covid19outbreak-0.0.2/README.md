# gym-covid19outbreak

<p align="center">
	<img src="docs/sarscov2.jpg" width=80%, height=80% align="center"/><br>
</p>

***covid19outbreak pays tribute to all researchers in African pharmacopoeia, epidemiologists, doctors, nurses, etc. who have fought valiantly against Sars-Cov II*** 

# Table of Contents

1. [Game-presentation](#Game-presentation)
	1. [Introduction](#Introduction)
	2. [Object of the game](#Object-of-the-game)
	3. [Gameplay](#Gameplay)
2. [Rules](#Rules)
	1. [Starting-positions](#Starting-positions)
	2. [moves](#moves)

3. [Environments](#Environments)
	1. [Episode termination](#Episode-termination)
	2. [Observations](#Observations)
	3. [Actions](#Actions)
	4. [Reward](#Reward)

4.	[Installation](#Installation)
3.	[Usage](#Usage)
	1. [Citation](#Citation)
   	2. [Contribute](#Contribute)


# Game-presentation

https://en.wikipedia.org/wiki/Covid19_pandemic

## Introduction

It was on March 11, 2020 that the World Health Organisation (WHO) declared the coronavirus pandemic. During this same period, Italy was the main focus and then the USA took the place. In March 17, 2020 many countries in Africa was closed borders and banning flights from elsewhere.  **Covid19outbreak** is a single-player simulator strategy board game. Player start with 10 lifes and priority is to save all patients. 

## Object of the game

By looking for the way to save patient, player must avoid Sars-Cov II and keep its life. If he save all patients player wins otherwise the game begins very difficult.

## Gameplay

During the game, player must be stratege by finding a plant and avoiding Sars-CovII in their way. If player touches viruse and have a plant, he kill viruse. If player touches viruse without a plant, he looses some percentage of life and he contaminates environment. Patient is  unstable due to collision with viruses. 

# Rule

## Starting-positions

Player starts in bottom of screen with 5 virus, 7 patients and 5 plants.

## Moves

Players can move following theses directions:

- **Up, Left, Right, Down**

- **LeftTop, RightTop,  LeftBottom, RightBottom, NOOP**

# Environment

## Observation

The observation is a numpy arrays of size (480, 520, 3). This arrays is a dtype=np.uint8 value in the [0, 255] range. You can see image below. 

<p align="center">
	<img src="docs/covid19outbreak.gif" width=70% height=70% align="center"/><br>
</p>
<em>gym-covid19outbreak</em>

## Actions

The moves is the 8 directions mentioned before. Player can go everywhere in the screen to reach his objective.
<p align="center">
	<img src="docs/boy.png" width=5% height=5% align="center"/><br>
</p>
<em>agent can move Up, Left, Right, Down, LeftTop, RightTop,  LeftBottom, RightBottom in the screen.</em>

## Reward

Player have four rewards:

1. If boy hits a plant: **reward = 1 + number of plant collected + 0.01** during an episode.

2. If boy saves a patient: **reward = 1 + number of patient saved** during an episode.

3. If boy hits Sars-Cov II with a plant: **reward = number of plant + 0.01 - 2**, 0.01 is a decay life.

4. If boy hits Sars-Cov II without having a plant: **reward = - 3 - 0.01**.

In beginning of game, player have 10 lifes by hitting the viruse without a plant, life = life - 1.

Do not forget that player can contaminate environment by creating two viruses each time after infection.

## Episode termination

The episode is terminated if agent looses all its life or saves all patients or kills all viruses.


## Requirement

- python 3.7+
- OpenAI gym
- Numpy
- Pygame
- PIL
- Keras or Tensorflow or Pytorch 

Dependencies can be installed with `pip` or `conda`

# Using pip


```
$ git clone https://github.com/batalong123/gym-covid19outbreak.git
$ cd gym-covid19outbreak
$ pip install -e .
```

or 

```
pip install gym-covid19outbreak
```

# Usage

```python
import gym
import gym_covid19outbreak

env = gym.make('covid19Attack-v0')
MAX_EPISODE = 10

for i in range(MAX_EPISODE):

	env.reset()
	done = False
	total_reward = 0

	while not done:

		action = env.action_space.sample()

		obs, reward, done, info = env.step(action)
		total_reward += reward
		env.render()

	print(f'Episode: {i+1}/{MAX_EPISODE}', f'reward: {total_reward}', f'done: {done}')

env.close()
```

## Citation

Bibtex if you want to cite this repository in your publications:

```
@misc{gym_covid19outbreak,
  author = {Massock Batalong M.B.},
  title = {Covid19outbreak Environments for OpenAI Gym},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/batalong123/gym-covid19outbreak}},
}
```

## Contribute

Feel free to contribute to this project. You can fork this repository and implement whatever you want. Alternatively, open a new issue in case you need help or want to have a feature added.

contact: lumierebatalong@gmail.com
