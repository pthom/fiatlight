fiat_image: advanced image widget
=================================

Fiatlight provides an advanced image viewer and analyzer which enables to zoom, pan, look at pixel values and sync the zoom across images.

Example
-------

```python
from fiatlight.fiat_kits.fiat_image import fiat_image_attrs_demo
fiat_image_attrs_demo.main()
```

> * In the "show_image" output, the options panel was opened
> * The "show_image_channels" output shows the image channels, and it zoom/pan is linked to "show_image"
> * The "show_image_different_zoom_key" image has a different zoom key, and the zoom/pan is not linked to "show_image".
    >   It also zoomed at a high-level, so that pixel values are displayed.
> * the "show_image_only_display" image is displayed, and cannot be zoomed or panned (the widget may be resized however)




Fiat attributes available for the ImageWithGui widget
-------------------------------------------------------

The image widget provided with fiat_image is extremely customizable. Here is a list of all the possible customizations options:

```
%%bash
fiatlight gui ImageWithGui
```


Image types
-----------
Fiatlight provides several synonyms for Numpy arrays that denote different types of images. Each of these types will be displayed by the image widget.

````python
import fiatlight
from fiatlight.fiat_notebook import look_at_code
%look_at_python_file fiat_kits/fiat_image/image_types.py
````

Source code for the example
---------------------------

```python
%look_at_python_file fiat_kits/fiat_image/fiat_image_attrs_demo.py
```

