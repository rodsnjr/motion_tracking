from math import *


# Calculate the euclidean distance between two tuple points
# Being a (x, y) tuple
def euclidean_dist(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return sqrt(x * x + y * y)


def manhattan_distance(x, y):
    return sum(abs(a-b) for a, b in zip(x, y))