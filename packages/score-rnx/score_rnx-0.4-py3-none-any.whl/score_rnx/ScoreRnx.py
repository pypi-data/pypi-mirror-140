from score_rnx.Pairwisedistances import PairwiseDistances
from score_rnx.Coranking import Coranking
from score_rnx.NXTrusion import NXTrusion
from score_rnx.RDMethod import RDMethod
from numpy import ndarray
import numpy as np
from typing import Any
import matplotlib.pyplot as plt
import random

class ScoreRnxException(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


class ScoreRnx:
    def __init__(self, high_data=None, methods=None) -> None:
        self.__high_data = high_data
        self.__score = 0
        self.__curve = Any
        self.methods_objects = []
        if type(methods) == list:
            self.methods_objects = methods
        else:
            if type(methods) == ndarray:
                self.methods_objects.append(RDMethod("METHOD", methods))

        self.pairwise_distances = PairwiseDistances()
        self.coranking = Coranking()
        self.nx_trusion = NXTrusion()

    def run(self):
        if len(self.methods_objects) > 0:
            if (self.__high_data.any()):
                for i in range(len(self.methods_objects)):
                    if not self.methods_objects[i].state:
                        try:
                            [Ravg, R_NX] = self.nx_scores(self.__high_data, self.methods_objects[i].data)
                            self.__score = Ravg
                            self.__curve = R_NX
                            self.methods_objects[i].score = self.__score
                            self.methods_objects[i].rnx = self.__curve
                            self.methods_objects[i].state = True
                        except Exception as e:
                            raise e
                                # lanzar una excepcion
                    else:
                        print(f"omitiendo nodo: {self.methods_objects[i].name}")
            else:
                raise ScoreRnxException("No haz ingresado los datos en alta dimensión, use ScoreRnx.add_high_data(data: ndarray)")
        else:
            raise ScoreRnxException("No haz agregado métodos al stack, use RDMethod(name, data: ndarray)")

    def get_rnx(self):
        return self.methods_objects

    def nx_scores(self, HD: np.ndarray, LD: np.ndarray):
        try:
            nbr = len(HD)

                # Crear matrices de distancias para datos en alta y baja dimension


            DX = self.pairwise_distances.run(HD)


            DYt = self.pairwise_distances.run(LD)

                # Crear la matriz de coranking con las matrices de distancias
                #   Nota: Tener encuenta que , coranking(DX, DYt) es diferente a    coranking(DYt, DX)


            co = self.coranking.run(DX, DYt)



            [n, x, p, b] = self.nx_trusion.run(co)
                # n => intrusiones, x => extrusiones, b => base aleatoria, p => tasa de rangos perfectamente conservados

            Q_NX = n + x + p  # Calidad general de incrustracion, varia entre 0-1

            B_NX = x - n  # Comportamiento
            LCMC = Q_NX - b  # Meta  criterio de continuidad local
            R_NX = LCMC[0: LCMC.shape[0] - 1] / (1 - b[0: b.shape[0] - 1])  # Convertir q_nx a r_nx

            wgh = np.divide(1, np.arange(1, nbr + 1))  # 1 / np.arange(1, nbr + 1)
            wgh = np.sum(np.divide(wgh, np.sum(wgh)))  # wgh / np.sum(wgh)
            wgh = np.divide(1, np.arange(1, nbr - 1))  # 1 / np.arange(1, nbr - 1)
            wgh = np.divide(wgh, sum(wgh))  # wgh / sum(wgh)
            Ravg = np.sum(wgh * R_NX)

            return [Ravg, R_NX]

        except Exception as e:
            print(e)
            raise e

    def add_method(self, name:str , data:ndarray):

        if len(self.methods_objects) == 6:
            ScoreRnxException("Solo se pueden agregar 6 métodos RD al stack")
            print("Solo se pueden agregar 6 métodos RD al stack")
            return
        self.methods_objects.append(RDMethod(name, data))


    def add_high_data(self, new_high_data: ndarray):
        self.__high_data = new_high_data

    def generate_graph(self):
        if len(self.methods_objects) > 0:
            markers = ['.', '>', 'o']
            bottom, top = 0, 100

            for data_method in self.methods_objects:
                plt.plot(np.arange(len(data_method.rnx)), 100 * data_method.rnx,
                         label=f"{data_method.name}:{round(data_method.score * 100, 1)}%",
                         marker=random.choice(markers),
                         markevery=0.1)

            plt.xscale('log')
            plt.ylim(bottom, top)
            plt.xlabel("K")
            plt.ylabel("100RNX (K)")

            plt.legend(loc='upper left', shadow=True, fontsize='x-large')
            plt.show()
        else:
            ScoreRnxException("Deben haber métodos en el stack para realizar la visualización")
