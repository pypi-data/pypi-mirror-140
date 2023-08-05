"""Implements principal rotation vector (PRV)."""

from typing import Optional

import numpy as np

import attlesnake.parameter.base as base
import attlesnake.parameter.quaternion as quaternion


class PRV(base.BaseAttitudeParameter):
    """Principal rotation vector (PRV)."""

    def __init__(
        self,
        angle: Optional[float] = None,
        e1: Optional[float] = None,
        e2: Optional[float] = None,
        e3: Optional[float] = None,
    ) -> None:
        self.angle = angle
        self.e1 = e1
        self.e2 = e2
        self.e3 = e3

    def _apply_constraint(self) -> None:
        self.e1, self.e1, self.e3 = self.unit_vector/np.linalg.norm(self.unit_vector)

    @property
    def phi(self) -> float:
        return self.angle

    @property
    def unit_vector(self) -> np.ndarray:
        return np.array([self.e1, self.e2, self.e3])

    @property
    def scaled_vector(self) -> np.ndarray:
        return self.angle*self.unit_vector

    @classmethod
    def from_quaternion(cls, q: "quaternion.Quaternion") -> "PRV":
        angle = 2*np.arccos(q.s)
        e1 = np.sin(q.v1/2)
        e2 = np.sin(q.v2/2)
        e3 = np.sin(q.v3/2)
        prv = cls(angle, e1, e2, e3)
        prv._apply_constraint()
        return prv
