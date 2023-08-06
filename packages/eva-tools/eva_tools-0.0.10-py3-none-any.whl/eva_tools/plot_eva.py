"""
plot_eva.py
Script for the interpretation and visualization of Easy Volcanic Aerosol (EVA) data.
Created by C.J. Ogilvie under the supervision of Dr. Matthew Toohey.
Created for the Institute of Space and Atmospheric Studies at the University of Saskatchewan.
Last updated April 22nd, 2021.

Primarily, this script is used to create and manipulate useful plots for four types of data:
-Extinction (ext)
-Single Scattering Albedo (ssa)
-Aerosol Optical Depth (aod)
-Scattering Asymmetry Factor (asy)

Use of this script can be from the command line to any of invoke the four functions:
-plot_at_wavelength()
-plot_all_bands()
-plot_difference()
-plotGlobalMeanAOD()

The script can also be imported into another file to use any of these functions, as well as
ReadNCData objects, PlotEVA objects, and the get_data() function. These may be useful if more specific
manipulation of the data is required.

A more detailed manual for the use of this script is currently in progress.
"""

import matplotlib.pyplot as plt
from netCDF4 import Dataset as open_ncfile
import numpy as np
import os
import os.path as path
import sys
import re

# Sets default wavelength to use, for global mean aod
DEFAULT_WAVELENGTH = 0.55
# Sets scaling to use for each datatype
AOD_SCALE = 1e2
EXT_SCALE = 1e3
SSA_SCALE = 1e2
ASY_SCALE = 1e2


class ReadNCData:
    """
    Class for opening, reading, and interpreting EVA data from a netCDF file
    """
    # unopened data file
    file = None
    # opened data file
    nc = None

    # data fields
    ext_sun = None
    ssa_sun = None
    asy_sun = None
    ext_earth = None
    ssa_earth = None
    asy_earth = None
    lat = None
    alt = None
    time = None
    wl1_sun = None
    wl2_sun = None
    wl1_earth = None
    wl2_earth = None
    aod_earth = None
    aod_sun = None

    # Unit fields
    ext_units = None
    ssa_units = None
    asy_units = None
    aod_units = None
    lat_units = None
    alt_units = None
    time_units = None
    wave_units = None

    def __init__(self, file_in=None, get_years=False):
        # check if given a file, or should be read from command line
        if file_in is None:
            self.__get_file()
        else:
            self.file = file_in
        self.__read_file(get_years=get_years)

    def __get_file(self):
        """
         # Reads the input file from the command line argument
        :return:
        """
        self.file = sys.argv[1]

    def __read_file(self, get_years=False):
        """
        Reads data fields into object attributes
        :param get_years: Sets if time data should be converted to years if it is in another format.
        :return: None
        """
        if self.file[0] == '.' and self.file[1] == '\\':
            self.file = str(os.getcwd() + '\\' + self.file[2:]).strip()

        # open netcdf file
        self.nc = open_ncfile(self.file)
        # read variables from file
        self.ext_sun = self.nc.variables['ext_sun']
        self.ssa_sun = self.nc.variables['omega_sun']
        self.asy_sun = self.nc.variables['g_sun']
        self.ext_earth = self.nc.variables['ext_earth']
        self.ssa_earth = self.nc.variables['omega_earth']
        self.asy_earth = self.nc.variables['g_earth']
        self.lat = self.nc.variables['latitude'][:]
        self.alt = self.nc.variables['altitude'][:]
        self.wl1_sun = self.nc.variables['wl1_sun'][:]
        self.wl2_sun = self.nc.variables['wl2_sun'][:]
        self.wl1_earth = self.nc.variables['wl1_earth'][:]
        self.wl2_earth = self.nc.variables['wl2_earth'][:]
        # Set units
        self.ext_units = self.nc.variables['ext_sun'].units
        self.ssa_units = self.nc.variables['omega_sun'].units
        self.asy_units = self.nc.variables['g_sun'].units
        self.lat_units = self.nc.variables['latitude'].units
        self.alt_units = self.nc.variables['altitude'].units
        self.wave_units = self.nc.variables['wl1_sun'].units

        # Set the time scale we will be using according to what data is available

        # Use dec_year as the most desirable time format, if available
        if 'dec_year' in self.nc.variables and not np.ma.is_masked(self.nc.variables['dec_year'][:]) \
                and self.nc.variables['dec_year'][0] < 1e36:
            self.time = self.dec_year = self.nc.variables['dec_year'][:]
            self.time_units = self.nc.variables['dec_year'].units
            self.__check_dimensions('dec_year')
        # Use months if dec_year is not available and months is
        elif 'month' in self.nc.variables and not np.ma.is_masked(self.nc.variables['month'][:]) \
                and self.nc.variables['month'][0] < 1e36:
            self.time = self.nc.variables['month'][:]
            self.time_units = self.nc.variables['month'].units
            self.__check_dimensions('month')
            if get_years:
                self.months_to_years(save_as_time=True)
        # Use time if neither dec_year or months are available
        elif 'time' in self.nc.variables and not np.ma.is_masked(self.nc.variables['time'][:]) \
                and self.nc.variables['time'][0] < 9e36:
            self.time = self.nc.variables['time'][:]
            self.time_units = self.nc.variables['time'].units
            self.__check_dimensions('time')
        # Exit if no time formats can be used
        else:
            sys.exit("Time parameter not found in this data set.")

    def __check_dimensions(self, time):
        """
        Check the dimensions of the data are in the expected order, and rearrange them if not.
        :param time: The name of the time variable we are using, 'dec_year', 'months', or 'time'
        :return: None
        """
        time = self.nc.variables[time].dimensions[0]
        bands = self.nc.variables['wl1_earth'].dimensions[0]
        lat = self.nc.variables['latitude'].dimensions[0]
        alt = self.nc.variables['altitude'].dimensions[0]

        expected_dimensions = [time, bands, lat, alt]
        dims_match = True
        for index, dim in enumerate(self.ext_earth.dimensions[:]):
            if expected_dimensions[index] != dim:
                dims_match = False
        # We will assume that ext, asy, and ssa share the same dimension ordering
        if dims_match:
            return
        # Determine the current order of dimensions
        time_index = self.ext_earth.dimensions[:].index(time)
        bands_index = self.ext_earth.dimensions[:].index(bands)
        lat_index = self.ext_earth.dimensions[:].index(lat)
        alt_index = self.ext_earth.dimensions[:].index(alt)
        # Rearrange the data to the appropriate dimensions
        self.ext_earth = np.transpose(self.ext_earth, (time_index, bands_index, lat_index, alt_index))
        self.ext_sun = np.transpose(self.ext_sun, (time_index, bands_index, lat_index, alt_index))
        self.asy_earth = np.transpose(self.asy_earth, (time_index, bands_index, lat_index, alt_index))
        self.asy_sun = np.transpose(self.asy_sun, (time_index, bands_index, lat_index, alt_index))
        self.ssa_earth = np.transpose(self.ssa_earth, (time_index, bands_index, lat_index, alt_index))
        self.ssa_sun = np.transpose(self.ssa_sun, (time_index, bands_index, lat_index, alt_index))

    def months_to_years(self, save_as_time=False):
        """
        Converts the time data from months to years.
        This function checks the time units for a starting year for the months data, and assumes 1850 if none is found.
        :param save_as_time: Sets if the time parameter should be updated to the calculated years.
        :return: array containing the time data in years.
        """
        months = self.time
        units = self.time_units
        if not ('month' in units or 'Month' in units):
            sys.exit("No units of months for conversion.")
        # Check if the units specify a starting year
        match = re.search('[1-2][0-9]{3}', units)
        if match:
            first_year = float(match.group())
        else:
            first_year = 1850
        years = months/12 + first_year
        if save_as_time:
            self.time = years
            self.time_units = 'Year'
        return years

    def print_file(self, print_vars=False):
        """
        Prints data on file contents to the console
        :param print_vars: If True, will print the nc data variables for this dataset.
        :return: None
        """
        if self.nc is None:
            self.nc = open_ncfile(self.file)
        if print_vars:
            print(self.nc.variables)
        else:
            print(self.nc)

    def calc_aod(self):
        """
        Calculates the aerosol optical depths, and stores them in the aod_earth and aod_sun attributes
        :return: None
        """
        # Want to iterate over all altitudes, in case altitude differences are not consistently spaced.
        # Build the aod arrays and initialize to zeros, so we can add to them
        aod_earth = np.zeros((len(self.time), len(self.wl1_earth), len(self.lat)))
        aod_sun = np.zeros((len(self.time), len(self.wl1_sun), len(self.lat)))
        # Extrapolate past edge of altitude, in order to get a change in altitude for first point
        last_alt = self.alt[0] - (self.alt[1] - self.alt[0])
        # Sum ext*d(alt) over all altitudes
        for alt_index, alt in enumerate(self.alt):
            aod_earth += self.ext_earth[:, :, :, alt_index] * (alt - last_alt)
            aod_sun += self.ext_sun[:, :, :, alt_index] * (alt - last_alt)
            last_alt = alt
        # Store the data in the object
        self.aod_earth = aod_earth
        self.aod_sun = aod_sun
        self.aod_units = 'unitless'


