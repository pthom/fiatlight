# type: ignore

import time

from pedalboard.io import AudioStream
from pedalboard import Reverb


input_devices = AudioStream.input_device_names
output_devices = AudioStream.output_device_names

input_device_name = AudioStream.input_device_names[1]
output_device_name = AudioStream.output_device_names[0]
with AudioStream(input_device_name, output_device_name, allow_feedback=True) as stream:
    # In this block, audio is streaming through `stream`!
    # Audio will be coming out of your speakers at this point.

    # Add plugins to the live audio stream:
    reverb = Reverb()
    stream.plugins.append(reverb)

    # Change plugin properties as the stream is running:
    reverb.wet_level = 1.0

    time.sleep(10)

    # Delete plugins:
    del stream.plugins[0]
