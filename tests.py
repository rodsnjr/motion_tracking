import unittest
import utils as ut
import numpy as np

class TestUtils(unittest.TestCase):
    def teste_magnitude_convolucao(self):
        teste = np.array([[2, 2, 2], [2, 8, 2], [2, 2, 2]])
        self.assertEquals(ut.magnitude_convolucao(teste, ut.PONTOS_ISOLADOS), 48)
