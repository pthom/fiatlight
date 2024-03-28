# fiatlight: shine light inside your algorithm pipelines


## Installation

### Requirements

- Python 3.10 or higher
-

### Install
### Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```
### Install the requirements:

```bash
pip install -v -r requirements.txt
```

This can take a while (5 minutes), since it will compile imgui_bundle from source.

### Install this library in editable mode:

```bash
pip install -v -e .
```


## Usage & Demos

### Run the demos

Demos list:
```
src/python/fiatlight/demos
├── __init__.py
├── math
│     ├── graph.py                # A demo that displays a binomial distribution as a histogram
│     └── play_versatile_math.py  # A demo on simple math operations
├── base
│     └── play_versatile_word.py  # A demo on words statistics
├── images
│     ├── canny.py                # A demo on the Canny edge detection algorithm
│     ├── oil_paint.py            # A demo on the oil paint effect (requires opencv-contrib-python)
│     ├── toon_edges.py
├── custom_graph
│     ├── demo_custom_graph.py    # A demo on custom graphs (you can add / remove nodes and edges)
│     ├── float_functions.py      # list of available float functions in the custom graph demo
│     ├── image_toy_functions.py  # list of available image functions in the custom graph demo
│     └── opencv_image_functions.py  # list of available opencv image functions in the custom graph demo
├── ai
│     ├── stable_diffusion_xl_initial_download.py  # run this once to download the model
│     ├                                            # from the Hugging Face model hub
│     └── stable_diffusion_xl_wrapper.py           # A wrapper for the Stable Diffusion XL model
│     └── sdxl_toon_edges.py                       # A demo on the Stable Diffusion XL model with fiatlight
└── meme
    └── old_school_meme.py                         # A demo on old school memes
```

### Specific notes for the AI demos

You will need to install the following packages:
```
pip install torch diffusers transformers accelerate
```

You will also need a GPU!!!

Run once this, to download the model from the Hugging Face model hub:

```
python3 src/python/fiatlight/demos/ai/stable_diffusion_xl_initial_download.py
```

If, needed, edit src/python/fiatlight/demos/ai/stable_diffusion_xl_wrapper.py:

```python
# Set the inference device type: By default, MPS on Mac
# SDXL cannot run on a CPU! (RuntimeError: "LayerNormKernelImpl" not implemented for 'Half')
if sys.platform == "darwin":
    _INFERENCE_DEVICE_TYPE = InferenceDeviceType.MPS
else:
    _INFERENCE_DEVICE_TYPE = InferenceDeviceType.CUDA
```
