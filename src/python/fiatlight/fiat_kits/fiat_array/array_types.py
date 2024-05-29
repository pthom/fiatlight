"""This module defines several types you can use to annotate your functions.
The array types are defined as NewType instances, which are just aliases for numpy arrays.

All those types will be displayed in the GUI as arrays, with various presentation depending on the array type.

Notes:
    - The easiest way to display an array is to use the `NumericMatrix` type, which is a union of all known types
"""

from typing import Tuple, Any, NewType
import numpy as np
from numpy.typing import NDArray


ShapeDim1 = Tuple[int]
ShapeDim2 = Tuple[int, int]
ShapeDim3 = Tuple[int, int, int]
ShapeDim4 = Tuple[int, int, int, int]
ShapeAny = Tuple[int, ...]


AnyFloat = np.dtype[np.floating[Any]]
AnyInt = np.dtype[np.integer[Any]]


#
# Float Matrices
#
FloatMatrix_Dim1 = NewType("FloatMatrix_Dim1", np.ndarray[ShapeDim1, AnyFloat])
FloatMatrix_Dim1.__doc__ = "synonym for a 1D ndarray of floats"

FloatMatrix_Dim2 = NewType("FloatMatrix_Dim2", np.ndarray[ShapeDim2, AnyFloat])
FloatMatrix_Dim2.__doc__ = "synonym for a 2D ndarray of floats"

FloatMatrix_Dim3 = NewType("FloatMatrix_Dim3", np.ndarray[ShapeDim3, AnyFloat])
FloatMatrix_Dim3.__doc__ = "synonym for a 3D ndarray of floats"

FloatMatrix_Dim4 = NewType("FloatMatrix_Dim4", np.ndarray[ShapeDim4, AnyFloat])
FloatMatrix_Dim4.__doc__ = "synonym for a 4D ndarray of floats"

FloatMatrix = NewType("FloatMatrix", np.ndarray[ShapeAny, AnyFloat])

#
# Int Matrices
#
IntMatrix_Dim1 = NewType("IntMatrix_Dim1", np.ndarray[ShapeDim1, AnyInt])
IntMatrix_Dim1.__doc__ = "synonym for a 1D ndarray of ints"

IntMatrix_Dim2 = NewType("IntMatrix_Dim2", np.ndarray[ShapeDim2, AnyInt])
IntMatrix_Dim2.__doc__ = "synonym for a 2D ndarray of ints"

IntMatrix_Dim3 = NewType("IntMatrix_Dim3", np.ndarray[ShapeDim3, AnyInt])
IntMatrix_Dim3.__doc__ = "synonym for a 3D ndarray of ints"

IntMatrix_Dim4 = NewType("IntMatrix_Dim4", np.ndarray[ShapeDim4, AnyInt])
IntMatrix_Dim4.__doc__ = "synonym for a 4D ndarray of ints"


def present_array(array: NDArray[Any]) -> str:
    # Basic format includes shape and dtype of the array
    description = f"shape{array.shape}, {array.dtype}"
    # Show a summary of the content of the array
    description += "\n"
    description += str(array)
    return description
