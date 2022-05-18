###############################################################################
# Project: Extended CSV common file format
# Purpose: Classes to plot and locate on a map data from an extended CSV file
# Author:  Paul M. Breen
# Date:    2022-05-15
###############################################################################

__version__ = '0.1.0'

import os
import re

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

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

    def get_site_plot_extent(self, datasets, xkey='longitude', ykey='latitude', offset=5):
        """
        Get the extent over which the datasets range in geographical coordinates

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

        # N.B.: We don't use the "safe" get_metadata_item_value() here,
        #       because if the dataset doesn't contain lon and lat, then
        #       we can't display on a map, so best to quit immediately
        extent = [min([float(dataset.metadata['header'][xkey]['value']) for dataset in datasets]) - offset, max([float(dataset.metadata['header'][xkey]['value']) for dataset in datasets]) + offset, min([float(dataset.metadata['header'][ykey]['value']) for dataset in datasets]) - offset, max([float(dataset.metadata['header'][ykey]['value']) for dataset in datasets]) + offset]

        return extent

    def setup_site_plot(self, fig, ax, extent, crs=None, bg_img_name=None, bg_img_resolution='low', coastlines_resolution='10m', add_gridlines=True):
        """
        Setup the site map

        This sets fixed properties of the map, such as extent and base map.

        :param fig: The figure object
        :type fig: matplotlib.figure.Figure
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
            ax.gridlines()

    def plot_site(self, fig, ax, dataset, xkey='longitude', ykey='latitude', site_key='site', color='C0', linewidth=2, marker='o', transform=None, xoffset=0, yoffset=-0.5, fontsize='large', horizontalalignment='left'):
        """
        Plot the site information for the given dataset on the map

        :param fig: The figure object
        :type fig: matplotlib.figure.Figure
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
        :param color: A unique color to identify this site
        :type color: str
        :param linewidth: The linewidth of the site marker on the map
        :type linewidth: int
        :param marker: The marker symbol for the site on the map
        :type marker: str
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
        """

        if not transform:
            transform = ccrs.PlateCarree()

        # Don't mask the case of no lon/lat, let it fail if they're not present
        lon = [float(dataset.metadata['header'][xkey]['value'])]
        lat = [float(dataset.metadata['header'][ykey]['value'])]
        site = self.get_metadata_item_value(dataset, site_key)

        ax.plot(lon, lat, color=color, linewidth=linewidth, marker=marker, transform=transform)
        ax.text(lon[0] + xoffset, lat[0] + yoffset, site, color=color, fontsize=fontsize, horizontalalignment=horizontalalignment, transform=transform)

    def setup_figure_and_axes(self, figsize=None, width_ratios=[1,1], projection=None):
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
        :param width_ratios: The width ratios of the two subplots - the data
        plot and the map, in that order.  For example, [2,1] will make the
        plot twice the size of the map
        :type width_ratios: list
        :param projection: The projection to transform the coordinates on the
        map.  If not specified, it defaults to ccrs.PlateCarree()
        :type projection: cartopy.crs.CRS
        """

        if not projection:
            projection = ccrs.PlateCarree()

        self.fig = plt.figure(figsize=figsize)
        gs = self.fig.add_gridspec(1, 2, width_ratios=width_ratios)

        self.axs.append(self.fig.add_subplot(gs[0, 0]))
        self.axs.append(self.fig.add_subplot(gs[0, 1], projection=projection))

    def plot_datasets(self, datasets, fig=None, axs=None, axs_idx=0, map_axs_idx=1, xcol=None, ycol=None, xidx=None, yidx=0, xlabel=None, ylabel=None, title=None, title_wrap=True, caption=None, label_key=None, invert_xaxis=False, invert_yaxis=False, show=True):
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
        :param title_wrap: Wrap the title text
        :type title_wrap: bool
        :param caption: The figure caption text
        :type caption: str
        :param label_key: The key of a header item in the XCSV header to be
        used as a unique label to identify each data series in the plot legend
        :type label_key: str
        :param invert_xaxis: Invert the x-axis
        :type invert_xaxis: bool
        :param invert_yaxis: Invert the y-axis
        :type invert_yaxis: bool
        :param show: Show the plot
        :type show: bool
        """
 
        if fig:
            self.fig = fig

        if axs:
            self.axs = axs

        if not self.fig or not self.axs:
            self.setup_figure_and_axes()

        self.datasets = datasets
        self.xcol = xcol
        self.ycol = ycol

        if not title:
            title = self.get_metadata_item_value(datasets[0], self.DEFAULTS['title_key'])

        if not caption:
            caption = self.get_metadata_item_value(datasets[0], self.DEFAULTS['caption_key'])

        if not label_key:
            label_key = self.DEFAULTS['label_key']

        if not xcol:
            if xidx is not None:
                self.xcol = datasets[0].data.iloc[:, xidx].name

        if not ycol:
            self.ycol = datasets[0].data.iloc[:, yidx].name

        if not xlabel:
            xlabel = self.xcol

        if not ylabel:
            ylabel = self.ycol

        self.fig.suptitle(title, wrap=title_wrap)
        self.setup_data_plot(self.fig, self.axs[axs_idx], caption=caption, xlabel=xlabel, ylabel=ylabel)
        self.setup_site_plot(self.fig, self.axs[map_axs_idx], self.get_site_plot_extent(datasets))

        for i, dataset in enumerate(datasets):
            label = self.get_metadata_item_value(dataset, label_key)
            color = f'C{i}'
            self.plot_data(self.fig, self.axs[axs_idx], dataset, self.xcol, self.ycol, label=label, color=color, invert_xaxis=invert_xaxis, invert_yaxis=invert_yaxis)
            self.plot_site(self.fig, self.axs[map_axs_idx], dataset, color=color)

        if show:
            plt.show()