class PlotEVA:
    """
    Class for performing plotting functions on a single EVA data file
    """
    # data object to plot from
    data = None
    # Boolean used for tracking figures
    first_fig = True
    # Scaling for the data
    aod_scale = AOD_SCALE
    ext_scale = EXT_SCALE
    ssa_scale = SSA_SCALE
    asy_scale = ASY_SCALE

    def __init__(self, data_in, get_years=False):
        """
        :param data_in: either a string path to an unopened nc data file, or a ReadNCData object.
        :param get_years: Determines if a file should be forced to use years as the time units.
        """
        try:
            # Check if input is a string (file location)
            if data_in is None or isinstance(data_in, str):
                self.data = ReadNCData(file_in=data_in, get_years=get_years)
            else:
                self.data = data_in
                test = self.data.time_units  # Just checks if time_units exists
        except TypeError:
            print('PlotEVA() input was not a valid file path, nor a ReadNCData object.')

    def _update_fig(self):
        """
        Updates the value of the current figure to the next
        :return: None
        """
        # Check if this is the first figure being plotted
        if plt.gcf().number == 1 and self.first_fig and not plt.gcf().get_axes():
            self.first_fig = False
        else:
            # Update plot, and reset first fig in case figures are reset
            plt.figure(plt.gcf().number + 1)
            self.first_fig = True

    def show(self):
        """
        Shows all created plots.
        :return: None
        """
        self.first_fig = True  # Reset, so correct for next plotting sequence
        plt.show()

    def save(self, save_name=None):
        """
        Saves the current figure to the current directory as a .png file.
        :return:
        """
        # Use file name if no save name is given
        if save_name is None:
            save_name = self.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '.png'
        # Check if a file with this save name exists, append a number if it does i.e. test_pic(2).png
        if path.isfile(save_name):
            filenum = 1
            new_name = save_name
            while path.isfile(new_name):
                filenum += 1
                new_name = save_name.rsplit('.png', 1)[0] + '(' + str(filenum) + ').png'
            save_name = new_name.strip()

        plt.savefig(save_name)

    def _determine_wavelength(self, wavelength):
        """
        Finds the narrowest band a given wavelength is contained within
        :param wavelength: integer value of the wavelength, in micrometers
        :return: index of the wl1 data which specifies the correct band (solar indices follow terrestrial).
                or -1 if the wavelength is not found.
        """
        # Find the bands which contain the specified wavelength
        matched_bands = []
        band_width = []
        # Examine terrestrial bands
        for band in range(0, len(self.data.wl1_earth)):
            if self.data.wl2_earth[band] > wavelength >= self.data.wl1_earth[band]:
                band_width.append(self.data.wl2_earth[band] - self.data.wl1_earth[band])
                matched_bands.append(band)
        # Examine solar bands
        for band in range(0, len(self.data.wl2_sun)):
            if self.data.wl2_sun[band] > wavelength >= self.data.wl1_sun[band]:
                band_width.append(self.data.wl2_sun[band] - self.data.wl1_sun[band])
                matched_bands.append(band+len(self.data.wl1_earth))

        if len(matched_bands) == 0:
            return -1
        else:
            index = band_width.index(min(band_width))
            return matched_bands[index]

    def _get_band_limits(self, wavelength, given_band_index=False):
        """
        Gets the wavelength limits of the band the target wavelength is within, as well as the band index.
        :param wavelength: The target wavelength OR the band index of the target band. For the latter, must set the
            given_band_index parameter to true
        :param given_band_index: Sets if 'wavelength' should be read as a band index instead
        :return: tuple containing the lowest wavelength in the band, the highest, and the band index.
                (Or None, None, -1 if wavelength cannot be found.)
        """
        if given_band_index:
            band_index = wavelength
        else:
            band_index = self._determine_wavelength(wavelength)
            if band_index == -1:
                print("Wavelength " + str(wavelength) + " not found in the given bands.")
                return None, None, -1
        # Determine the wavelength range of this band
        if band_index < len(self.data.wl1_earth):
            low_wave = round(self.data.wl1_earth[band_index], 2)
            high_wave = round(self.data.wl2_earth[band_index], 2)
        else:
            band_index -= len(self.data.wl1_earth)
            low_wave = round(self.data.wl1_sun[band_index], 2)
            high_wave = round(self.data.wl2_sun[band_index], 2)
        return low_wave, high_wave, band_index

    def wavelength(self, wavelength, datatype="multi", time='mean', DataID='', new_fig=True, divs=10):
        """
        Plots the extinction data for a single band at a specified wavelength.
        :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
        :param datatype: string specifying type of data to be plotted - 'ext','aod','ssa','asy', or 'multi'.
        :param wavelength: integer value of the wavelength to be plotted, in micrometers
        :param DataID: String that specifies the type of data being plotted, for the title.
        :param new_fig: boolean which sets if this plot should be plotted on a new figure
        :param divs: Sets the amount of colorbar divisions that should be used
        :return: None if wavelength cannot be found, otherwise tuple containing low and high wavelength in the band, and band index
        """

        low_wave, high_wave, band_index = self._get_band_limits(wavelength)
        if band_index == -1:
            print("Wavelength " + str(wavelength) + " not found in the given bands.")
            return None
        else:
            self._single(band_index, datatype=datatype, time=time, new_fig=new_fig, divs=divs)
            plt.suptitle(DataID + "Wavelength " + str(wavelength) + self.data.wave_units + " (Band " + str(band_index) +
            ": " + str(low_wave) + "-" + str(high_wave) + self.data.wave_units + ")")
            return low_wave, high_wave, band_index

    def allbands(self, band_range='all', datatype='multi', time='mean', plot_lim=4, ncols=2,  spacing=1.5, top=0.85,
                 save_fig=False, save_name=None, divs=10):
        """
        Plots all bands of data for this data type
        :param band_range: string, specifies the bands to be plotted - 'all', 'terrestrial' or 'solar'
        :param datatype: Specifies the type of data all bands will be plotted for
        :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
        :param plot_lim: sets the limit on the number of subplots per figure
        :param ncols: sets the number of subplot columns for each figure
        :param spacing: sets the spacing between subplots
        :param top: sets the spacing between the subplots and the top of the figure
        :param save_fig: Boolean sets if the figures created should be saved
        :param save_name: String, sets the save name if this figure is to be saved
        :param divs: sets the number of colorbar divisions to be used
        :return: None
        """
        # Ensure the datatype is valid
        assert datatype == 'multi' or datatype == 'aod' or datatype == 'ext' or datatype == 'ssa' or datatype == 'asy',\
            "datatype argument not recognized - acceptable strings are 'multi', 'aod', 'ext', 'ssa', or 'asy'."

        # If type is multi, switch to using the multi allbands function
        if datatype == 'multi':
            self._allbands_multi(band_range=band_range, time=time, spacing=spacing, top=top, save_fig=save_fig,
                                 save_name=save_name, divs=divs)
            return

        # Ensure the specified band range is valid
        assert band_range == 'all' or band_range == 'terrestrial' or band_range == 'solar', \
            "band_range argument not recognized - acceptable values are 'all', 'terrestrial' or 'solar' "
        if band_range == 'all':
            numBands = len(self.data.wl1_earth) + len(self.data.wl1_sun)
        elif band_range == 'terrestrial':
            numBands = len(self.data.wl1_earth)
        else:
            numBands = len(self.data.wl1_sun)

        # Determine the number of subplots needed and the arrangement
        plot_lim = plot_lim    # Sets how many plots to limit the figure to
        ncols = ncols          # Sets how many columns to limit the figure to
        # Determine the number of rows needed
        if numBands <= ncols:
            nrows = 1
            ncols = numBands
        else:
            nrows = int(np.ceil(plot_lim / ncols))

        # Limit the number of plots on a figure
        index = 0
        bands_remaining = numBands

        # Plot the correct amount of data for each figure
        while bands_remaining > plot_lim:
            self._update_fig()
            # Plot the data for each band
            for band in range(0, plot_lim):
                plt.subplot(nrows, ncols, band + 1)
                # Get limits and offset band index
                band = band + index * plot_lim  # - Offset the band to account for the bands already plotted
                if band_range == 'solar':
                    band = band + len(self.data.wl1_earth)
                low_wave, high_wave, band_index = self._get_band_limits(band, given_band_index=True)
                plt.title("Band " + str(band + 1) + ': ' + str(low_wave) + '-' + str(high_wave) + self.data.wave_units)
                # Plot the correct data for the specified band range
                self._single(band, new_fig=False, datatype=datatype, time=time, divs=divs)
            # Format the current figure
            plt.suptitle(
                datatype.upper() + " allbands plot " + str(index+1) + " of " + str(int(np.ceil((numBands / plot_lim)))))
            plt.tight_layout(pad=spacing)
            plt.subplots_adjust(top=top)
            if save_fig:
                if save_name is None:
                    save_name = datatype.upper() + '_allbands--' + self.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '.png'
                self.save(save_name=save_name)
            # Update iterating values
            bands_remaining = bands_remaining - plot_lim
            index = index+1
        self._update_fig()

        # Plot the remaining data on the last figure
        for band in range(0, bands_remaining):
            plt.subplot(nrows, ncols, band + 1)
            band = band + index * plot_lim
            if band_range == 'solar':
                band = band + len(self.data.wl1_earth)
            low_wave, high_wave, band_index = self._get_band_limits(band, given_band_index=True)
            plt.title("Band " + str(band + 1) + ': ' + str(low_wave) + '-' + str(high_wave) + self.data.wave_units)
            self._single(band, new_fig=False, datatype=datatype, time=time, divs=divs)
        # Format the plot
        plt.suptitle(datatype.upper() + " allbands plot " + str(index+1) + " of " + str(int(np.ceil((numBands/plot_lim)))))
        plt.tight_layout(pad=spacing)
        plt.subplots_adjust(top=top)
        if save_fig:
            if save_name is None:
                save_name = datatype.upper() + '_allbands--' + self.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '.png'
            self.save(save_name=save_name)

    def _allbands_multi(self, band_range='all', time='mean', spacing=1.5, top=0.85,
                 save_fig=False, save_name=None, divs=10):
        """
         Plots all bands of data for all four data types. Always makes 2x2 figures.
        :param band_range: string, specifies the bands to be plotted - 'all', 'terrestrial' or 'solar'
        :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
        :param spacing: Sets the spacing of the plots from each other
        :param top: Sets the spacing of the plots from the top of the figure
        :param save_fig: Boolean which determines if this figure will be saved
        :param save_name: String which sets the name of the saved figure, if it is to be saved.
        :param divs: Sets the number of colorbar divisions to be used
        :return: None
        """
        assert band_range == 'all' or band_range == 'terrestrial' or band_range == 'solar', \
            "band_range argument not recognized - acceptable values are 'all', 'terrestrial' or 'solar' "
        if band_range == 'all':
            numBands = len(self.data.wl1_earth) + len(self.data.wl1_sun)
        elif band_range == 'terrestrial':
            numBands = len(self.data.wl1_earth)
        else:
            numBands = len(self.data.wl1_sun)
        # Determine the number of subplots needed and the arrangement
        # For these multiplots, will limit to 2x2 plots.
        nrows = 2
        ncols = 2
        # Plot the data for each band
        for band in range(0, numBands):
            if band_range == 'all' or band_range == 'terrestrial':
                index = band
            else:  # Need offset for solar bands
                index = band + len(self.data.wl1_earth)
            low_wave, high_wave, band_index = self._get_band_limits(index, given_band_index=True)
            self._update_fig()
            plt.subplot(nrows, ncols, 1)
            plt.title("AOD: Band " + str(band + 1))
            self._single(index, new_fig=False, datatype='aod', time=time, divs=divs)
            plt.subplot(nrows, ncols, 2)
            plt.title("EXT: Band " + str(band + 1))
            self._single(index, new_fig=False, datatype='ext', time=time, divs=divs)
            plt.subplot(nrows, ncols, 3)
            plt.title("SSA: Band " + str(band + 1))
            self._single(index, new_fig=False, datatype='ssa', time=time, divs=divs)
            plt.subplot(nrows, ncols, 4)
            plt.title("ASY: Band " + str(band + 1))
            self._single(index, new_fig=False, datatype='asy', time=time, divs=divs)
            plt.tight_layout(pad=spacing)
            plt.subplots_adjust(top=top)
            plt.suptitle("Allbands: Band " + str(band+1) + " of " + str(numBands) + " (Band "
                         + str(index+1) + ": " + str(low_wave) + '-' + str(high_wave) + self.data.wave_units + ")")
            if save_fig:
                if save_name is None:
                    save_name = datatype + '_allbands--' + self.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '.png'
                self.save(save_name=save_name)

    def _get_z_data(self, datatype, band, time='mean'):
        """
        Finds the scaled z data for this datatype in the specified band
        :param datatype: String to specify the type of data to be analyzed. 'aod', 'ext', 'ssa' or 'asy'.
        :param band: int representing the wavelength band to be analyzed
        :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
        :return: Array containing the calculated z data.
        """

        # Ensure input time is valid
        if time != 'mean':
            try:
                time = float(time)
            except ValueError:
                print("Time argument not recognized - acceptable strings contain 'mean' or a float.")
        if datatype == 'aod':
            # Check if aod data exists yet, calculate it if not
            if self.data.aod_earth is None:
                self.data.calc_aod()
            # Check which band range this data is in
            if band < len(self.data.wl1_earth):
                z_data = self.data.aod_earth
            else:
                z_data = self.data.aod_sun
                band = band - len(self.data.wl1_earth)
            z_mean = self.aod_scale * z_data[:, band, :]
        elif datatype == 'ext':
            # Check which band range this data is in
            if band < len(self.data.wl1_earth):
                z_data = self.data.ext_earth
            else:
                z_data = self.data.ext_sun
                band = band - len(self.data.wl1_earth)
            # Get the z data for the correct time
            if time == 'mean':
                z_mean = self.ext_scale * np.mean(z_data[:, band, :, :], 0)  # -- Adjust scaling
            else:
                # Check time is in the valid range
                if time < min(self.data.time) or time > max(self.data.time):
                    sys.exit('Error in _single(): Input time is not in the valid range for this data.')
                else:
                    # Find index of given time
                    half_step = float(self.data.time[1] - self.data.time[0]) / 2
                    time_index = None
                    for index, value in enumerate(self.data.time):
                        if time + half_step >= value > time - half_step:
                            time_index = index
                    try:
                        z_mean = self.ext_scale * z_data[time_index, band, :, :]
                    except:
                        Exception('Error in _single(): Could not create z array for this time index.')
        elif datatype == 'ssa':
            # Check which band range this data is in
            if band < len(self.data.wl1_earth):
                z_data = self.data.ssa_earth
            else:
                z_data = self.data.ssa_sun
                band = band - len(self.data.wl1_earth)
            # Set the z data for the correct time
            if time == 'mean':
                z_mean = self.ssa_scale * np.mean(z_data[:, band, :, :], 0)  # -- Adjust scaling
            else:
                # Check time is in the valid range
                if time < min(self.data.time) or time > max(self.data.time):
                    sys.exit('Error in _single(): Input time is not in the valid range for this data.')
                else:
                    # Find index of given time
                    half_step = float(self.data.time[1] - self.data.time[0]) / 2
                    time_index = None
                    for index, value in enumerate(self.data.time):
                        if time + half_step >= value > time - half_step:
                            time_index = index
                    try:
                        z_mean = self.ssa_scale * z_data[time_index, band, :, :]
                    except:
                        print('Error in _single(): Could not find create z array for this time index.')
        elif datatype == 'asy':
            # Check which band range this data is in
            if band < len(self.data.wl1_earth):
                z_data = self.data.asy_earth
            else:
                z_data = self.data.asy_sun
                band = band - len(self.data.wl1_earth)
            # Set the z data for the correct time
            if time == 'mean':
                z_mean = self.asy_scale * np.mean(z_data[:, band, :, :], 0)  # -- Adjust scaling
            else:
                # Check time is in the valid range
                if time < min(self.data.time) or time > max(self.data.time):
                    sys.exit('Error in _single(): Input time is not in the valid range for this data.')
                else:
                    # Find index of given time
                    half_step = float(self.data.time[1] - self.data.time[0]) / 2
                    time_index = None
                    for index, value in enumerate(self.data.time):
                        if time + half_step >= value > time - half_step:
                            time_index = index
                    try:
                        z_mean = self.asy_scale * z_data[time_index, band, :, :]
                    except:
                        print('Error in _single(): Could not find create z array for this time index.')
        else:
            print('Error in _get_z_data() - Unrecognized data type: ' + datatype)
            return None
        return z_mean

    def _single(self, band, new_fig=True, datatype='multi', time='mean', divs=10, level_divs=None):
        """
        Builds a single plot for the given band, time, and datatype.
        :param band: index of wavelength band to be plotted
        :param new_fig: specifies if a new figure should be created for this plot.
        :param datatype: String to specify the type of data to be plotted. 'multi', 'aod', 'ext', 'ssa' or 'asy'.
        :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
        :param divs: Sets the number of colorbar dvisions that will be created, if level_divs is not given
        :param level_divs: Array containing the colorbar divisions that will be used. If none, level_divs will be built.
        :return: None
        """
        # Check input datatype is valid
        assert datatype == 'multi' or datatype == 'aod' or datatype == 'ext' or datatype == 'asy' or datatype == 'ssa',\
            "datatype argument not recognized - acceptable values are 'multi', 'aod', 'ext', 'asy', or 'ssa'."
        # Check input time is valid

        if new_fig:
            self._update_fig()
        if datatype == 'multi':
            # Build the multiplot by calling single recursively.
            plt.subplot(2, 2, 1)
            self._single(band, new_fig=False, datatype='aod', time=time, divs=divs, level_divs=level_divs)
            plt.subplot(2, 2, 2)
            self._single(band, new_fig=False, datatype='ext', time=time, divs=divs, level_divs=level_divs)
            plt.subplot(2, 2, 3)
            self._single(band, new_fig=False, datatype='ssa', time=time, divs=divs, level_divs=level_divs)
            plt.subplot(2, 2, 4)
            self._single(band, new_fig=False, datatype='asy', time=time, divs=divs, level_divs=level_divs)
            plt.tight_layout(pad=2)
            return

        # Calculate the scaled mean z data for this datatype
        z_mean = self._get_z_data(datatype, band, time=time)

        # Set the data to be plotted
        if datatype == 'aod':
            x_data = self.data.time
            y_data = self.data.lat
            # Set the colorbar divisions - should start at 0 for aod
            if level_divs is None:
                level_divs = np.linspace(0, np.ceil(np.max(z_mean)), divs)
            # Build the plot
            self._plot_single(x_data, y_data, z_mean, datatype='aod',
                              level_divs=level_divs, divs=divs)
        elif datatype == 'ext':
            # Set the data that will be used
            x_data = self.data.lat
            y_data = self.data.alt
            # Set the colorbar divisions - should start at 0 for ext
            if level_divs is None:
                level_divs = np.linspace(0, np.ceil(np.max(z_mean)), divs)
            # Build the plot
            self._plot_single(x_data, y_data, z_mean, datatype=datatype,
                              level_divs=level_divs, divs=divs)
        elif datatype == 'ssa' or datatype == 'asy':
            # Set the data we will be plotting
            x_data = self.data.lat
            y_data = self.data.alt
            # Set the divisions to use for the colorbar
            if level_divs is None:
                level_divs = np.linspace(np.amin(z_mean), np.amax(z_mean), divs)
            # Build the plot
            self._plot_single(x_data, y_data, z_mean, datatype=datatype,
                              level_divs=level_divs, divs=divs)
        else:
            print('Unknown error: If you see this, something broke in _single()')
            return None

    def _plot_single(self, x_data, y_data, z_mean, datatype='ext', colorbar_label=None, level_divs=None, divs=10):
        """
        Builds the 3D contourf plot, given the data for the plot.
        :param x_data: Data list for the x-axis
        :param y_data: Data list for the y-axis
        :param z_mean: Data list for z-axis, usually a mean.
        :param datatype: The type of data being plotted. 'aod', 'ext', 'ssa', or 'asy'.
        :param colorbar_label: String label for the colorbar
        :return: None
        """
        if level_divs is None:
            level_divs = np.linspace(np.amin(z_mean), np.amax(z_mean), divs)
        # Make sure there is actually varying data here to be plotted, adjust division levels if not
        if max(level_divs) <= min(level_divs):
            level_divs = np.linspace(np.amin(z_mean), np.amax(z_mean)+1e-14, 1)
        # Draw filled contours
        cmap = plt.cm.get_cmap('hot_r')
        cnplot = plt.contourf(x_data, y_data, z_mean.transpose(), divs,
                              cmap=cmap, extend='both')

        # Format x axis
        if datatype == 'aod':
            # -- Format x axis if time scale is too small for normal aod ticks (two years)
            max_x = np.ceil(max(self.data.time))  # Round up to nearest integer
            min_x = np.floor(min(self.data.time))  # Round down to nearest integer
            if max_x - min_x < 2:
                num_xticks = 5
                xtick_locations = np.arange(min_x, max_x, (max_x - min_x) / num_xticks)
                rounded_xticks = [round(elem, 2) for elem in xtick_locations]
                plt.xticks(xtick_locations, rounded_xticks, rotation=45)
            # Set the plotting labels
            colorbar_label = 'AOD x ' + "{:.0e}".format(self.aod_scale)
            xlabel = ('Time, ' + self.data.time_units)
            ylabel = ('Latitude, ' + self.data.lat_units)

        elif datatype == 'ext':
            # Set the plot labels
            colorbar_label = 'EXT x ' + "{:.0e}".format(self.ext_scale) + " (" + self.data.ext_units + ")"
            xlabel = ('Latitude, ' + self.data.lat_units)
            ylabel = ('Altitude, ' + self.data.alt_units)
            x_ticks = [int(elem) for elem in np.linspace(-90, 90, 5)]
            plt.xticks(x_ticks, x_ticks)

        elif datatype == 'ssa':
            # Set the labels for the plot
            colorbar_label = 'SSA x ' + "{:.0e}".format(self.ssa_scale)
            xlabel = ('Latitude, ' + self.data.lat_units)
            ylabel = ('Altitude, ' + self.data.alt_units)
            x_ticks = [int(elem) for elem in np.linspace(-90, 90, 5)]
            plt.xticks(x_ticks, x_ticks)

        elif datatype == 'asy':
            # Set the labels for the plot
            colorbar_label = 'ASY x ' + "{:.0e}".format(self.asy_scale)
            xlabel = ('Latitude, ' + self.data.lat_units)
            ylabel = ('Altitude, ' + self.data.alt_units)
            x_ticks = [int(elem) for elem in np.linspace(-90, 90, 5)]
            plt.xticks(x_ticks, x_ticks)
        else:
            sys.exit('Unrecognized datatype' + str(datatype))

        # Add colorbar
        cbar = plt.colorbar(cnplot, orientation='vertical')  # pad: distance between map and colorbar
        cbar.set_label(colorbar_label)  # add colorbar title string
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

    def plot_gm_aod(self, new_fig=True, formataxis=True, label=None, wavelength=DEFAULT_WAVELENGTH):
        """
        Plots the global mean aerial optical depth over time.
        :param new_fig: Sets if the data should be plotted on a new figure
        :param formataxis: Sets if x axis should be manually formatted. If false, default python settings will be used.
        :param label: Sets the label for the plotted line.
        :param wavelength: Specifies the wavelength to plot aod data for. If 'None' is given, will take average of wavelengths.
        :return: None
        """
        if new_fig:
            self._update_fig()
        # Check if aod data exists yet, calculate it if not
        if self.data.aod_earth is None:
            self.data.calc_aod()
        # Create arrays to be filled
        weighted_lat = np.zeros(len(self.data.lat))
        gm_aod = np.zeros(len(self.data.time))
        # Check if a particular wavelength is specified
        if wavelength is None:  # Will average across bands if no wavelength given
            aod = np.zeros([len(self.data.lat), len(self.data.time)])
            # Calculate the weighted latitude data
            weighted_lat[:] = np.cos(self.data.lat[:] * np.pi / 180)
            weighted_lat[:] = weighted_lat[:] / sum(weighted_lat[:])
            # Average the aod across all bands
            aod = np.sum(self.data.aod_earth[:, :, :], 1) + np.sum(self.data.aod_sun[:, :, :], 1)
            aod = aod / (len(self.data.aod_earth[0, :, 0]) + len(self.data.aod_sun[0, :, 0]))
            # Fill the gm_aod with the properly weighed data
            gm_aod[:] = np.inner(np.sum(weighted_lat * aod[:, :]), weighted_lat)
        else:  # if a wavelength is specified, only plot for that band
            # Determine the band and aod data to use
            band = self._determine_wavelength(wavelength)
            if band >= len(self.data.wl1_earth):
                aod_in = self.data.aod_sun
                band_index = band-len(self.data.wl1_earth)
            else:
                aod_in = self.data.aod_earth
                band_index = band
            # Calculate the weighted latitude data
            weighted_lat[:] = np.cos(self.data.lat[:] * np.pi/180)
            weighted_lat[:] = weighted_lat[:] / sum(weighted_lat[:])
            # Fill the gm_aod with the properly weighed aod data
            gm_aod[:] = np.inner(aod_in[:, band_index, :], weighted_lat)
        # Plot the data
        plt.plot(self.data.time, gm_aod, '.-', label=label)
        if wavelength is None:
            plt.title("Global Mean AOD Trend: Average of all bands")
        else:
            plt.title("Global Mean AOD Trend at Wavelength: " + str(wavelength) + str(self.data.wave_units))
        plt.xlabel("Time (" + self.data.time_units + ")")
        plt.ylabel("Global Mean AOD at lambda = " + str(wavelength))
        if formataxis:
            # -- Format x axis if time scale is too small for normal ticks (two years)
            max_x = np.ceil(max(self.data.time))  # Round up to nearest integer
            min_x = np.floor(min(self.data.time))  # Round down to nearest integer
            if max_x - min_x < 2:
                num_xticks = 5
                xtick_locations = np.arange(min_x, max_x, (max_x - min_x) / num_xticks)
                rounded_xticks = [round(elem, 2) for elem in xtick_locations]
                plt.xticks(xtick_locations, rounded_xticks, rotation=45)
            plt.gca().set_ylim(bottom=0)


