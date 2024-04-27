from typing import NewType

# FilePath is a synonym of str, but when used as a function parameter,
# it will be displayed as a widget where you can select a file.
FilePath = NewType("FilePath", str)

# With ImagePath, you can select an image file.
ImagePath = NewType("ImagePath", str)

# With TextPath, you can select a text file.
TextPath = NewType("TextPath", str)

# With AudioPath, you can select an audio file.
AudioPath = NewType("AudioPath", str)

# With VideoPath, you can select a video file.
VideoPath = NewType("VideoPath", str)

# A string that can be multiline (displayed as a textarea in the GUI)
StrMultiline = NewType("StrMultiline", str)

# A string used as a prompt (displayed as a textarea in the GUI)
# Mainly used for AI text and image generation models.
Prompt = NewType("Prompt", str)
