import cv2
import math as math
import numpy as np

cap = cv2.VideoCapture('VideoBike.avi')


def euclidian_dist(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x * x + y * y)


def expose_trackers(frame):
    # blur the image to remove noise
    # substituir por um algoritmo próprio de mediana
    dst = cv2.medianBlur(frame, 3)

    # Threshold segmentation
    # Everyone below 220 becomes black
    dst[dst < 220] = 0
    # Everyone above 220 becomes white
    dst[dst > 220] = 255

    return dst


def find_trackers(image):
    image = expose_trackers(image)

    # Get all white space coordinates
    image = image[:, :, 1]
    whites = np.transpose(np.nonzero(image))
    # whites.sort(axis=1)
    valores = []

    for i, xy in enumerate(whites):
        # print(xy)
        # proximo valor na base
        prox = (0, 0)
        if i + 1 < whites.shape[0]:
            prox = whites[i+1]
        else:
            prox = whites[i-1]

        dist = euclidian_dist((xy[0], xy[1]), (prox[0], prox[1]))

        if dist > 25:
            print((xy[1], xy[0]))
            valores.append((xy[1], xy[0]))

    return valores

"""
ret, frame = cap.read()
white_spaces = find_trackers(frame)

for xy in white_spaces:
    frame = cv2.circle(frame, xy, 10, (255, 0, 255), 1)

cv2.imshow('frame', frame)

while cv2.waitKey(1) & 0xFF != ord('q'):
    cv2.imshow('frame', frame)

"""

while cap.isOpened():
    # Keep reading the frames
    ret, frame = cap.read()

    if ret:
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # segmentation, thresh = cv2.threshold(frame, 10, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        white_spaces = find_trackers(frame)

        for xy in white_spaces:
           frame = cv2.circle(frame, xy, 10, (255, 0, 255), 1)

        cv2.imshow('frame', frame)
    else:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()