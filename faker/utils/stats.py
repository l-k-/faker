# coding=utf-8

import bisect
import math
import scipy.stats as stats

from faker.generator import random


def reservoir_sampling(iterator, n=2):
    """
    Reservoir sampling method to generate a random sample of n elements
    from a given element stream (implementation of algorithm R).
    https://en.wikipedia.org/wiki/Reservoir_sampling
    This method is suitable for generating a large number of elements
    because time complexity is dominated by the size of the original stream,
    not the number of elements selected from it.
    """
    res = []

    # initialize the reservoir with the first n elements of the stream
    for _ in range(n):
        res.append(next(iterator))

    # replace elements in the reservoir with gradually decreasing probability
    i = 0

    for value in iterator:
        j = random.randint(0, i)  # important: inclusive range
        if j < n:
            res[j] = value
        i += 1

    return res


class RandomNormalVar(object):
    def __init__(self, mean=0, variance=1, min=None, max=None):
        std_dev = math.sqrt(variance)
        if (min is not None) and (max is not None):
            self.rand_var = stats.truncnorm((min - mean) / std_dev, (max - mean) / std_dev, loc=mean, scale=std_dev)
        else:
            if (min is not None) or (max is not None):
                raise Exception('Must specify either both max and min value, or neither')
            self.rand_var = stats.norm(loc=mean, scale=std_dev)

    def get(self, n=1):
        if n < 2:
            return self.rand_var.rvs(1)[0]
        return list(self.rand_var.rvs(n))

    def get_int(self, n=1):
        if n < 2:
            return int(self.get())
        return [int(round(i)) for i in self.get(n)]
