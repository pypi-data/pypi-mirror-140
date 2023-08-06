
"""
Class for opening, reading, and interpreting EVA data from a netCDF file.
Merged class from 'ReadNCdata' in plot_eva.py and 'ReadData' in data_converter.py, in order to have single class
capable of reading all EVA data files into a single.

Author: C.J. Ogilvie, cfo188@usask.ca
Created under the supervision of Dr. Matthew Toohey at the Institute of Space and Atmospheric Studies, University of
Saskatchewan.

Last Updated Oct 20th, 2021.
"""

from netCDF4 import Dataset as open_ncfile
from scipy.interpolate import interp1d
import numpy as np
import os
import sys
import re


class ReadEvaNC:
    """
    Class for opening, reading, and interpreting EVA data from a netCDF file
    """
    # unopened data file
    file = None
    # opened data file
    nc = None
    # Store metadata
    metadata = None
    # Save format - "aod" or "forcing"
    format = None

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

    # data fields for aod format file
    aod550 = None
    gm_aod_550 = None
    hemi_aod_550 = None
    lat4_aod_550 = None
    lat4 = None

    # Unit fields
    ext_units = None
    ssa_units = None
    asy_units = None
    aod_units = None
    lat_units = None
    alt_units = None
    time_units = None
    wave_units = None

    def __init__(self, file_in=None, get_years=False, aod550=False, clip_trop=None):
        # check if given a file, or should be read from command line
        if file_in is None:
            self.__get_file()
        else:
            self.file = file_in
        self.__read_file(get_years=get_years, aod550=aod550)

        if clip_trop and self.format == "forcing":
            # Truncate data at tropopause
            self._clip_tropopause(clip_trop)

        if aod550:
            # Calculate the global mean AOD
            self._get_gm_aod550()
            # Calculate the mean AOD for each hemisphere
            self._get_hemi_aod550()
            # Calculate the mean AOD for four equal latitude regions
            self._get_lat_four_aod550()

    def __get_file(self):
        """
         # Reads the input file from the command line argument
        :return:
        """
        self.file = sys.argv[1]

    def __read_file(self, get_years=False, aod550=False):
        """
        Reads data fields into object attributes
        :param get_years: Sets if time data should be converted to years if it is in another format.
        :return: None
        """
        if self.file[0] == '.' and self.file[1] == '\\':
            self.file = str(os.getcwd() + '\\' + self.file[2:]).strip()

        # open netcdf file
        self.nc = open_ncfile(self.file)
        # Read metadata
        self.metadata = self.nc.__dict__
        if 'aod550' in self.nc.variables.keys():
            self.__read_aod_format()
            self.format = 'aod'

        # Otherwise, use forcing style reading reading
        else:
            self.format = 'forcing'
            self.__read_forcing_format(get_years=get_years)
            # Forcing files do not include AOD, so calculate it
            self.calc_aod()
            if aod550:
                # Get AOD at 550nm wavelength
                self._get_aod550()

    def __read_forcing_format(self, get_years=False):
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

    def __read_aod_format(self):
        """
        Reads in nc variables for files written in the 'AOD' format instead of the forcing format.
        :return:
        """
        # Extract data
        self.lat = self.nc.variables['lat'][:]
        self.aod550 = self.nc.variables['aod550'][:, :]
        self.time = self.nc.variables['time'][:]
        # self.reff = self.nc.variables['reff'][:]
        # Set units
        self.lat_units = self.nc.variables['lat'].units
        self.aod_units = 'unitless'
        self.time_units = self.nc.variables['time'].units
        # self.reff_units = self.nc.variables['reff'].units
        # Check dimensions to ensure correct ordering
        self.__check_aod_dimensions()

    def __check_dimensions(self, time):
        """
        Check the dimensions of the data are in the expected order, and rearrange them if not.
        :param time: The name of the time variable we are using, 'dec_year', 'months', or 'time'
        :return: None
        :postcondition: optical data has dimensions [time, band, latitude, altitude].
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

    def __check_aod_dimensions(self):
        """
        Ensure aod data read in is consistent with the expected dimensional format.
        Corrects the data if it is not.
        :postconditions: self.aod550 has dimensions [time, latitude]
        :return: None
        """
        time_dim = self.nc.variables['time'].dimensions[0]
        # Set dimensions to be [time, latitude]
        if self.nc.variables['aod550'].dimensions[0] != time_dim:
            self.aod550 = np.transpose(self.aod550, (1, 0))

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

    def _clip_tropopause(self, file):
        """
        Truncates extension data recorded below the tropopause.
        Truncation is done by taking mean height of tropopause altitude over time. This is calculated for each latitude.
        :param file: Tropopause height data file (typically GloSSAC). In netcdf format.
        :postcondition: Extinction data is truncated at the tropopause.
        :return: None
        """
        trop_nc = open_ncfile(file)
        trop_z = trop_nc.variables['trp_hgt'][:, :]
        trop_lat = trop_nc.variables['lat'][:]
        mean_trop_z = np.mean(trop_z, 1)

        # Fit troposphere data to needed latitude
        trop_z = interp1d(list(trop_lat), list(mean_trop_z), kind='linear', fill_value="extrapolate")(list(self.lat))

        # Omit data below tropopause at each latitude
        for lat_i, lat in enumerate(self.lat):
            # Omit data below tropopause height at this latitude
            self.ext_earth[:, :, lat_i, self.alt < trop_z[lat_i]] = "nan"
            self.ext_earth[:, :, lat_i, self.alt < trop_z[lat_i]] = "nan"

    def _get_aod550(self):
        """
        Obtains the aod data at the wavelength of 550 nm.
        :return: the AOD data at 550nm, or -1 if the data cannot be found. Also sets the self.aod550 attribute.
        """
        # If in AOD format, we will already have aod550
        if self.aod550 is not None:
            return self.aod550
        # If we do not have it, we are in forcing format and need to obtain it.
        else:
            # First, determine the band 550nm is in
            wavelength = 0.55
            # Find the bands which contain the specified wavelength
            matched_bands = []
            band_width = []
            # Examine terrestrial bands
            for band in range(0, len(self.wl1_earth)):
                if self.wl2_earth[band] > wavelength >= self.wl1_earth[band]:
                    band_width.append(self.wl2_earth[band] - self.wl1_earth[band])
                    matched_bands.append(band)
            # Examine solar bands
            for band in range(0, len(self.wl2_sun)):
                if self.wl2_sun[band] > wavelength >= self.wl1_sun[band]:
                    band_width.append(self.wl2_sun[band] - self.wl1_sun[band])
                    matched_bands.append(band + len(self.wl1_earth))
            # If no bands were found, exit with -1.
            if len(matched_bands) == 0:
                return -1
            # Use the found band with the narrowest range
            index = band_width.index(min(band_width))
            band = matched_bands[index]
            # Obtain the aod data from the appropriate band
            if band >= len(self.wl1_earth):
                aod_in = self.aod_sun
                band_index = band - len(self.wl1_earth)
            else:
                aod_in = self.aod_earth
                band_index = band
            # Set the aod550 to the correct data
            self.aod550 = aod_in[:, band_index, :]
            return self.aod550

    def _get_gm_aod550(self):
        """
        Calculates the global mean using latitude weighting for the AOD for the 550 nm wavelength
        :postconditions: Sets the self.gm_aod_550 parameter
        :return: List containing Global AOD data at 550nm
        """
        # Ensure AOD550 has already been calculated
        if self.aod550 is None:
            self._get_aod550()
        # Create arrays to be filled
        weighted_lat = np.zeros(len(self.lat))
        gm_aod = np.zeros(len(self.time))
        # Calculate the weighted latitude data
        weighted_lat[:] = np.cos(self.lat[:] * np.pi / 180)
        weighted_lat[:] = weighted_lat[:] / sum(weighted_lat[:])
        # Fill the gm_aod with the properly weighed aod data
        gm_aod[:] = np.inner(self.aod550[:, :], weighted_lat)
        # Save the data in this object and return it
        self.gm_aod_550 = gm_aod
        return gm_aod

    def _get_hemi_aod550(self):
        """
        Calculates the hemispheric means using latitude weighting for the AOD at 550 nm wavelength
        :postconditions: Sets the self.hemi_aod_550 parameter
        :return: 2D List containing hemispheric AOD data at 550nm
        """
        # Ensure AOD550 has already been calculated
        if self.aod550 is None:
            self._get_aod550()
        # Set needed variables and data
        north_AOD = []
        north_lat = []
        south_AOD = []
        south_lat = []
        aod = self.aod550
        lat = self.lat
        # Sort AOD into North and South data
        for index, latitude in enumerate(lat):
            if latitude >= 0:
                north_lat.append(float(latitude))  # Ensure lats are floats to avoid type error later
                north_AOD.append(aod[:, index])
            else:
                south_lat.append(float(latitude))  # Ensure lats are floats to avoid type error later
                south_AOD.append(aod[:, index])
        # Reformat as np.arrays for easier arithmetic
        north_lat = np.array(north_lat)
        north_AOD = np.array(north_AOD)
        south_lat = np.array(south_lat)
        south_AOD = np.array(south_AOD)
        # Fix dimensions of AOD arrays (so they work with np.inner later)
        north_AOD = np.transpose(north_AOD, (1, 0))
        south_AOD = np.transpose(south_AOD, (1, 0))
        # Then find the weighted means of each
        # Create arrays to be filled
        weighted_lat_N = np.zeros(len(north_lat))
        weighted_lat_S = np.zeros(len(south_lat))
        mean_aod_N = np.zeros(len(self.time))
        mean_aod_S = np.zeros(len(self.time))
        # Calculate the weighted latitude data
        weighted_lat_N[:] = np.cos(north_lat[:] * np.pi / 180)
        weighted_lat_S[:] = np.cos(south_lat[:] * np.pi / 180)
        weighted_lat_N[:] = weighted_lat_N[:] / sum(weighted_lat_N[:])
        weighted_lat_S[:] = weighted_lat_S[:] / sum(weighted_lat_S[:])
        # Fill the mean aod with the properly weighed aod data
        mean_aod_N[:] = np.inner(north_AOD[:, :], weighted_lat_N)
        mean_aod_S[:] = np.inner(south_AOD[:, :], weighted_lat_S)
        # Save the data in one variable and return it
        self.hemi_aod_550 = [mean_aod_N, mean_aod_S]
        return self.hemi_aod_550

    def _get_lat_four_aod550(self):
        """
        Calculates the aod means for four equal area regions at 550 nm wavelength
        :postconditions: Sets the self.lat4_aod_550 parameter
        :return: 2D List containing the four-latitude AOD data at 550nm
        """
        # Ensure AOD550 has already been calculated
        if self.aod550 is None:
            self._get_aod550()
        # Create containers for each of the 4 regions AOD data and latitude data
        n3090_AOD = []
        n3090_lat = []
        n030_AOD = []
        n030_lat = []
        s030_AOD = []
        s030_lat = []
        s3090_AOD = []
        s3090_lat = []
        # Extract the data we have
        aod = self.aod550
        lat = self.lat
        # Sort AOD and latitude data into the four regions
        for index, latitude in enumerate(lat):
            if latitude >= 30:
                n3090_lat.append(float(latitude))  # Ensure lats are floats to avoid type error later
                n3090_AOD.append(aod[:, index])
            elif latitude >= 0:
                n030_lat.append(float(latitude))  # Ensure lats are floats to avoid type error later
                n030_AOD.append(aod[:, index])
            elif latitude >= -30:
                s030_lat.append(float(latitude))  # Ensure lats are floats to avoid type error later
                s030_AOD.append(aod[:, index])
            else:
                s3090_lat.append(float(latitude))  # Ensure lats are floats to avoid type error later
                s3090_AOD.append(aod[:, index])
        # Store AOD and lat sets in a list for convenience
        aod_list = [n3090_AOD, n030_AOD, s030_AOD, s3090_AOD]
        lat_list = [n3090_lat, n030_lat, s030_lat, s3090_lat]
        # Calculate the weighted mean AOD for each region
        lat4_aod = []
        for index, aod_set in enumerate(aod_list):
            # Reformat as np.arrays for easier arithmetic
            aod_set = np.array(aod_set)
            lat_list[index] = np.array(lat_list[index])
            lat_set = lat_list[index]
            # Fix dimensions of AOD arrays (so they work with np.inner later)
            aod_set = np.transpose(aod_set, (1, 0))
            # Create arrays to be filled
            weighted_lat = np.zeros(len(lat_set))
            mean_aod = np.zeros(len(self.time))
            # Calculate the weighted latitude data
            weighted_lat[:] = np.cos(lat_set[:] * np.pi / 180)
            weighted_lat[:] = weighted_lat[:] / sum(weighted_lat[:])
            # Fill the mean aod with the properly weighed aod data
            mean_aod[:] = np.inner(aod_set[:, :], weighted_lat)
            lat4_aod.append(mean_aod)

        # Save the data and return the aod
        self.lat4_aod_550 = lat4_aod
        self.lat4 = lat_list
        return self.lat4_aod_550

