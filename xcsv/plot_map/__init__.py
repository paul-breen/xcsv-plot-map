###############################################################################
# Project: Extended CSV common file format
# Purpose: Classes to plot and locate on a map data from an extended CSV file
# Author:  Paul M. Breen
# Date:    2022-05-15
###############################################################################

__version__ = '0.4.0'

import os
import re

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from shapely import geometry

import xcsv
import xcsv.plot as xp

ENV_CARTOPY_USER_BACKGROUNDS_DIR = 'static/images'
os.environ["CARTOPY_USER_BACKGROUNDS"] = ENV_CARTOPY_USER_BACKGROUNDS_DIR

class Plot(xp.Plot):
    """
    Class for plotting, and locating on a map, extended CSV objects
    """

    @staticmethod
    def get_crs_class_from_string(crs_str):
        """
        Get a Cartopy CRS class from a string containing its name

        For example 'PlateCarree' will return ccrs.PlateCarree().  If the
        string doesn't map to a supported CRS class, then an exception is
        thrown along with a hint that the string is not a valid CRS name

        :param crs_str: A string of the CRS class
        :type crs_str: str
        :returns: The class
        :rtype: cartopy.crs.CRS
        """

        # Using getattr() we can access the CRS/projection class from a string
        try:
            crs_class = getattr(ccrs, crs_str)()
        except AttributeError as e:
            print(f'It seems that {crs_str} is not a CRS that is provided by Cartopy')
            raise

        return crs_class

    def _get_site_plot_extent(self, datasets, keys, offset):
        """
        Get the extent over which the datasets range in geographical
        coordinates, either point or bounding box, given the appropriate
        header keys

        A list is returned with the shape [left, right, bottom, top].  This
        can be used for the extent value to set_extent().

        :param datasets: A list of XCSV objects containing the input datasets
        :type datasets: list
        :param keys: An ordered list of keys, giving [xmin,xmax,ymin,ymax]
        :type keys: list
        :param offset: An offset (in degrees) to apply around the given keys
        :type offset: float
        :returns: The extent
        :rtype: list
        """

        extent = []

        # The default value returned from get_metadata_item_value() if the
        # key doesn't exist, is None.  Hence we catch TypeError
        try:
            extent = [min([float(dataset.get_metadata_item_value(keys[0])) for dataset in datasets]) - offset, max([float(dataset.get_metadata_item_value(keys[1])) for dataset in datasets]) + offset, min([float(dataset.get_metadata_item_value(keys[2])) for dataset in datasets]) - offset, max([float(dataset.get_metadata_item_value(keys[3])) for dataset in datasets]) + offset]
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot calculate map extent as some of the required spatial coordinate keys were not found in the header. Exception: {e}")

        return extent

    def get_site_plot_extent_from_point(self, datasets, xkey='longitude', ykey='latitude', offset=5):
        """
        Get the extent over which the datasets range in point geographical
        coordinates

        A list is returned with the shape [left, right, bottom, top].  This
        can be used for the extent value to set_extent().

        :param datasets: A list of XCSV objects containing the input datasets
        :type datasets: list
        :param xkey: The header item key for the coordinate in the x-direction
        :type xkey: str
        :param ykey: The header item key for the coordinate in the y-direction
        :type ykey: str
        :param offset: An offset (in degrees) to apply around the given point
        :type offset: float
        :returns: The extent
        :rtype: list
        """

        keys = [xkey, xkey, ykey, ykey]

        return self._get_site_plot_extent(datasets, keys, offset)

    def get_site_plot_extent_from_bbox(self, datasets, xminkey='geospatial_lon_min', xmaxkey='geospatial_lon_max', yminkey='geospatial_lat_min', ymaxkey='geospatial_lat_max', offset=5):
        """
        Get the extent over which the datasets range in bounding box
        geographical coordinates

        A list is returned with the shape [left, right, bottom, top].  This
        can be used for the extent value to set_extent().

        :param datasets: A list of XCSV objects containing the input datasets
        :type datasets: list
        :param xminkey: The header item key for the minimum coordinate in
        the x-direction
        :type xminkey: str
        :param xmaxkey: The header item key for the maximum coordinate in
        the x-direction
        :type xmaxkey: str
        :param yminkey: The header item key for the minimum coordinate in
        the y-direction
        :type yminkey: str
        :param ymaxkey: The header item key for the maximum coordinate in
        the y-direction
        :type ymaxkey: str
        :param offset: An offset (in degrees) to apply around the given bbox
        :type offset: float
        :returns: The extent
        :rtype: list
        """

        keys = [xminkey, xmaxkey, yminkey, ymaxkey]

        return self._get_site_plot_extent(datasets, keys, offset)

    def get_site_plot_extent(self, datasets, point_test_key='longitude', bbox_test_key='geospatial_lon_min'):
        """
        Get the extent over which the datasets range in geographical
        coordinates, either point or bounding box

        A list is returned with the shape [left, right, bottom, top].  This
        can be used for the extent value to set_extent().

        :param datasets: A list of XCSV objects containing the input datasets
        :type datasets: list
        :param point_test_key: The header item key to test whether coordinates
        are given as a point
        :type point_test_key: str
        :param bbox_test_key: The header item key to test whether coordinates
        are given as a bounding box
        :type bbox_test_key: str
        :returns: The extent
        :rtype: list
        """

        extent = []

        try:
            test_dataset = datasets[0]
        except IndexError:
            raise KeyError(f"Cannot calculate map extent as no datasets were provided")

        if point_test_key in test_dataset.metadata['header']:
            extent = self.get_site_plot_extent_from_point(datasets)
        elif bbox_test_key in test_dataset.metadata['header']:
            extent = self.get_site_plot_extent_from_bbox(datasets)
        else:
            raise KeyError(f"Cannot calculate map extent as required spatial coordinate keys were not found in the header")

        return extent

    def setup_site_plot(self, ax, extent, crs=None, bg_img_name=None, bg_img_resolution='low', coastlines_resolution='10m', add_gridlines=True, draw_gridline_labels=True):
        """
        Setup the site map

        This sets fixed properties of the map, such as extent and base map.

        :param ax: The axis object
        :type ax: matplotlib.axes.Axes
        :param extent: The geographical bounding box extent for the map
        as [left, right, bottom, top]
        :type extent: list
        :param crs: The CRS for the map.  If not specified, it defaults to
        ccrs.PlateCarree()
        :type crs: cartopy.crs.CRS
        :param bg_img_name: A name of a background image to be used for the
        base layer of the map.  This must be a valid name from images.json,
        found in the directory specified in the CARTOPY_USER_BACKGROUNDS
        environment variable.  If not specified, then the built-in low
        resolution stock image (e.g. ax.stock_img()) is used instead
        :type bg_img_name: str
        :param bg_img_resolution: A supported resolution of the background
        image name given in bg_img_name
        :type bg_img_resolution: str
        :param coastlines_resolution: The resolution of the coastlines
        :type coastlines_resolution: str
        :param add_gridlines: Add gridlines to the map
        :type add_gridlines: bool
        :param draw_gridline_labels: Draw gridline labels on the map
        :type draw_gridline_labels: bool
        """

        if not crs:
            crs = ccrs.PlateCarree()

        ax.set_extent(extent, crs=crs)
        ax.coastlines(resolution=coastlines_resolution)

        if bg_img_name:
            ax.background_img(name=bg_img_name, resolution=bg_img_resolution)
        else:
            ax.stock_img()

        if add_gridlines:
            ax.gridlines(draw_labels=draw_gridline_labels)

    def plot_point_site(self, ax, dataset, xkey='longitude', ykey='latitude', site_key='site', transform=None, xoffset=0, yoffset=-0.5, fontsize='large', horizontalalignment='left', opts={}):
        """
        Plot the site information for the given dataset on the map

        :param ax: The axis object
        :type ax: matplotlib.axes.Axes
        :param dataset: The dataset to plot
        :type dataset: XCSV object
        :param xkey: The header item key for the coordinate in the x-direction
        :type xkey: str
        :param ykey: The header item key for the coordinate in the y-direction
        :type ykey: str
        :param site_key: The header item key for the site identifier
        :type site_key: str
        :param transform: The projection to transform the coordinates on the
        map.  If not specified, it defaults to ccrs.PlateCarree()
        :type transform: cartopy.crs.CRS
        :param xoffset: An x-direction offset for the site text from the marker
        :type xoffset: float
        :param yoffset: An y-direction offset for the site text from the marker
        :type yoffset: float
        :param fontsize: Font size of the site text
        :type fontsize: str
        :param horizontalalignment: Horizontal position of the site text
        relative to the marker
        :type horizontalalignment: str
        :param opts: Option kwargs to apply to all plots (e.g., color, marker)
        :type opts: dict
        """

        if not transform:
            transform = ccrs.PlateCarree()

        site = dataset.get_metadata_item_value(site_key)
        color = opts['color'] if 'color' in opts else 'C0'
        marker = opts['marker'] if 'marker' in opts else 'o'

        try:
            lon = [float(dataset.get_metadata_item_value(xkey))]
            lat = [float(dataset.get_metadata_item_value(ykey))]

            ax.plot(lon, lat, transform=transform, color=color, marker=marker)
            ax.text(lon[0] + xoffset, lat[0] + yoffset, site, color=color, fontsize=fontsize, horizontalalignment=horizontalalignment, transform=transform)
        except KeyError:
            pass

    def plot_bbox_site(self, ax, dataset, xminkey='geospatial_lon_min', xmaxkey='geospatial_lon_max', yminkey='geospatial_lat_min', ymaxkey='geospatial_lat_max', site_key='site', transform=None, xoffset=0, yoffset=-0.5, fontsize='large', horizontalalignment='left', opts={}):
        """
        Plot the site information for the given dataset on the map

        :param ax: The axis object
        :type ax: matplotlib.axes.Axes
        :param dataset: The dataset to plot
        :type dataset: XCSV object
        :param xminkey: The header item key for the minimum coordinate in
        the x-direction
        :type xminkey: str
        :param xmaxkey: The header item key for the maximum coordinate in
        the x-direction
        :type xmaxkey: str
        :param yminkey: The header item key for the minimum coordinate in
        the y-direction
        :type yminkey: str
        :param ymaxkey: The header item key for the maximum coordinate in
        the y-direction
        :type ymaxkey: str
        :param site_key: The header item key for the site identifier
        :type site_key: str
        :param transform: The projection to transform the coordinates on the
        map.  If not specified, it defaults to ccrs.PlateCarree()
        :type transform: cartopy.crs.CRS
        :param xoffset: An x-direction offset for the site text from the marker
        :type xoffset: float
        :param yoffset: An y-direction offset for the site text from the marker
        :type yoffset: float
        :param fontsize: Font size of the site text
        :type fontsize: str
        :param horizontalalignment: Horizontal position of the site text
        relative to the marker
        :type horizontalalignment: str
        :param opts: Option kwargs to apply to all plots (e.g., color, marker)
        :type opts: dict
        """

        if not transform:
            transform = ccrs.PlateCarree()

        site = dataset.get_metadata_item_value(site_key)
        color = opts['color'] if 'color' in opts else 'C0'
        marker = opts['marker'] if 'marker' in opts else 'o'
        alpha = opts['alpha'] if 'alpha' in opts else 0.5

        try:
            lon_min = float(dataset.get_metadata_item_value(xminkey))
            lon_max = float(dataset.get_metadata_item_value(xmaxkey))
            lat_min = float(dataset.get_metadata_item_value(yminkey))
            lat_max = float(dataset.get_metadata_item_value(ymaxkey))

            geom = geometry.box(minx=lon_min, maxx=lon_max, miny=lat_min, maxy=lat_max)
            ax.add_geometries([geom], crs=transform, facecolor=color, edgecolor='black', alpha=alpha)
            ax.text(lon_min + xoffset, lat_min + yoffset, site, color=color, fontsize=fontsize, horizontalalignment=horizontalalignment, transform=transform)
        except KeyError:
            pass

    def plot_site(self, ax, dataset, point_test_key='longitude', bbox_test_key='geospatial_lon_min', site_key='site', transform=None, xoffset=0, yoffset=-0.5, fontsize='large', horizontalalignment='left', opts={}):
        """
        Plot the site information for the given dataset on the map

        :param ax: The axis object
        :type ax: matplotlib.axes.Axes
        :param dataset: The dataset to plot
        :type dataset: XCSV object
        :param point_test_key: The header item key to test whether coordinates
        are given as a point
        :type point_test_key: str
        :param bbox_test_key: The header item key to test whether coordinates
        are given as a bounding box
        :type bbox_test_key: str
        :param site_key: The header item key for the site identifier
        :type site_key: str
        :param transform: The projection to transform the coordinates on the
        map.  If not specified, it defaults to ccrs.PlateCarree()
        :type transform: cartopy.crs.CRS
        :param xoffset: An x-direction offset for the site text from the marker
        :type xoffset: float
        :param yoffset: An y-direction offset for the site text from the marker
        :type yoffset: float
        :param fontsize: Font size of the site text
        :type fontsize: str
        :param horizontalalignment: Horizontal position of the site text
        relative to the marker
        :type horizontalalignment: str
        :param opts: Option kwargs to apply to all plots (e.g., color, marker)
        :type opts: dict
        """

        # Plot according to whether site coordinates are given by a point
        # or a bounding box
        if point_test_key in dataset.metadata['header']:
            self.plot_point_site(ax, dataset, site_key=site_key, transform=transform, xoffset=xoffset, yoffset=yoffset, fontsize=fontsize, horizontalalignment=horizontalalignment, opts=opts)
        elif bbox_test_key in dataset.metadata['header']:
            self.plot_bbox_site(ax, dataset, site_key=site_key, transform=transform, xoffset=xoffset, yoffset=yoffset, fontsize=fontsize, horizontalalignment=horizontalalignment, opts=opts)
        else:
            raise KeyError(f"Cannot plot site on the map as no spatial coordinate keys were found in the header")

    def setup_figure_and_axes(self, figsize=None, nrows=1, ncols=2, width_ratios=[1,1], projection=None):
        """
        Setup the figure and axes array

        If not called directly, then it is called by the plot_datasets()
        function.  If a specific figure size is required, then this function
        should be called directly, before calling any of the plotting
        functions (e.g., plot_datasets()).

        This stores the figure object in self.fig and the axes array in
        self.axs.

        :param figsize: The figure size tuple as (width, height)
        :type figsize: tuple
        :param nrows: The number of rows for the subplots (1 or 2)
        :type nrows: int
        :param ncols: The number of columns for the subplots (1 or 2)
        :type ncols: int
        :param width_ratios: The width ratios of the subplots.  If there is
        only one subplot, then it is the map, and this should be [1].  If
        there are two subplots, then these are the data plot and the map, in
        that order.  For example, [2,1] will make the plot twice the size of
        the map
        :type width_ratios: list
        :param projection: The projection to transform the coordinates on the
        map.  If not specified, it defaults to ccrs.PlateCarree()
        :type projection: cartopy.crs.CRS
        """

        if not projection:
            projection = ccrs.PlateCarree()

        self.fig = plt.figure(figsize=figsize)
        gs = self.fig.add_gridspec(nrows=nrows, ncols=ncols, width_ratios=width_ratios)

        if nrows * ncols > 1:
            self.axs.append(self.fig.add_subplot(gs[0, 0]))
            self.axs.append(self.fig.add_subplot(gs[0, 1], projection=projection))
        else:
            self.axs.append(self.fig.add_subplot(gs[0, 0], projection=projection))

    def _setup_fallback_figure_and_axes(self, fig=None, axs=None, plot_on_map=False):
        """
        Setup a fallback figure and axes array

        This calls setup_figure_and_axes() if it hasn't already beeen called

        :param fig: The figure object
        :type fig: matplotlib.figure.Figure
        :param axs: The axes array
        :type axs: matplotlib.axes.Axes
        :param plot_on_map: Only setup a map, as the data are to be plotted
        directly on the map
        :type plot_on_map: bool
        """

        if fig:
            self.fig = fig

        if axs:
            self.axs = axs

        if not self.fig or not self.axs:
            fa_opts = {'nrows': 1, 'ncols': 2, 'width_ratios': [1,1]}

            if plot_on_map:
                fa_opts = {'nrows': 1, 'ncols': 1, 'width_ratios': [1]}

            self.setup_figure_and_axes(**fa_opts)

    def _add_figure_annotations(self, axs_idx=0, map_axs_idx=1, plot_on_map=False):
        """
        Add annotations to the figure

        :param axs_idx: The index of the axis object in the axs array
        :type axs_idx: int
        :param map_axs_idx: The index of the map axis object in the axs array
        :type map_axs_idx: int
        :param plot_on_map: Only setup a map, as the data are to be plotted
        directly on the map
        :type plot_on_map: bool
        """

        self.add_figure_title(self.title)
        self.add_figure_caption(self.caption)

        if plot_on_map:
            self.setup_site_plot(self.axs[axs_idx], self.get_site_plot_extent(self.datasets))
        else:
            self.setup_data_plot(self.axs[axs_idx], xlabel=self.xlabel, ylabel=self.ylabel)
            self.setup_site_plot(self.axs[map_axs_idx], self.get_site_plot_extent(self.datasets))

    def _plot_datasets(self, axs_idx=0, map_axs_idx=1, plot_on_map=False, invert_xaxis=False, invert_yaxis=False, opts={}):
        """
        Plot the data for the figure datasets

        :param axs_idx: The index of the axis object in the axs array
        :type axs_idx: int
        :param map_axs_idx: The index of the map axis object in the axs array
        :type map_axs_idx: int
        :param plot_on_map: Only setup a map, as the data are to be plotted
        directly on the map
        :type plot_on_map: bool
        :param invert_xaxis: Invert the x-axis
        :type invert_xaxis: bool
        :param invert_yaxis: Invert the y-axis
        :type invert_yaxis: bool
        :param opts: Option kwargs to apply to all plots (e.g., color, marker)
        :type opts: dict
        """

        generate_colors = True

        if 'color' in opts:
            generate_colors = False

        for i, dataset in enumerate(self.datasets):
            label = dataset.get_metadata_item_value(self.label_key)

            if generate_colors:
                opts.update({'color': f'C{i}'})

            if plot_on_map:
                projection = self.axs[axs_idx].projection

                if not projection:
                    projection = ccrs.PlateCarree()

                opts.update({'transform': projection})

                self.plot_data(self.axs[axs_idx], dataset, self.xcol, self.ycol, label=label, invert_xaxis=invert_xaxis, invert_yaxis=invert_yaxis, opts=opts)
            else:
                self.plot_data(self.axs[axs_idx], dataset, self.xcol, self.ycol, label=label, invert_xaxis=invert_xaxis, invert_yaxis=invert_yaxis, opts=opts)
                self.plot_site(self.axs[map_axs_idx], dataset, site_key=self.label_key, opts=opts)

    def plot_datasets(self, datasets, fig=None, axs=None, axs_idx=0, map_axs_idx=1, xcol=None, ycol=None, xidx=None, yidx=0, xlabel=None, ylabel=None, title=None, caption=None, label_key=None, invert_xaxis=False, invert_yaxis=False, plot_on_map=False, show=True, opts={}):
        """
        Plot the data for the given datasets

        Either the xcol and ycol column header labels, or the xidx and yidx
        column indices, can be specified.  These are mutually exclusive.  They
        identify the data series from the datasets' data tables to be used for
        the x- and y-axis data.

        If annotations such as the title and caption, and the label_key,
        are not specified, then they are taken from XCSV header items
        (see self.DEFAULTS for details).  If these keys are not present in
        the header, then an empty string is used instead, effectively leaving
        them blank.

        If show is set to False, then custom edits can be made to the plot
        (e.g. adding extra annotations) before displaying.  Also, if saving
        the plot to an output file instead of displaying, then set show=False.

        :param datasets: A list of XCSV objects containing the input datasets
        :type datasets: list
        :param fig: The figure object
        :type fig: matplotlib.figure.Figure
        :param axs: The axes array
        :type axs: matplotlib.axes.Axes
        :param axs_idx: The index of the plot axis object in the axs array
        :type axs_idx: int
        :param map_axs_idx: The index of the map axis object in the axs array
        :type map_axs_idx: int
        :param xcol: The x-axis data column header label
        :type xcol: str
        :param ycol: The y-axis data column header label
        :type ycol: str
        :param xidx: The x-axis data column index
        :type xidx: int
        :param yidx: The y-axis data column index
        :type yidx: int
        :param xlabel: The x-axis label text
        :type xlabel: str
        :param ylabel: The y-axis label text
        :type ylabel: str
        :param title: The figure title text
        :type title: str
        :param caption: The figure caption text
        :type caption: str
        :param label_key: The key of a header item in the XCSV header to be
        used as a unique label to identify each data series in the plot legend
        :type label_key: str
        :param invert_xaxis: Invert the x-axis
        :type invert_xaxis: bool
        :param invert_yaxis: Invert the y-axis
        :type invert_yaxis: bool
        :param plot_on_map: Instead of plotting the data on a plot alongside
        the site map, show just a map and plot the data directly on the map.
        This requires the data to be coordinates
        :type plot_on_map: bool
        :param show: Show the plot
        :type show: bool
        :param opts: Option kwargs to apply to all plots (e.g., color, marker)
        :type opts: dict
        """

        self._setup_fallback_figure_and_axes(fig, axs, plot_on_map)
        self._store_figure_parameters(datasets, xcol, ycol, xidx, yidx, xlabel, ylabel, title, caption, label_key)
        self._add_figure_annotations(axs_idx, map_axs_idx, plot_on_map)
        self._plot_datasets(axs_idx, map_axs_idx, plot_on_map, invert_xaxis, invert_yaxis, opts)

        if show:
            plt.show()

