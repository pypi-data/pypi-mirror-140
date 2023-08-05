"""
Implements Classical and Modified Rodrigues Parameters
(CRPs and MRPs).
"""

from typing import Optional
import numpy as np

import attlesnake.parameter.base as base
import attlesnake.parameter.direction_cosine_matrix as direction_cosine_matrix
import attlesnake.parameter.quaternion as quaternion
import attlesnake.parameter.principal_rotation_vector as principal_rotation_vector


class CRP(base.BaseAttitudeParameter):
    """Classical Rodrigues Parameter (CRP)."""

    def __init__(
        self,
        r1: Optional[float] = None,
        r2: Optional[float] = None,
        r3: Optional[float] = None
    ) -> None:
        """Initialize the CRP."""
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3

    def __repr__(self) -> str:
        return "(r1, r2, r3) = " + np.array_str(self.vector, precision=4)

    def __mul__(self, other) -> "CRP":
        return self @ other

    def __matmul__(self, other: "CRP") -> "CRP":
        """
        CRP composition. Conventionally, other is applied first,
        followed by self.
        """
        coeff = 1/(1 - np.inner(self.vector, other.vector))
        r1, r2, r3 = coeff*(
            self.vector + other.vector - np.cross(self.vector, other.vector)
        )
        return CRP(r1, r2, r3)

    def __sub__(self, other: "CRP") -> "CRP":
        """Relative attitude of self with respect to other."""
        coeff = 1/(1 + np.inner(self.vector, other.vector))
        r1, r2, r3 = coeff*(
            self.vector - other.vector + np.cross(self.vector, other.vector)
        )
        return CRP(r1, r2, r3)

    @property
    def vector(self) -> np.ndarray:
        return np.array([self.r1, self.r2, self.r3])

    @classmethod
    def from_dcm(cls, dcm: "direction_cosine_matrix.DCM") -> "CRP":
        C = dcm.array
        coeff = 1/(np.trace(C) + 1)
        r1, r2, r3 = coeff*np.array(
            [
                C[1,2] - C[2,1],
                C[2,0] - C[0,2],
                C[0,1] - C[1,0]
            ]
        )
        return cls(r1, r2, r3)

    @classmethod
    def from_quaternion(cls, quaternion: "quaternion.Quaternion") -> "CRP":
        r1 = quaternion.v1/quaternion.s
        r2 = quaternion.v2/quaternion.s
        r3 = quaternion.v3/quaternion.s
        return cls(r1, r2, r3)

    @classmethod
    def from_prv(cls, prv: "principal_rotation_vector.PRV") -> "CRP":
        r1, r2, r3 = np.tan(prv.angle)*prv.unit_vector
        return cls(r1, r2, r3)

    def inverse(self) -> "CRP":
        """The CRP parameterizing the opposite attitude."""
        return CRP(*(-1*self.vector))
