import numpy as np
import math as math

#KN for Kernels
KN_ISOLATED_POINTS = np.array([[-1,-1,-1], [-1, 8, -1], [-1,-1,-1]])


class Tracker(object):
    def __init__(self, positions, index):
        self.positions = positions
        self.index = index

    def middle(self):
        mid = len(self.positions) // 2
        return self.positions[mid]

    def color(self):
        if self.index == 0:
            return (0, 0, 0)
        elif self.index == 1:
            return (255, 0, 0)
        elif self.index == 2:
            return (0, 255, 0)
        elif self.index == 3:
            return (0, 0, 255)
        elif self.index == 4:
            return (255,255,0)
        elif self.index == 5:
            return (255,0,255)
        elif self.index == 6:
            return (0,255,255)
        elif self.index == 7:
            return (80,120,0)
        elif self.index == 8:
            return (120,0,80)
        elif self.index == 9:
            return (80,0,255)
        else:
            return (0, 50, 50)

    def __eq__(self, other):
        self.positions.sort()
        other.positions.sort()
        return self.positions == other.positions

# based on flood fill with a queue
# get all the tracker/white positions of the current point
def tracker_positions(frame, xy):
    def add_east(node):
        if node[0] + 1 < frame.shape[1]:
            east = (node[0] + 1, node[1])
            if east not in filled:
                q.put(east)

    def add_west(node):
        if node[0] - 1 > -1:
            west = (node[0] - 1, node[1])
            if west not in filled:
                q.put(west)

    def add_north(node):
        if node[1] + 1 < frame.shape[0]:
            north = (node[0], node[1] + 1)
            if north not in filled:
                q.put(north)

    def add_south(node):
        if node[1] - 1 > -1:
            south = (node[0], node[1] - 1)
            if south not in filled:
                q.put(south)

    import queue

    if frame[xy[1]][xy[0]] != 255:
        return

    q = queue.Queue()
    q.put(xy)
    filled = []
    while not q.empty():
        n = q.get()
        if frame[n[1]][n[0]] == 255:
            # fill the actual point
            filled.append(n)
            # paint the point to a black color
            frame[n[1]][n[0]] = 0

            # generate neighbours
            add_west(n)
            add_east(n)
            add_south(n)
            add_north(n)

    return filled


# Calculate the euclidean distance between two tuple points
# Being a (x, y) tuple
def euclidean_dist(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x * x + y * y)


# Expose all white trackers of the frame
def expose_trackers(frame):
    import cv2
    # blur the image to remove noise
    # substituir por um algoritmo próprio de median blur
    dst = cv2.medianBlur(frame, 3)

    # Threshold segmentation
    # Everyone below 220 becomes black
    dst[dst < 230] = 0
    # Everyone above 220 becomes white
    dst[dst > 230] = 255

    return dst


def find_trackers_1(frame):
    image = expose_trackers(frame)

    # slice the images to only intensity dimensions
    image = image[:, :, 1]
    trackers = []
    i = 0
    for y, row in enumerate(image):
        for x, col in enumerate(row):
            if col == 255:
                find = tracker_positions(image, (x, y))
                tracker = Tracker(find, i)
                i += 1
                if tracker not in trackers:
                    trackers.append(tracker)

    return trackers


def find_trackers(image):
    image = expose_trackers(image)

    #slice the images to only intensity dimensions
    image = image[:, :, 1]
    # Get all white space coordinates
    whites = np.transpose(np.nonzero(image))

    values = []

    for i, xy in enumerate(whites):
        nxt = (0, 0)
        if i + 1 < whites.shape[0]:
            nxt = whites[i+1]
        else:
            nxt = whites[i-1]

        dist = euclidean_dist((xy[0], xy[1]), (nxt [0], nxt [1]))

        if dist > 10:
            values.append((xy[1], xy[0]))

    return values


# Array, ex [[1,2,3], [4,3,1], [4,4,4]]
# Central point 3
# Multiply by a kernel,
# and return the product of the sum
def convolve_image(image, kernel):
    sum = 0
    for a, b in zip(image.flat, kernel.flat):
        sum += a*b
    return sum