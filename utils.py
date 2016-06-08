import numpy as np

PONTOS_ISOLADOS = np.array([[-1,-1,-1], [-1, 8, -1], [-1,-1,-1]])


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