def plot_at_wavelength(wavelength, *files, datatype='multi', time='mean', save_fig=False, save_name=None, plot_lim=4,
                       ncols=2,  spacing=1.5, top=0.85, get_years=False, divisions=10, display=True):
    """
    Plots the data from each given file at the given wavelength.
    :param wavelength: The wavelength to be plotted at
    :param files: Input data files - either a file path string, or a ReadNCData object
    :param datatype: sets which data will be plotted, ext, aod, asy, or ssa
    :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
    :param save_fig: Boolean which sets if a png of the data plot will be saved.
    :param save_name: If the data is to be saved, this can set a name for the save file.
    :param plot_lim: Limits the total number of plots on a figure
    :param ncols: Limits the maximum number of columns on a figure
    :param spacing: Adjusts the spacing between subplots plots on a figure
    :param top: Adjusts the spacing between the top of the figure and the subplots
    :param get_years: Boolean, sets if the time for the data file should be converted to years, if it is not by default.
    :param divisions: Int, specifies the number of colorbar divisions that should be used.
    :param display: Boolean, sets if the created plot should be displayed.
    :return: None
    """
    assert isinstance(wavelength, float) or isinstance(wavelength, int), 'Wavelength should be a float or int.'
    assert files is not None or files.size != 0, 'Must input at least one file'
    assert datatype == 'multi' or datatype == 'ext' or datatype == 'aod' or datatype == 'asy' or datatype == 'ssa', \
        'Invalid datatype - must be ext, aod, asy, or ssa'
    if datatype == 'multi':
        plot_lim = 1
    numFiles = len(files)
    # Limit columns if the plot is limited to 1
    if plot_lim == 1:
        ncols = 1
    # Determine the number of subplots needed and the arrangement
    # Determine the number of rows needed
    if numFiles <= ncols:
        nrows = 1
        ncols = numFiles
    else:
        nrows = int(np.ceil(plot_lim / ncols))

    # Limit the number of plots on a figure
    index = 1
    files_remaining = numFiles
    # Plot the correct amount of data for each figure
    while files_remaining > plot_lim:
        plotter = PlotEVA(files[numFiles-files_remaining], get_years=get_years)
        plotter._update_fig()
        # Plot the data for each band
        for file in range(0, plot_lim):
            plotter = PlotEVA(files[numFiles-files_remaining], get_years=get_years)
            plt.subplot(nrows, ncols, file + 1)
            file = file + (index - 1) * plot_lim
            # Plot the correct data for the specified band range
            low_wave, high_wave, band_index = plotter.wavelength(wavelength, new_fig=False, datatype=datatype,
                                                                 time=time, divs=divisions)
            plt.title("File " + str(file + 1) + " " + "(Band " + str(band_index+1) + ': ' + str(low_wave) + "-" + str(
                high_wave) + plotter.data.wave_units + ")")
            files_remaining -= 1
        # Format the current figure
        plt.suptitle(str(wavelength) + plotter.data.wave_units + ": " + datatype.upper() + " Comparision Plot " + str(index) +
                     " of " + str(int(np.ceil((numFiles / plot_lim)))))
        plt.tight_layout(pad=spacing)
        plt.subplots_adjust(top=top)
        # Save the current figure
        if save_fig:
            if save_name is None:
                if len(files) == 1:
                    save_name = datatype.upper() + '_' + str(wavelength) + str(plotter.data.wave_units).replace(" ",
                                                                                                        "") + '--' + \
                                plotter.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '.png'
                else:
                    save_name = datatype.upper() + '_' + str(wavelength) + str(plotter.data.wave_units) + '_comparison'\
                                                                                                  '-MultipleInputs.png'
            plotter.save(save_name=save_name)
        # Update iterating values
        index = index + 1

    # Plot the remaining data on the last figure
    plotter = PlotEVA(files[numFiles-files_remaining], get_years=get_years)
    plotter._update_fig()
    for file in range(0, files_remaining):
        plotter = PlotEVA(files[numFiles-files_remaining], get_years=get_years)
        plt.subplot(nrows, ncols, file + 1)
        file = file + (index-1) * plot_lim
        low_wave, high_wave, band_index = plotter._get_band_limits(wavelength)
        plotter.wavelength(wavelength, new_fig=False, datatype=datatype, time=time,
                           divs=divisions)
        plt.title("File " + str(file + 1) + " " + "(Band " + str(band_index+1) + ': ' + str(low_wave) + "-" + str(
            high_wave) + plotter.data.wave_units + ")")
        files_remaining -= 1
    # Format the plot
    if numFiles > plot_lim:
        plt.suptitle(datatype.upper() + " comparison plot " + str(index) + " of " + str(int(np.ceil((numFiles / plot_lim)))))
    elif numFiles > 1:
        plt.suptitle(datatype.upper() + " comparison at wavelength: " + str(wavelength) + " " + plotter.data.wave_units)
    else:
        plt.suptitle(datatype.upper() + " at wavelength: " + str(wavelength) + " " + plotter.data.wave_units)
    plt.tight_layout(pad=spacing)
    plt.subplots_adjust(top=top)
    # Save the current figure
    if save_fig:
        if save_name is None:
            if len(files) == 1:
                save_name = datatype.upper() + '_' + str(wavelength) + str(plotter.data.wave_units).replace(" ",
                                                                                                    "") + '--' + \
                            plotter.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '.png'
            else:
                save_name = datatype.upper() + '_' + str(wavelength) + str(plotter.data.wave_units) + '_comparison' \
                                                                                              '-MultipleInputs.png'
        plotter.save(save_name=save_name)
    # Display the figure
    if display:
        plotter.show()


