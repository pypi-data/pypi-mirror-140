import functools
import math
from abc import ABC, abstractmethod
from typing import Union, List

import numpy as np
from numpy import linalg
from scipy.linalg import sqrtm


class CriticalSurfaceBrownianMotion(ABC):
    """
        alpha: significance level (look at quantiles of order alpha/2 and 1 − alpha/2)
    """

    def __init__(self,
                 N: int,
                 alpha: float = 0.05,
                 k: int = 1,
                 chi2_trials: int = 100000):
        self.N = N
        self.alpha = alpha
        self.k = k
        np.random.seed(6)
        self.chi2 = np.random.chisquare(df=1, size=(self.N, chi2_trials))

    @functools.cached_property
    def matrix_A_k(self):
        A_k = np.zeros((self.N, self.N))
        for i in range(self.N):
            for j in range(self.N):
                if abs(i - j) == self.k:
                    A_k[i, j] = 0.5 / (self.N - self.k)
                # elif i == j:
                #     A_k[i, j] = 1 / self.N
        return A_k

    @abstractmethod
    def _autocovariance_matrix(self, sig2: float, H: Union[List[float], np.ndarray, float]):
        pass

    def _eigenvalues(self, sig2: float, H: Union[List[float], np.ndarray, float]):
        Sigma: np.ndarray = self._autocovariance_matrix(sig2=sig2, H=H)
        square_root_Sigma: np.ndarray = sqrtm(Sigma)
        A_k = self.matrix_A_k
        mat = square_root_Sigma.dot(A_k)
        mat = mat.dot(square_root_Sigma)
        eigenvalues, _ = linalg.eig(mat)
        return eigenvalues

    def _generalized_chi2(self, sig2, H: Union[List[float], np.ndarray, float]):
        eigenvalues = self._eigenvalues(sig2=sig2, H=H)
        stat = np.array(eigenvalues.dot(self.chi2))
        return stat

    def quantile(self, sig2, H: Union[List[float], np.ndarray, float]):
        dist = self._generalized_chi2(sig2=sig2, H=H)
        quantile = [0, 0]
        quantile[0] = np.percentile(a=dist, q=100 * self.alpha / 2)
        quantile[1] = np.percentile(a=dist, q=100 - 100 * self.alpha / 2)
        return quantile


class CriticalSurfaceFBM(CriticalSurfaceBrownianMotion):
    """
        Source paper: Michał Balcerek, Krzysztof Burnecki. (2020)
                      Testing of fractional Brownian motion in a noisy environment.
                      Chaos, Solitons & Fractals, Volume 140, 110097.
                      https://doi.org/10.1016/j.chaos.2020.110097
    """

    def _r_k(self, k: int, H: float):
        twoH = 2 * H
        return 0.5 * ((k + 1) ** twoH + abs(k - 1) ** twoH - 2 * k ** twoH)

    def _r_M_k(self, k: int, sig2: float, H: float):
        r_k = self._r_k(k=k, H=H)
        if k == 0:
            r_M_k = r_k + 2 * sig2
        elif k == 1:
            r_M_k = r_k - sig2
        else:
            r_M_k = r_k
        return r_M_k

    def _autocovariance_matrix(self, sig2: float, H: float):
        if not isinstance(H, (float, int)) or H > 1 or H < 0:
            raise ValueError(f'H is {H}, but it needs to be a float in [0,1].')
        Sigma = np.zeros((self.N, self.N))
        for i in range(self.N):
            for j in range(self.N):
                k = abs(i - j)
                Sigma[i, j] = self._r_M_k(k=k, sig2=sig2, H=H)
        return Sigma


class CriticalSurfaceMFBM(CriticalSurfaceBrownianMotion):
    """
        Source paper: Balcerek, Michał, and Krzysztof Burnecki. (2020) Testing of Multifractional Brownian Motion.
                          Entropy 22, no. 12: 1403.
                          https://doi.org/10.3390/e22121403
    """

    @functools.lru_cache(maxsize=128)
    def _D(self, alpha):
        gam_ = math.gamma(alpha + 1)
        sin_ = math.sin(math.pi * alpha / 2)
        return math.pi / gam_ / sin_

    def _autocovariance_matrix(self, sig2, H: Union[List, np.ndarray]):
        if isinstance(H, (float, int)):
            raise ValueError('H needs to be a list for MBM.')
        Sigma = np.zeros((self.N, self.N))
        for i in range(self.N):
            for j in range(self.N):
                h = H[i] + H[j]
                D = self._D(alpha=h)
                Sigma[i, j] = sig2 * D * ((i + 1) ** h + (j + 1) ** h - abs(i - j) ** h)
        return Sigma
