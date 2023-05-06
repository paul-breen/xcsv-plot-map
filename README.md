# xcsv-plot-map

xcsv-plot-map is a subpackage of [xcsv](https://github.com/paul-breen/xcsv).  It's main purpose is to provide a simple CLI for plotting extended CSV (XCSV) files, and locating the data on a map, given an extended header section with geographical coordinates.  These will typically detail where the data were acquired.  It inherits from the [xcsv-plot](https://pypi.org/project/xcsv-plot) subpackage of xcsv.

## Install

The package can be installed from PyPI:

```bash
$ pip install xcsv-plot-map
```

## Notes on installing Cartopy

xcsv-plot-map has a dependency on Cartopy.  In turn, Cartopy requires the Proj library.  If you find that you can't install Cartopy because the version of the Proj library on your system is too old, then you can build a local version of the Proj library.  This should be a fairly straightforward build.  You may then find that the Cartopy package installs OK, but that you get the following segfault at runtime when trying to use xcsv-plot-map:

```bash
free(): invalid size
Aborted (core dumped)
```

This is a known issue.  A suggested fix for this is to reinstall the Python `shapely` package.  First remove it:

```bash
$ pip uninstall shapely
```

and then reinstall it with specific `pip` options:

```bash
$ pip install --no-binary :all: shapely
```

This may take a while, but should resolve the segfault issue and everything should work.

## Using the package

An XCSV file with an [ACDD-compliant](https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3) extended header section, including geographical coordinates in `longitude` and `latitude` header items, and well-annotated column-headers, already provides much of the text needed to make an informative plot and map, so we can just plot the XCSV file directly from the command line.  This is the purpose of the `xcsv-plot-map` subpackage.  For example:

```bash
$ python3 -m xcsv.plot_map -x 0 -y 1 example.csv
```

Note here that we're calling `xcsv-plot-map` as a *module main*.  As a convenience, this invocation is wrapped as a console script when installing the package, hence the following invocation is equivalent:

```bash
$ xcsv_plot_map -x 0 -y 1 example.csv
```

In addition to using the CLI, the package can be used as a Python library.  The main class is `Plot`.  This is inherited from the `xcsv-plot.Plot` class, with some overridden methods.  The class provides methods to plot a given list of datasets (XCSV objects), and locate them on a map:

```python
import xcsv
import xcsv.plot_map as xpm

filenames = ['example1.csv','example2.csv','example3.csv']
datasets = []

for filename in filenames:
    with xcsv.File(filename) as f:
        datasets.append(f.read())

plotter = xpm.Plot()
plotter.plot_datasets(datasets, xidx=0, yidx=1)
```

## Command line usage

Calling the script with the `--help` option will show the following usage:

```bash
$ python -m xcsv.plot_map --help
usage: xcsv_plot_map [-h] [-x XIDX | -X XCOL] [-y YIDX | -Y YCOL]
                     [--x-label XLABEL] [--y-label YLABEL] [--invert-x-axis]
                     [--invert-y-axis] [--title TITLE] [--caption CAPTION]
                     [--label-key LABEL_KEY] [-s FIGSIZE FIGSIZE]
                     [-p PROJECTION] [-m] [-b BG_IMG_PATH] [-o OUT_FILE]
                     [-P PLOT_OPTS] [-S] [-V]
                     in_file [in_file ...]

plot the given XCSV files and locate the data on a map

positional arguments:
  in_file               input XCSV file(s)

optional arguments:
  -h, --help            show this help message and exit
  -x XIDX, --x-idx XIDX
                        column index (zero-based) containing values for the
                        x-axis
  -X XCOL, --x-column XCOL
                        column label containing values for the x-axis
  -y YIDX, --y-idx YIDX
                        column index (zero-based) containing values for the
                        y-axis
  -Y YCOL, --y-column YCOL
                        column label containing values for the y-axis
  --x-label XLABEL      text to be used for the plot x-axis label
  --y-label YLABEL      text to be used for the plot y-axis label
  --invert-x-axis       invert the x-axis
  --invert-y-axis       invert the y-axis
  --title TITLE         text to be used for the plot title
  --caption CAPTION     text to be used for the plot caption
  --label-key LABEL_KEY
                        key of the header item in the extended header section
                        whose value will be used for the plot legend label
  -s FIGSIZE FIGSIZE, --figsize FIGSIZE FIGSIZE
                        size of the figure (width height)
  -p PROJECTION, --map-projection PROJECTION
                        projection to use for displaying the site coordinates
                        on the map (one of the CRS classes provided by
                        Cartopy)
  -m, --plot-on-map     instead of a plot alongside a site map, show just a
                        map and plot the coordinate data directly on the map
  -b BG_IMG_PATH, --background-image BG_IMG_PATH
                        path to an image to show in the background of the plot
  -o OUT_FILE, --out-file OUT_FILE
                        output plot file
  -P PLOT_OPTS, --plot-options PLOT_OPTS
                        options for the plot, specified as a simple JSON
                        object
  -S, --scatter-plot    set plot options (see -P) to produce a scatter plot
  -V, --version         show program's version number and exit

Examples

Given an XCSV file with an ACDD-compliant extended header section, including geographical coordinates in longitude and latitude, and a single column (at column 0) of data values:

# id: 1
# title: The title
# latitude: -73.86 (degree_north)
# longitude: -65.46 (degree_east)
depth (m)
0.575
1.125
2.225

Then the following invocation will plot the only column on the y-axis, with the x-axis the indices of the data points, and will locate the coordinates on a map:

python3 -m xcsv.plot_map input.csv

If the file also contains a suitable variable for the x-axis:

# id: 1
# title: The title
# latitude: -73.86 (degree_north)
# longitude: -65.46 (degree_east)
time (year) [a],depth (m)
2012,0.575
2011,1.125
2010,2.225

then the columns to be used for the x- and y-axes can be specified thus:

python3 -m xcsv.plot_map -x 0 -y 1 input.csv
```