def plot_difference(wavelength, file1, file2, datatype='multi', time='mean', save_fig=False, save_name=None,
                    get_years=True, divisions=10, display=True):
    """
    Plots the difference in the datatype specified, at the specified wavelength, for these two files (file1-file2).
    :param wavelength: The wavelength for data to be plotted at.
    :param file1: First data file
    :param file2: Second data file
    :param datatype: The type of data to be plotted: String containing 'multi', 'aod', 'ext', 'ssa', or 'asy'.
    :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
    :param save_fig: Boolean specifying if the figure should be saved to the current directory.
    :param save_name: Name to be saved under, if save_fig=True. Will create a default name if save_name=None
    :param get_years: Boolean, sets if the time for the data file should be converted to years, if it is not by default.
    :param divisions: Int, specifies the number of colorbar divisions that should be used.
    :param display: Boolean, sets if the created plot should be displayed.
    :return: None
    """

    plotter1 = PlotEVA(file1, get_years=get_years)
    plotter2 = PlotEVA(file2, get_years=get_years)
    band1 = plotter1._determine_wavelength(wavelength)
    band2 = plotter2._determine_wavelength(wavelength)
    assert band1 != -1, "Wavelength not found."
    assert datatype == 'multi' or datatype == 'aod' or datatype == 'ext' or datatype == 'ssa' or datatype == 'asy',\
        "Unrecognized datatype: " + datatype
    if datatype == 'multi':
        # Build the multiplot by calling single recursively.
        plt.subplot(2, 2, 1)
        plot_difference(wavelength, file1, file2, datatype='aod', time=time, save_fig=False, display=False,
                        get_years=get_years, divisions=divisions)
        plt.subplot(2, 2, 2)
        plot_difference(wavelength, file1, file2, datatype='ext', time=time, save_fig=False, display=False,
                        get_years=get_years, divisions=divisions)
        plt.subplot(2, 2, 3)
        plot_difference(wavelength, file1, file2, datatype='ssa', time=time, save_fig=False, display=False,
                        get_years=get_years, divisions=divisions)
        plt.subplot(2, 2, 4)
        plot_difference(wavelength, file1, file2, datatype='asy', time=time, save_fig=False, display=False,
                        get_years=get_years, divisions=divisions)
        plt.tight_layout(pad=2)
    elif datatype == 'aod':
        # Check if aod data exists yet, calculate it if not
        if plotter1.data.aod_earth is None:
            plotter1.data.calc_aod()
        if plotter2.data.aod_earth is None:
            plotter2.data.calc_aod()
        # For AOD, need to fit the times together to show the difference
        # Find the overlapping limits
        min_time = max([min(plotter1.data.time), min(plotter2.data.time)])
        max_time = min([max(plotter1.data.time), max(plotter2.data.time)])
        # Trim the time and aod length of the first dataset
        min_index = 0
        max_index = len(plotter1.data.time) - 1
        for index, time in enumerate(plotter1.data.time):
            if time < min_time:
                min_index = index + 1
            if time > max_time:
                max_index = index - 1
        # Set the aod to the relevant bands
        if band1 < len(plotter1.data.wl1_earth):
            aod_1 = plotter1.data.aod_earth[:, band1, :]
        else:
            band1 = band1 - len(plotter1.data.wl1_earth)
            aod_1 = plotter1.data.aod_sun[:, band1, :]

        if band2 < len(plotter2.data.wl1_earth):
            aod_2 = plotter2.data.aod_earth[:, band2, :]
        else:
            band2 = band2 - len(plotter2.data.wl1_earth)
            aod_2 = plotter2.data.aod_sun[:, band2, :]

        plotter1.data.time = plotter1.data.time[min_index:max_index]
        aod_1 = aod_1[min_index:max_index, :]
        # Trim the time and aod length of the second dataset
        min_index = 0
        max_index = len(plotter2.data.time) - 1
        for index, time in enumerate(plotter2.data.time):
            if time < min_time:
                min_index = index+1
            if time > max_time:
                max_index = index-1
        plotter2.data.time = plotter2.data.time[min_index:max_index]
        aod_2 = aod_2[min_index:max_index]
        # Determine which dataset is larger than the other
        if len(plotter1.data.time) > len(plotter2.data.time):
            long_time = plotter1.data.time[:]
            long_aod = aod_1[:, :]
            short_time = plotter2.data.time
            short_aod = aod_2[:, :]
            short = 2
        else:
            long_time = plotter2.data.time
            long_aod = aod_2[:, :]
            short_time = plotter1.data.time
            short_aod = aod_1[:, :]
            short = 1
        # Calculate a shorter aod for the long dataset using a weighted average of the nearest points
        new_aod = np.zeros([len(short_time), len(short_aod[0, :])])
        for index, time in enumerate(short_time):
            for index2, time2 in enumerate(long_time):
                if time2 > time:
                    high_index = index2
                    high_time = time2
                    low_index = index2 - 1
                    low_time = long_time[index2-1]
                    break
            weight = (time-low_time)/(high_time-low_time)
    #        print((long_earth[high_index, :, :] - long_earth[low_index, :, :]) * weight + long_earth[low_index, :, :])
            new_aod[index, :] = (long_aod[high_index, :]-long_aod[low_index, :])*weight + long_aod[low_index, :]
        # Plot the correct time and aod data
        if short == 2:
            plotter1.data.time = plotter2.data.time[:]
            z_mean1 = AOD_SCALE * new_aod[:, :]
            z_mean2 = AOD_SCALE * short_aod[:, :]
        else:
            plotter2.data.time = plotter1.data.time[:]
            z_mean1 = AOD_SCALE * short_aod[:, :]
            z_mean2 = AOD_SCALE * new_aod[:, :]
        plotter1._plot_single(plotter1.data.time, plotter1.data.lat, z_mean1-z_mean2, datatype='aod')

    else:
        # Calculate and plot the difference
        z_mean1 = plotter1._get_z_data(datatype=datatype, band=band1, time=time)
        z_mean2 = plotter2._get_z_data(datatype=datatype, band=band2, time=time)
        plotter1._plot_single(plotter1.data.lat, plotter1.data.alt, z_mean1-z_mean2)

    # Set the title
    plt.suptitle('Difference in ' + datatype.upper() + ' at ' + str(wavelength) + str(plotter1.data.wave_units) )
    # Save the current figure
    if save_fig:
        if save_name is None:
            save_name = datatype + '_' + str(wavelength) + str(plotter1.data.wave_units) + '_difference_plot.png'
        plotter1.save(save_name=save_name)
    # Display the figure
    if display:
        plotter1.show()


