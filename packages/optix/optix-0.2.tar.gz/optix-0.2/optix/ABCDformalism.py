import numpy as np
from functools import reduce
from optix.beams import GaussianBeam

class ABCDElement:
    @property
    def length(self) -> float:
        return 0

    def __init__(self, *args) -> None:
        """Accepts A, B, C, D matrix elements or a matrix itself"""
        if len(args) == 4:
            self._A = args[0]
            self._B = args[1]
            self._C = args[2]
            self._D = args[3]
        elif len(args) == 1 and isinstance(args[0], np.ndarray) and self.__is_square_matrix_of_dim(args[0], 2):
            self._A = args[0][0][0]
            self._B = args[0][0][1]
            self._C = args[0][1][0]
            self._D = args[0][1][1]
        else:
            raise ValueError("No matrix definition present in init.")

    def __is_square_matrix_of_dim(self, m: np.ndarray, dim: int):
        return all(len(row) == len(m) for row in m) and len(m) == dim

    @property
    def matrix(self) -> np.ndarray:
        return np.array([[self._A, self._B], [self._C, self._D]])
    
    def act(self, q_param: complex) -> complex:
        nom = self._A * q_param + self._B
        denom = self._C * q_param + self._D
        return nom / denom


class PropagationInMedia(ABCDElement):
    @property
    def length(self) -> float:
        return self._d

    @property
    def n(self) -> float:
        return self._n

    def __init__(self, d, n) -> None:
        self._d = d
        self._n = n
        super().__init__(1, d / n, 0, 1)

class FreeSpace(PropagationInMedia):
    def __init__(self, d: float) -> None:
        super().__init__(d, 1)

class ThinLens(ABCDElement):
    @property
    def f(self):
        return self._f

    def __init__(self, f: float) -> None:
        self._f = f
        super().__init__(1, 0, -1/f, 1)


class RefractionOnSphericalBoundary(ABCDElement):
    @property
    def n1(self):
        return self._n1

    @property
    def n2(self):
        return self._n2

    @property
    def R(self):
        return self._R

    def __init__(self, n1, n2, R) -> None:
        """
        Args:
            n1 (float): Refractive index of the material the ray is propagating from
            n2 (float): Refractive index of the material the ray is propagating to
            R (float): Curviture of the boundary that is positive for convex boundary and negative for concave boundary.
        """
        self._n1 = n1
        self._n2 = n2
        self._R = R
        super().__init__(self.__build_matrix())

    def __build_matrix(self) -> np.ndarray:
        return np.array([
            [1,                                             0],
            [-1*(self.n2 - self.n1) / (self.n2 * self.R),   self.n1 / self.n2]
        ])


class ThickLens(ABCDElement):
    @property
    def length(self) -> float:
        return self._d

    def __init__(self, R1, n, R2, d) -> None:
        """ It is assumed, that the refractive index of free space is 1

        Args:
            R1 (float, positive): Curviture of the first face of the lense
            n (float): Refractive index of the lense
            R2 (float, positive): Curviture of the second face of the lense
            d (float): Thickness of the lense
        """
        self._n = n
        self._R1 = R1
        self._R2 = R2
        self._d = d

        m = self.__build_matrix()
        super().__init__(m)

    def __build_matrix(self):
        first_boundary = RefractionOnSphericalBoundary(1, self._n, self._R1).matrix
        media = PropagationInMedia(self._d, self._n).matrix
        second_boundary = RefractionOnSphericalBoundary(self._n, 1, -self._R2).matrix
        return second_boundary.dot(media.dot(first_boundary))




class OpticalPath:
    """Represents optical path that is created in init function."""
    def __init__(self, *elements: list[ABCDElement]) -> None:
        self._elements = list(elements)

    #TODO: Otestova funkci
    def append(self, element: ABCDElement) -> None:
        self._elements.append(element)

    def __len__(self) -> int:
        return len(self._elements)

    def propagate(self, input: GaussianBeam) -> GaussianBeam:
        q_in = input.cbeam_parameter(0)
        system = self.__build_system()
        q_out = system.act(q_in)
        return GaussianBeam.from_q(input.wavelength, q_out, self.length, input.refractive_index, input.amplitude)

    def __build_system(self) -> ABCDElement:
        system_matrix = reduce(lambda c, b: c.dot(b), [e.matrix for e in reversed(self._elements)])
        return ABCDElement(system_matrix)
    
    @property
    def length(self):
        return reduce(lambda a, b: a +b , [e.length for e in self._elements])

