from typing import TypeAlias, Any
import numpy as np
from numpy.typing import NDArray


ImageUInt8: TypeAlias = NDArray[np.uint8]
ImageFloat: TypeAlias = NDArray[np.floating[Any]]
Image: TypeAlias = NDArray[np.uint8 | np.floating[Any]]