def plot_all_bands(*files, save_fig=False, save_name=None, band_range='all', datatype='multi', time='mean', plot_lim=4,
                   ncols=2,  spacing=1.5, top=0.85, get_years=False, divisions=10, display=True):
    """
       Plots all bands of data for this data type
       :param save_name: String, sets the save name if this figure is to be saved
       :param save_fig: Boolean sets if the figures created should be saved
       :param band_range: string, specifies the bands to be plotted - 'all', 'terrestrial' or 'solar'
       :param datatype: Specifies the type of data all bands will be plotted for
       :param time: String 'mean' or a numeric value representing a specific time for the data to be plotted at.
       :param plot_lim: sets the limit on the number of subplots per figure
       :param ncols: sets the number of subplot columns for each figure
       :param spacing: sets the spacing between subplots
       :param top: sets the spacing between the subplots and the top of the figure
       :param get_years: Sets if years are to be used as the time division, even if file is in another time unit.
       :param divisions: Sets the number of colobar divisions to be used.
       :param display: Sets if the created plot(s) should be displayed.
       :return: None
   """
    assert files is not None or files.size != 0, 'Must input at least one file'
    if save_fig:
        if save_name is None:
            if len(files) != 1:
                save_name = datatype.upper() + '_allbands--MultipleInputs.png'
    for filenum, file in enumerate(files):
        plotter = PlotEVA(file, get_years=get_years)
        plotter.allbands(band_range=band_range, datatype=datatype, time=time, plot_lim=plot_lim, ncols=ncols,
                         spacing=spacing, top=top, save_fig=save_fig, save_name=save_name, divs=divisions)
    if display:
        plotter.show()


