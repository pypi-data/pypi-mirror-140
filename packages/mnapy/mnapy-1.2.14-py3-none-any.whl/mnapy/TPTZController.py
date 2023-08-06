from typing import List

import numpy as np


class TPTZController:
    def __init__(self, tptz_buffer):
        self.buffer = tptz_buffer
        self.x = np.zeros(2, dtype=np.float64)
        self.y = np.zeros(2, dtype=np.float64)
        self.x[0] = 0
        self.x[1] = 0
        self.y[0] = 0
        self.y[1] = 0
        self.a1 = 0
        self.a2 = 1
        self.b0 = 2
        self.b1 = 3
        self.b2 = 4
        self.n_1 = 0
        self.n_2 = 1
        self.center = 0
        self._y = 0

    def get_output(self, input_error: float) -> float:
        None
        return self._2p2z(input_error)

    def set_initial(self, setter: float) -> None:
        None
        self.y[self.n_1] = setter
        self.y[self.n_2] = setter

    def _2p2z(self, _x: float) -> float:
        None
        self.center = (
                _x * self.buffer[self.b0]
                + self.buffer[self.b1] * self.x[self.n_1]
                + self.buffer[self.b2] * self.x[self.n_2]
        )
        self._y = (
                self.center
                - self.buffer[self.a1] * self.y[self.n_1]
                - self.buffer[self.a2] * self.y[self.n_2]
        )
        self.x[self.n_2] = self.x[self.n_1]
        self.x[self.n_1] = _x
        self.y[self.n_2] = self.y[self.n_1]
        self.y[self.n_1] = self._y
        return self._y

    def set_tptz_coefficients(self, tptz_buffer: List[float]) -> None:
        None
        self.buffer = tptz_buffer
