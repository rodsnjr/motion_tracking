import numpy as np


class AbstractTracker(object):
    def __init__(self, tracking=True):
        self.tracking = tracking

    def stop_tracking(self):
        self.tracking = False

    def start_tracking(self):
        self.tracking = True


class Tracker(AbstractTracker):
    def __init__(self, positions, index, pixels=None):
        super().__init__()
        self.positions = positions
        self.index = index
        self.pixels = pixels
        self.pixel_sum = 0

    def middle(self):
        mid = len(self.positions) // 2
        return self.positions[mid]

    def noise(self):
        return len(self.positions) < 1

    def color(self):
        return color(self.index)

    def binary_pixel_sum(self):
        if self.pixel_sum == 0:
            binary_pixels = self.pixels.copy()
            binary_pixels[binary_pixels == 255] = 1
            for row in binary_pixels:
                self.pixel_sum += sum(row)
        return self.pixel_sum

    def __eq__(self, other):
        self.positions.sort()
        other.positions.sort()
        return self.positions == other.positions

    def __lt__(self, other):
        return self.middle()[0] < other.middle()[0]


class Vector(AbstractTracker):
    def __init__(self, start, direction, size):
        super().__init__()
        self.start = start
        self.direction = direction
        self.size = size
        self.name = ""

    def name_joint(self, name):
        self.name = name


def color(index):
    if index == 0:
        return 0, 0, 0
    elif index == 1:
        return 255, 0, 0
    elif index == 2:
        return 0, 255, 0
    elif index == 3:
        return 0, 0, 255
    elif index == 4:
        return 255, 255, 0
    elif index == 5:
        return 255, 0, 255
    elif index == 6:
        return 0, 255, 255
    elif index == 7:
        return 80, 120, 0
    elif index == 8:
        return 120, 0, 80
    elif index == 9:
        return 80, 0, 255
    else:
        return 0, 50, 50


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
    exposed_frame = image.copy()

    trackers = []
    i = 0

    for y, row in enumerate(image):
        for x, col in enumerate(row):
            if col == 255:
                find = tracker_positions(image, (x, y))

                if frames_square_size > 0:
                    tracker = Tracker(find, i, get_square(exposed_frame, find[0], frames_square_size))
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
    sx = xy[0] - size
    sy = xy[1] - size
    square = np.zeros((size * 2, size * 2))
    x = 0
    y = 0

    y_size = xy[1] + size if frame.shape[0] < xy[1] + size else xy[1] + size-1
    x_size = xy[0] + size if frame.shape[1] < xy[0] + size else xy[0] + size-1

    while sy < y_size:
        while sx < x_size:
            square[y][x] = frame[sy][sx]
            sx += 1
            x += 1
        y += 1
        sy += 1
        sx = xy[0]
        x = 0
    return square


def get_square_positions(frame, xy, size):
    sx = xy[0] - size
    sy = xy[1] - size
    square = np.zeros((size * 2, size * 2))
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


def trackers_vectors(trackers):
    """
    From the trackers of a frame, generate a list of vectors
    pointing towards each trackers pairs
    :param trackers:
    :return:
    """
    import distances

    vectors = []
    """
    size = len(trackers)

    if index + 1 < size:
        direction = trackers[index + 1].middle()
        distance = distances.euclidean_dist(tracker.middle(), direction)
        vectors.append(Vector(tracker.middle(), direction, distance))
    """

    minor_dist = 1000
    closest_tracker = 0
    closed_dist = []

    for index, tracker in enumerate(trackers):
        for tracker1 in trackers:
            if tracker1 == tracker:
                continue
            distance = distances.euclidean_dist(tracker.middle(), tracker1.middle())
            if distance < minor_dist and distance not in closed_dist:
                minor_dist = distance
                closest_tracker = tracker1
        if closest_tracker is not 0:
            closed_dist.append(minor_dist)
            direction = closest_tracker.middle()
            vec = Vector(tracker.middle(), direction, minor_dist)
            vec.tracking = tracker.tracking
            vectors.append(vec)
            minor_dist = 1000
            closest_tracker = 0

    return vectors


def create_vector(tracker1_positions, tracker2_positions):
    """
    From the positions of two tracker1 create a vector
    pointing to both of them
    :param tracker1_positions:
    :param tracker2_positions:
    :return:
    """
    import distances
    if len(tracker1_positions) > 0 and len(tracker2_positions) > 0:
        tracker1_middle = tracker1_positions[len(tracker1_positions)//2]
        tracker2_middle = tracker2_positions[len(tracker2_positions)//2]
        distance = distances.euclidean_dist(tracker1_middle, tracker2_middle)
        return Vector(tracker1_middle, tracker2_middle, distance)

    return None


def find_trackers_vector(vector, frame):
    """
    Look for the trackers that the vector might be linking
    At the start of the vector we know that the trackers are
    between the vector.
    :param vector: the vectors from the previous frame
    :param frame: the current frame
    :return: the positions found from the vectors
    """
    def look_for(xy):
        x_s = xy[0] - 8
        y_s = xy[1] - 8
        end_x = xy[0] + 8
        end_y = xy[1] + 8
        positions = []
        while y_s < end_y:
            while x_s < end_x:
                if frame[y_s][x_s] >= 200:
                    positions.append((x_s, y_s))
                x_s += 1
            y_s += 1
            x_s = xy[0] - 8
        return positions

    positions1 = look_for(vector.start)
    positions2 = look_for(vector.direction)

    return positions1, positions2


def sad(p1, p2):
    import distances
    value = 0

    p1[p1 == 255] = 1
    p2[p2 == 255] = 1

    for row, row1 in zip(p1, p2):
        value += distances.manhattan_distance(row, row1)
    return value

# Array, ex [[1,2,3], [4,3,1], [4,4,4]]
# Central point 3
# Multiply by a kernel,
# and return the product of the sum
def convolve_image(image, kernel):
    sum = 0
    for a, b in zip(image.flat, kernel.flat):
        sum += a*b
    return sum