def plotGlobalMeanAOD(*files, save_fig=False, save_name=None, wavelength=DEFAULT_WAVELENGTH, display=True, legend=True):
    """
    Plots the global mean aod over time, for one or multiple files.
    :param files: Input data, can be the file path as a string, or a ReadNCData object.
    :param save_fig: Sets if the figure will be automatically saved or not.
    :param save_name: If the figure will be saved, sets the name to save it under.
    :param wavelength: Sets the wavelength for which we are analyzing the data.
    :param display: Sets if plot should be displayed.
    :return: None
    """
    assert files is not None or len(files) != 0, 'Must input at least one file'
    max_x = None
    min_x = None
    get_years = (len(files) > 1)
    for file in files:
        # Check if input is a string (file location)
        plotter = PlotEVA(file, get_years=get_years)
        low_wave, high_wave, band_index = plotter._get_band_limits(wavelength)
        label = plotter.data.file.split('\\')[-1] + ' (Band ' + str(band_index+1) + ': ' + str(low_wave) + '-' + str(high_wave) + ')'
        plotter.plot_gm_aod(new_fig=False, formataxis=False, label=label, wavelength=wavelength)
        if max_x is None or np.ceil(np.max(plotter.data.time)) > max_x:
            max_x = np.ceil(np.max(plotter.data.time))  # Round up to nearest integer
        if min_x is None or np.ceil(np.min(plotter.data.time)) < min_x:
            min_x = np.floor(np.min(plotter.data.time))  # Round down to nearest integer
    if max_x - min_x < 2:
        num_xticks = 10.0
        xtick_locations = np.arange(min_x, max_x, (max_x - min_x) / num_xticks)
        rounded_xticks = [round(elem, 2) for elem in xtick_locations]
        plt.xticks(xtick_locations, rounded_xticks, rotation=45)
    if legend:
        plt.legend()
    plt.gca().set_ylim(bottom=0)
    if save_fig:
        if save_name is None:
            if len(files) == 1:
                save_name = plotter.data.file.split('\\')[-1].rsplit('.nc', 1)[0] + '_gmAOD.png'
            else:
                save_name = 'gmAOD-MultipleInputs.png'

        plotter.save(save_name=save_name)
    if display:
       plotter.show()


