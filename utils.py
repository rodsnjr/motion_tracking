import numpy as np
import math as math

PONTOS_ISOLADOS = np.array([[-1,-1,-1], [-1, 8, -1], [-1,-1,-1]])


def euclidian_dist(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return math.sqrt(x * x + y * y)


def expose_trackers(frame):
    import cv2
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

# Array de espaço, ex [[1,2,3], [4,3,1], [4,4,4]]
# Sendo o ponto central 3
# Multiplica e soma todos os pontos
def magnitude_convolucao(ponto, convolucao):
    sum = 0
    for a, b in zip(ponto.flat, convolucao.flat):
        sum += a*b
    return sum


def segmenta_blob(np_array, x, y):
    s_x = x - 1
    s_y = y - 1

    tam_x = s_x + 3
    tam_y = s_y + 3

    em_x = 0
    em_y = 0

    soma = 0

    while s_y < tam_y:
        while s_x < tam_x:
            soma += np_array[s_y][s_x] * PONTOS_ISOLADOS[em_y][em_x]
            em_x += 1
            s_x += 1

        em_x = 0
        s_x = x - 1

        em_y += 1
        s_y += 1

    if soma < 200:
        np_array[x][y] = 0

# pega um pedaço menor ao redor do ponto
# em um array
# o tamanho w e h para o pedaço
def small_blob(np_array, x, y, w, h):
    s_x = x - 1
    s_y = y - 1

    tam_x = s_x + w
    tam_y = s_y + h

    blob = np.empty([w, h])

    em_x = 0
    em_y = 0
    while s_y < tam_y:
        while s_x < tam_x:
            blob[em_y][em_x] = np_array[s_y][s_x]
            em_x += 1
            s_x += 1

        em_x = 0
        s_x = x - 1

        em_y += 1
        s_y += 1

    return blob
