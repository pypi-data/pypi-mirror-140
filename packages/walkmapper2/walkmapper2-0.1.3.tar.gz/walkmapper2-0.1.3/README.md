# walkmapper

This is a fork of the [original walkmapper package](https://pypi.org/project/walkmapper/) from [sam-olson](https://github.com/sam-olson).

## About

A Python package for plotting and animating your walk/run/bike ride routes.

Install walkmapper using the command line:

```shell
pip install walkmapper
```

You can then run the example script:

```shell
python example.py
```

-------------

The package works by analyzing .gpx files, a common file format used by GPS devices. The [Asics Runkeeper](https://runkeeper.com/) app was used in the development of this package, as it allows you to record GPS locations on your smart phone and export them from your account in the browser.

[Open Street Map](https://www.openstreetmap.org/) is a great resource for grabbing maps to use as backgrounds. Just select "Share" on the map sidebar, size your image with "Set custom dimensions", and download. Rename the photo using the methods described below, allowing the package to properly parse the latitudes and longitudes.

-------------

You can get the latitudes and longitudes of the image you have downloaded using "Share" in OpenStreetMap, by following these steps, as long as you **have not** checked `Set custom dimensions`, and you **have not** panned or zoomed tha map after downloading the image:

1. Paste this into your shell (including the single quote at the end), but do not press enter yet: `python3 -c "import sys;print([round(float(s), 4) for s in sys.argv[1].split('?bbox=')[1].split('&amp')[0].split('%2C')])" '`
2. Select `HTML` under the `Link or HTML` section of the Share panel.
3. Copy the HTML, it should start with `<iframe`, and it should be all in one line, with no line breaks.
4. Then paste the copied HTML into your shell after the single quote, add a single quote at the end, and press Enter.

The output will be in the format `[LowerLeftLon, LowerLeftLat, UpperRightLon, UpperRightLat]`. For example, processing the HTML for a map centered on Portland, OR would output `[-122.7077, 45.4761, -122.5831, 45.5372]`.

-------------

The class `SingleRoute` contains methods for analyzing and plotting a single route. It is also possible to obfuscate your address with a privacy bubble if you plan on sharing on the internet:

```python
from walkmapper.routes import SingleRoute

route = SingleRoute("path/to/your/file.gpx", home_lat=45.0000, home_lon=-122.0000, privacy_bubble_rad=150)
```
From here you can plot the .gpx file over a map image using the `SingleRoute.plot` method. The map image should have the following format: **Description_UpperRightLat_UpperRightLon_LowerLeftLat_LowerLeftLon.png**. If a latitude or longitude is negative, its value should be preceded by an **m**. For example, a map centered on Portland, OR would have the file name: **Portland_45.5372_m122.5831_45.4761_m122.7077.png**. Providing the coordinates of the upper right and lower left corners of the map image in the title allows the plotting functions to parse these values and put appropriate boundaries on the matplotlib images.

The function `map_file_name` in `walkmapper.utils` makes formatting an image title far easier:

```python
from walkmapper.utils import map_file_name

# this function automatically renames the image
map_file_name("images/portland.png", 45.5372, -122.5831, 45.4761, -122.7077, "Portland")

# saves over images/portland.png with images/Portland_45.5372_m122.5831_45.4761_m122.7077.png
```

You can also create a snake animation, where the route is drawn out from start to finish, by using the `SingleRoute.snake_animation` method.

-------------

The class `MultipleRoutes` contains methods for analyzing, plotting, and animating multiple routes:

```python
from walkmapper.routes import MultipleRoutes

# compile all .gpx files in a folder into a list
files = [f"folder/{i}" for i in os.listdir("folder") if i.endswith(".gpx")]

# create instance of MultipleRoutes
routes = MultipleRoutes(files, home_lat=45.0000, home_lon=-122.0000, privacy_bubble_rad=150)
```

Once a `MultipleRoutes` instance is created, you can display the data several ways:
```python
map_file = "Portland_45.5372_m122.5831_45.4761_m122.7077.png"

# plot all routes with map background
routes.basic_plot(map_file)

# plot heat map
routes.heat_map(map_file, n_bins=100, alpha=0.5)

# create .mp4 animation displaying one route after another
routes.basic_route_animation(map_file_path, fps=2, dpi=300)

# create an .mp4 animation that draws out each route sequentially
routes.snake_animation(frame_distance=50, map_file_path=map_file, fps=60, dpi=300)
```

-------------

See `example.py` for an example script, and the directory `example` for example data, maps, and animations.