def get_data(file):
    """
    Gets the data from a file
    :param file: string path to an NC data file
    :return: a ReadNCData object containing the data
    """
    return ReadNCData(file)


if __name__ == "__main__":
    function = sys.argv[1]
    arguments = sys.argv[2:]
    if function == 'plot_at_wavelength' or function == 'wavelength':
        # Determine the special arguments that have been specified
        datatype = 'multi'
        time = 'mean'
        save_fig = False
        save_name = None
        plot_lim = 4
        ncols = 2
        spacing = 1.5
        top = 0.85
        divisions = 10
        display = True
        # Check for special arguments
        for arg in arguments:
            if '=' in arg:
                split_arg = arg.split('=')
                if split_arg[0] == 'datatype':
                    datatype = split_arg[1]
                elif split_arg[0] == 'time':
                    time = split_arg[1]
                elif split_arg[0] == 'save_fig':
                    save_fig = (split_arg[1] == 'True')
                elif split_arg[0] == 'save_name':
                    save_name = split_arg[1]
                elif split_arg[0] == 'plot_lim':
                    plot_lim = int(split_arg[1])
                elif split_arg[0] == 'ncols':
                    ncols = int(split_arg[1])
                elif split_arg[0] == 'spacing':
                    spacing = float(split_arg[1])
                elif split_arg[0] == 'top':
                    top = float(split_arg[1])
                elif split_arg[0] == 'divisions':
                    divisions = int(split_arg[1])
                elif split_arg[0] == 'display':
                    display = (split_arg[1] == 'True')
                else:
                    sys.exit("Unrecognized argument '" + arg + "'")
        # Remove any special arguments from the list
        arguments = [arg for arg in arguments if '=' not in arg]
        plot_at_wavelength(float(arguments[0]), *arguments[1:], datatype=datatype, time=time, save_fig=save_fig,
                           save_name=save_name, plot_lim=plot_lim, ncols=ncols, spacing=spacing, top=top,
                           divisions=divisions, display=display)
    elif function == 'plotGlobalMeanAOD' or function == 'gmAOD':
        # Set the defaults for any special arguments
        save_fig = False
        save_name = None
        wavelength = DEFAULT_WAVELENGTH
        display = True
        # Check for special arguments
        for arg in arguments:
            if '=' in arg:
                split_arg = arg.split('=')
                if split_arg[0] == 'save_fig':
                    save_fig = (split_arg[1] == 'True')
                elif split_arg[0] == 'save_name':
                    save_name = split_arg[1]
                elif split_arg[0] == 'wavelength':
                    wavelength = float(split_arg[1])
                elif split_arg[0] == 'display':
                    display = (split_arg[1] == 'True')
                else:
                    sys.exit("Unrecognized argument '" + arg + "'")
        # Remove any special arguments from the list
        arguments = [arg for arg in arguments if '=' not in arg]
        plotGlobalMeanAOD(*arguments[0:], save_fig=save_fig, save_name=save_name, wavelength=wavelength, display=display)
    elif function == 'plot_all_bands' or function == 'allbands':
        # Determine the special arguments that have been specified
        datatype = 'multi'
        time = 'mean'
        save_fig = False
        save_name = None
        plot_lim = 4
        ncols = 2
        spacing = 1.5
        top = 0.85
        divisions = 10
        band_range = 'all'
        display = True
        # Check for special arguments
        for arg in arguments:
            if '=' in arg:
                split_arg = arg.split('=')
                if split_arg[0] == 'datatype':
                    datatype = split_arg[1]
                elif split_arg[0] == 'time':
                    time = split_arg[1]
                elif split_arg[0] == 'save_fig':
                    save_fig = (split_arg[1] == 'True')
                elif split_arg[0] == 'save_name':
                    save_name = split_arg[1]
                elif split_arg[0] == 'plot_lim':
                    plot_lim = int(split_arg[1])
                elif split_arg[0] == 'ncols':
                    ncols = int(split_arg[1])
                elif split_arg[0] == 'spacing':
                    spacing = float(split_arg[1])
                elif split_arg[0] == 'top':
                    top = float(split_arg[1])
                elif split_arg[0] == 'divisions':
                    divisions = int(split_arg[1])
                elif split_arg[0] == 'band_range':
                    band_range = split_arg[1]
                elif split_arg[0] == 'display':
                    display = (split_arg[1] == 'True')
                else:
                    sys.exit("Unrecognized argument '" + arg + "'")
        # Remove any special arguments from the list
        arguments = [arg for arg in arguments if '=' not in arg]
        plot_all_bands(*arguments, save_fig=save_fig, save_name=save_name, band_range=band_range, datatype=datatype,
                       time=time, plot_lim=plot_lim, ncols=ncols, spacing=spacing, top=top, display=display)
    elif function == 'plot_difference' or function == 'difference':
        # Determine the special arguments that have been specified
        datatype = 'multi'
        time = 'mean'
        save_fig = False
        save_name = None
        divisions = 10
        get_years = True
        display = True
        # Check for special arguments
        for arg in arguments:
            if '=' in arg:
                split_arg = arg.split('=')
                if split_arg[0] == 'datatype':
                    datatype = split_arg[1]
                elif split_arg[0] == 'time':
                    time = split_arg[1]
                elif split_arg[0] == 'save_fig':
                    save_fig = (split_arg[1] == 'True')
                elif split_arg[0] == 'save_name':
                    save_name = split_arg[1]
                elif split_arg[0] == 'divisions':
                    divisions = int(split_arg[1])
                elif split_arg[0] == 'get_years':
                    get_years = (split_arg[1] == 'True')
                elif split_arg[0] == 'display':
                    display = (split_arg[1] == 'True')
                else:
                    sys.exit("Unrecognized argument '" + arg + "'")
        # Remove any special arguments from the list
        arguments = [arg for arg in arguments if '=' not in arg]
        plot_difference(float(arguments[0]), arguments[1], arguments[2], datatype=datatype, time=time, save_fig=save_fig,
                           save_name=save_name, divisions=divisions, get_years=get_years, display=display)
    else:
        sys.exit('Unrecognized function: ' + function)


# What do a photon and a pirate have in common?
# They both travel at c. :D
