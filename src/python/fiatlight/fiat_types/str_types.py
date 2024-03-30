from typing import NewType

# FilePath is a synonym of str, but when used as a function parameter,
# it will be displayed as a widget where you can select a file.
FilePath = NewType("FilePath", str)

# With ImagePath, you can select an image file.
ImagePath = NewType("ImagePath", str)

# With TextPath, you can select a text file.
TextPath = NewType("TextPath", str)
