import math


def chebyshev(goals, values):
  return  max(abs(goals[index]-value) for index, value in enumerate(values))

def d2h(goals, values):
  return  math.sqrt(sum((goals[index]-value)**2 for index, value in enumerate(values))/len(values))