fiat_image: advanced image widget
=================================

Image types
-----------
Fiatlight provides several synonyms for Numpy arrays that denote different types of images. Each of these types will be displayed by the image widget.


````python
import fiatlight
%look_at_python_code fiatlight.fiat_kits.fiat_image.fiat_image_custom_attrs_demo
````



Custom attributes available for the image widget
------------------------------------------------

The image widget provided with fiat_image is extremely customizable. Here is a list of all the possible customizations options:
````python
from fiatlight import fiat_image

print(fiat_image.image_gui.image_custom_attributes_documentation())
````


Example
-------

```python
%look_at_python_code fiatlight.fiat_kits.fiat_image.fiat_image_custom_attrs_demo
```

The example above leads to the following output:
```python
from fiatlight.fiat_kits.fiat_image import fiat_image_custom_attrs_demo
fiat_image_custom_attrs_demo.main()
```

> * In the "show_image" output, the options panel was opened
> * The "show_image_channels" output shows the image channels, and it zoom/pan is linked to "show_image"
> * The "show_image_different_zoom_key" image has a different zoom key, and the zoom/pan is not linked to "show_image".
>   It also zoomed at a high-level, so that pixel values are displayed.
> * the "show_image_only_display" image is displayed, and cannot be zoomed or panned (the widget may be resized however)