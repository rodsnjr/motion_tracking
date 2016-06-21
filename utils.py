import numpy as np
import math as math

# KN for Kernels
# KN_ISOLATED_POINTS = np.array([[-1,-1,-1], [-1, 8, -1], [-1,-1,-1]])


class Tracker(object):
    def __init__(self, positions, index, tracking=True, pixels=None):
        self.positions = positions
        self.index = index
        self.tracking = tracking
        self.pixels = pixels
        self.closest = None

    def middle(self):
        mid = len(self.positions) // 2
        return self.positions[mid]

    def noise(self):
        return len(self.positions) < 1

    def color(self):
        if self.index == 0:
            return 0, 0, 0
        elif self.index == 1:
            return 255, 0, 0
        elif self.index == 2:
            return 0, 255, 0
        elif self.index == 3:
            return 0, 0, 255
        elif self.index == 4:
            return 255, 255, 0
        elif self.index == 5:
            return 255, 0, 255
        elif self.index == 6:
            return 0, 255, 255
        elif self.index == 7:
            return 80, 120, 0
        elif self.index == 8:
            return 120, 0, 80
        elif self.index == 9:
            return 80, 0, 255
        else:
            return 0, 50, 50

    def stop_tracking(self):
        self.tracking = False

    def start_tracking(self):
        self.tracking = True

    def __eq__(self, other):
        self.positions.sort()
        other.positions.sort()
        return self.positions == other.positions

    def __lt__(self, other):
        return self.middle()[0] < other.middle()[0]


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


# Expose all white trackers of the frame
def expose_trackers(frame):
    # Start by slicing the 3 dimension image
    image = frame[:, :, 1]

    # blur the image to remove noise
    # OpenCV Blur, probably faster
    import cv2
    dst = cv2.medianBlur(image, 3)
    # My simple median_blur
    # dst = median_blur(image)

    dst = np_thresh_segmentation(dst)

    return dst


# Expose all white trackers of the frame
def expose_trackers_square(frame):

    dst = np_thresh_segmentation(frame)

    return dst


def median_blur(src, median_size=3):
    dst = np.copy(src)
    medians = list()
    middle = median_size // 2
    y = 0
    i = 0
    while y < dst.shape[0]:
        for x, col in enumerate(dst[y]):
            if i < median_size:
                default = ((y, x), col)
                yi = y - middle
                while yi < y + median_size:
                    if y + yi < dst.shape[0]:
                        medians.append(((y + yi, x), dst[y + yi][x]))
                    else:
                        medians.append(default)
                    yi += 1

                i += 1
            else:
                i = 0
                sorted(medians, key=lambda val: val[1])
                median = medians[median_size // 2][1]
                for item in medians:
                    dst[item[0][0]][item[0][1]] = median
                medians.clear()
        y += median_size

    return dst


# Threshold segmentation using numpy
def np_thresh_segmentation(src, threshold=230, color1=0, color2=255):
    dst = src.copy()
    # Everyone below threshold becomes black
    dst[dst < threshold] = color1
    # Everyone above threshold becomes white
    dst[dst > threshold] = color2
    return dst


# Threshold segmentation, iterates over the image and change the colors
# above the threshold to color1, and below to color2
def thresh_segmentation(src, threshold=230, color1=0, color2=255):
    for row in src:
        for x, col in enumerate(row):
                if col > threshold:
                    row[x] = color1
                else:
                    row[x] = color2
    return src


def find_trackers_1(frame, frames_square_size=0):

    image = expose_trackers(frame)

    trackers = []
    i = 0

    for y, row in enumerate(image):
        for x, col in enumerate(row):
            if col == 255:
                find = tracker_positions(image, (x, y))

                if frames_square_size > 0:
                    tracker = Tracker(find, i, True, get_square(frame, find[0], frames_square_size))
                else:
                    tracker = Tracker(find, i)

                i += 1
                if tracker not in trackers and not tracker.noise():
                    trackers.append(tracker)

    return trackers


def find_trackers(image):
    import distances
    image = expose_trackers(image)

    # slice the images to only intensity dimensions
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

        dist = distances.euclidean_dist((xy[0], xy[1]), (nxt[0], nxt[1]))

        if dist > 10:
            values.append((xy[1], xy[0]))

    return values


def get_square(frame, xy, size):
    sx = xy[0]
    sy = xy[1]
    square = np.zeros((size, size))
    x = 0
    y = 0
    while sy < xy[1] + size:
        while sx < xy[0] + size:
            square[y][x] = frame[sy][sx][1]
            sx += 1
            x += 1
        y += 1
        sy += 1
        sx = xy[0]
        x = 0
    return square


def get_square_positions(frame, xy, size):
    sx = xy[0]
    sy = xy[1]
    square = np.zeros((size, size))
    x = 0
    y = 0
    pos = []

    y_size = xy[1] + size if frame.shape[0] < xy[1] + size else xy[1] + size-1
    x_size = xy[0] + size if frame.shape[1] < xy[0] + size else xy[0] + size-1

    while sy < y_size:
        while sx < x_size:
            pixel = frame[sy][sx][1]
            square[y][x] = pixel
            if pixel >= 230:
                pos.append((sx, sy))
            sx += 1
            x += 1
        y += 1
        sy += 1
        sx = xy[0]
        x = 0

    return square, pos


def sad(p1, p2):
    import distances
    sad = 0
    for row, row1 in zip(p1, p2):
        sad += distances.manhattan_distance(row, row1)
    return sad

# Array, ex [[1,2,3], [4,3,1], [4,4,4]]
# Central point 3
# Multiply by a kernel,
# and return the product of the sum
def convolve_image(image, kernel):
    sum = 0
    for a, b in zip(image.flat, kernel.flat):
        sum += a*b
    return sum