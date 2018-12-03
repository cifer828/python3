import numpy as np
from hmmlearn import hmm
import math

states = ["box1", "box2", "box3"]
n_states = len(states)

observations = ["red", "white"]
n_observations = len(observations)

# model = hmm.MultinomialHMM(n_components=n_states, n_iter=20, tol = 0.01)
# x = np.array([[0 ,1, 0, 1]])
# model.fit(x)
# print(math.exp(model.score(x)))

model2 = hmm.GaussianHMM(n_components = 4, covariance_type="full")
# The means of each component
means = np.array([[0.0,  0.0],
                  [0.0, 11.0],
                  [9.0, 10.0],
                  [11.0, -1.0]])
# The covariance of each component
covars = .5 * np.tile(np.identity(2), (4, 1, 1))
observation = np.array([[1,5], [2,6], [3,3]])
model2.fit(observation)
print(math.exp(model2.score(observation)))