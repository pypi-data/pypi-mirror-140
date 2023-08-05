"""Implements Direction Cosine Matrix (DCM) attitude parameter."""

from typing import Optional

import numpy as np

import attlesnake.parameter.base as base
import attlesnake.parameter.euler_angle as euler_angle
import attlesnake.parameter.quaternion as quaternion
import attlesnake.parameter.rodrigues as rodrigues
import attlesnake.util as util


class DCM(base.BaseAttitudeParameter):
    """Direction Cosine Matrix (DCM)."""
    def __init__(
        self, array_3x3: Optional[float] = None) -> None:
        if array_3x3 is None:
            self.array = np.eye(3)
        else:
            if not np.shape(array_3x3) == (3, 3):
                raise ValueError("DCM must be initialized with a 3x3 array of floats")
            # TODO: add validation that given array represents a valid DCM
            # (i.e. that columns are orthonormal with determinant +1)
            self.array = np.array(array_3x3)

    def __matmul__(self, other: "DCM") -> "DCM":
        """DCM composition (real matrix multiplication)."""
        return DCM(self.array @ other.array)

    def __repr__(self):
        return np.array_str(self.array, precision=4)

    def inverse(self) -> "DCM":
        """
        Return the inverse DCM, without modifying the
        original DCM.
        """
        return DCM(np.transpose(self.array))

    @classmethod
    def from_ea321(
        cls, ea_321: "euler_angle.EulerAngle321"
    ) -> None:
        """
        Initialize the DCM from a 3-2-1 set of Euler
        angles, where the angles are expressed in radians.
        3-2-1: a1*yaw, a2*pitch, a3*roll.
        """
        a1, a2, a3 = ea_321.array
        array = np.array([
            [
                np.cos(a2)*np.cos(a1),
                np.cos(a2)*np.sin(a1),
                -np.sin(a2)
            ],
            [
                np.sin(a3)*np.sin(a2)*np.cos(a1) - np.cos(a3)*np.sin(a1),
                np.sin(a3)*np.sin(a2)*np.sin(a1) + np.cos(a3)*np.cos(a1),
                np.sin(a3)*np.cos(a2)
            ],
            [
                np.cos(a3)*np.sin(a2)*np.cos(a1) + np.sin(a3)*np.sin(a1),
                np.cos(a3)*np.sin(a2)*np.sin(a1) - np.sin(a3)*np.cos(a1),
                np.cos(a3)*np.cos(a2)
            ]
        ])
        return cls(array)

    @classmethod
    def from_ea313(
        cls, ea_313: "euler_angle.EulerAngle313"
    ) -> "DCM":
        """
        Initialize the DCM from a 3-1-3 set of Euler
        angles, where the angles are expressed in radians.
        3-1-3: a1*yaw, a2*roll, a3*yaw.
        """
        a1, a2, a3 = ea_313.array
        array = np.array([
            [
                np.cos(a3)*np.cos(a1) - np.sin(a3)*np.cos(a2)*np.sin(a1),
                np.cos(a3)*np.sin(a1) + np.sin(a3)*np.cos(a2)*np.cos(a1),
                np.sin(a3)*np.sin(a2)
            ],
            [
                -np.sin(a3)*np.cos(a1) - np.cos(a3)*np.cos(a2)*np.sin(a1),
                -np.sin(a3)*np.sin(a1) + np.cos(a3)*np.cos(a2)*np.cos(a1),
                np.cos(a3)*np.sin(a2)
            ],
            [
                np.sin(a2)*np.sin(a1),
                -np.sin(a2)*np.cos(a1),
                np.cos(a2)
            ]
        ])
        return cls(array)

    @classmethod
    def from_quaternion(cls, q: "quaternion.Quaternion") -> "DCM":
        array = np.array([
            [
                q.s**2 + q.v1**2 - q.v2**2 - q.v3**2,
                2*(q.v1*q.v2 + q.s*q.v3),
                2*(q.v1*q.v3 - q.s*q.v2)
            ],
            [
                2*(q.v1*q.v2 - q.s*q.v3),
                q.s**2 - q.v1**2 + q.v2**2 - q.v3**2,
                2*(q.v2*q.v3 + q.s*q.v1)
            ],
            [
                2*(q.v1*q.v3 + q.s*q.v2),
                2*(q.v2*q.v3 - q.s*q.v1),
                q.s**2 - q.v1**2 - q.v2**2 + q.v3**2
            ]
        ])
        return cls(array)

    @classmethod
    def from_crp(cls, crp: "rodrigues.CRP") -> "DCM":
        coeff = 1/(1 + np.inner(crp.vector, crp.vector))
        C = coeff*(
            (1 - np.inner(crp.vector, crp.vector))*np.eye(3)
            + 2*np.outer(crp.vector, crp.vector)
            - 2*util.cross_matrix(crp.vector)
        )
        return cls(C)
