from typing import NewType

# FilePath is a synonym of str, but when used as a function parameter,
# it will be displayed as a widget where you can select a file.
FilePath = NewType("FilePath", str)
# FilePath_Save is a synonym of str, but when used as a function parameter,
# it will be displayed as a widget where you can select a file to save to.
FilePath_Save = NewType("FilePath_Save", str)

# With ImagePath, you can select an image file.
ImagePath = NewType("ImagePath", str)
ImagePath_Save = NewType("ImagePath_Save", str)

# With TextPath, you can select a text file.
TextPath = NewType("TextPath", str)
TextPath_Save = NewType("TextPath_Save", str)

# With AudioPath, you can select an audio file.
AudioPath = NewType("AudioPath", str)
AudioPath_Save = NewType("AudioPath_Save", str)

# With VideoPath, you can select a video file.
VideoPath = NewType("VideoPath", str)
VideoPath_Save = NewType("VideoPath_Save", str)
