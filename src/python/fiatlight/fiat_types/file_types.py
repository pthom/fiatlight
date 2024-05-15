from typing import NewType


# FilePath is a synonym of str, but when used as a function parameter,
# it will be displayed as a widget where you can select a file.
FilePath = NewType("FilePath", str)
# FilePath_Save is a synonym of str, but when used as a function parameter,
# it will be displayed as a widget where you can select a file to save to.
FilePath_Save = NewType("FilePath_Save", str)

# With ImagePath, you can select an image file.
ImagePath = NewType("ImagePath", FilePath)
ImagePath_Save = NewType("ImagePath_Save", FilePath_Save)

# With TextPath, you can select a text file.
TextPath = NewType("TextPath", FilePath)
TextPath_Save = NewType("TextPath_Save", FilePath_Save)

# With AudioPath, you can select an audio file.
AudioPath = NewType("AudioPath", FilePath)
AudioPath_Save = NewType("AudioPath_Save", FilePath_Save)

# With VideoPath, you can select a video file.
VideoPath = NewType("VideoPath", FilePath)
VideoPath_Save = NewType("VideoPath_Save", FilePath_Save)
