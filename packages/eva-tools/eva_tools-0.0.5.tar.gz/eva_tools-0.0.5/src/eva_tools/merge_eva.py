"""
merge_eva.py
Merges two netcdf data files containing easy volcanic aerosol data (or climate data of the same format).
The files are merged at a specified time.
Outputs a netcdf file containing the merged data.

Created by C.J. Ogilvie for Dr. Matthew Toohey at the University of Saskatchewan.
Last updated Nov. 3rd, 2021
"""
from datetime import datetime
from scipy.interpolate import interp1d
import numpy as np
import os
from read_eva import ReadEvaNC
from write_eva import WriteEvaNC


def merge_files(file_1_name, file_2_name, output_file, early_file, stitch_at_time, metadata, merge_metadata=True, truncate=False, trop_file=None, time_desc = 'fractional year (ISO 8901)', time_units='years', lat_units='degrees N'):
    """
    Merges two stratospheric SAOD files (in netcdf format) into one file, stitched at a given time.
    :param file_1_name: path to first file
    :param file_2_name: path to second file
    :param output_file: name of output file (will be created in Data_Out dir)
    :param early_file: integer 1 or 2: sets which file contains the data which will be used for the earlier time period
    :param stitch_at_time: sets the time where the stitching occurs.
    :param metadata: Additional metadata (in python dictionary format) to be added to source metadata. Typically regarding merging process.
    :param merge_metadata: Boolean, sets if the metadata from the source files should be kept and written to merged file.
    :param truncate: Boolean, sets if the data should be truncated at the tropopause.
    :param trop_file: File path to tropopause data. Needed only if truncate=True.
    :param time_desc: Description of time parameter used.
    :param time_units: Description of time units used (typically ='year')
    :param lat_units: Description of latitude units used (typically ='degrees N')
    :return: None - output merged file is created.
    """

    # Read the files, truncating at tropopause if needed
    if truncate:
        data_1 = ReadEvaNC(file_in=file_1_name, get_years=True, aod550=True, clip_trop=trop_file)
        data_2 = ReadEvaNC(file_in=file_2_name, get_years=True, aod550=True, clip_trop=trop_file)
    else:
        data_1 = ReadEvaNC(file_in=file_1_name, get_years=True, aod550=True)
        data_2 = ReadEvaNC(file_in=file_2_name, get_years=True, aod550=True)

    # Merge metadata
    if merge_metadata:
        for key in data_1.metadata.keys():
            metadata['File 1: '+key] = data_1.metadata[key]
        for key in data_2.metadata.keys():
            metadata['File 2: '+key] = data_2.metadata[key]

    # Find time limits
    min_t_1 = min(data_1.time)
    min_t_2 = min(data_2.time)
    max_t_1 = max(data_1.time)
    max_t_2 = max(data_2.time)

    # Check if second dataset has higher time values we should use
    if early_file == 1:
        # Stitch at specified time if given
        if stitch_at_time is not None:
            time_low = [time for time in data_1.time if time < stitch_at_time]
            time_high = [time for time in data_2.time if time >= stitch_at_time]
            # Truncate aod data to these time regions
            aod_1 = data_1.aod550[data_1.time < stitch_at_time, :]
            aod_2 = data_2.aod550[data_2.time >= stitch_at_time, :]
        # Otherwise go to beginning of more recent series
        else:
            # Cut low time back so no overlap
            time_low = [time for time in data_1.time if time < min_t_2]
            time_high = data_2.time
            # Truncate aod data to these time regions
            aod_1 = data_1.aod550[:len(time_low) - 1, :]
            aod_2 = data_2.aod550[len(data_2.time) - len(time_high) - 1:, :]
    else:
        # Stitch at specified time if given
        if stitch_at_time is not None:
            time_low = [time for time in data_2.time if time < stitch_at_time]
            time_high = [time for time in data_1.time if time >= stitch_at_time]
            # Truncate aod data to these time regions
            aod_1 = data_1.aod550[data_1.time >= stitch_at_time, :]
            aod_2 = data_2.aod550[data_2.time < stitch_at_time, :]
        # Otherwise go to beginning of more recent series
        else:
            # Cut low time back so no overlap
            time_low = [time for time in data_2.time if time < min_t_1]
            time_high = data_1.time
            # Truncate aod data to these time regions
            aod_1 = data_1.aod550[len(data_1.time) - len(time_high) - 1:, :]
            aod_2 = data_2.aod550[:len(time_low) - 1, :]

    # Concatenate times
    merged_time = time_low + time_high

    # Fit aod to matching latitudes
    # Use whichever has more narrow range to allow accurate interpolation
    if max(data_2.lat) <= max(data_1.lat):
        latitude = list(data_2.lat)
        aod_temp = []
        for index, time in enumerate(aod_1[:, 0]):
            # Fit data 1 set to data 2 latitude
            result = interp1d(list(data_1.lat), aod_1[index, :], kind='linear')(latitude)
            # Save result to array
            aod_temp.append(result)
        aod_1 = aod_temp
    else:
        latitude = list(data_1.lat)
        aod_temp = []
        for index, time in enumerate(aod_2[:, 0]):
            # Fit data 2 set to data 1 latitude
            result = interp1d(list(data_2.lat), aod_2[index, :], kind='linear')(latitude)
            # Save result to array
            aod_temp.append(result)
        aod_2 = aod_temp

    # Merge aod
    # Convert to numpy array for 2D concatenation
    aod_1 = np.array(aod_1)
    aod_2 = np.array(aod_2)

    # Concatenate data in time axis
    merged_aod = np.concatenate([aod_1, aod_2], axis=0)

    # Convert back to a list
    merged_aod = merged_aod.tolist()

    # Write merged data to new file
    WriteEvaNC(filename=output_file, aod550=merged_aod, latitude=latitude, time=merged_time, time_unit=time_units, lat_unit=lat_units, time_desc=time_desc, metadata=metadata)


def merge_three(file_1_name, file_2_name, file_3_name, output_file, file_order, stitch_at_times, metadata, merge_metadata=True, truncate=False, trop_file=None, time_desc = 'fractional year (ISO 8901)', time_units='years', lat_units='degrees N'):
    """
    Merges two stratospheric SAOD files (in netcdf format) into one file, stitched at a given time.
    :param file_1_name: path to first file
    :param file_2_name: path to second file
    :param file_3_name: path to third file
    :param output_file: name of output file (will be created in Data_Out dir)
    :param file_order: list of integers containing 1,2 and 3. Sets the chronological order the files should be merged in. (i.e, [1, 3, 2])
    :param stitch_at_times: list, sets the times where the stitching occurs. (i.e, [-500, 1850])
    :param metadata: Additional metadata (in python dictionary format) to be added to source metadata. Typically regarding merging process.
    :param merge_metadata: Boolean, sets if the metadata from the source files should be kept and written to merged file.
    :param truncate: Boolean, sets if the data should be truncated at the tropopause.
    :param trop_file: File path to tropopause data. Needed only if truncate=True.
    :param time_desc: Description of time parameter used.
    :param time_units: Description of time units used (typically ='year')
    :param lat_units: Description of latitude units used (typically ='degrees N')
    :return: None - output merged file is created.
    """
    files = [file_1_name, file_2_name, file_3_name]
    temp_filename = "merge_3_temp.nc"

    # Merge metadata separately to avoid errors
    if merge_metadata:
        # Read the files to get metadata
        data_1 = ReadEvaNC(file_in=file_1_name, get_years=True, aod550=True)
        data_2 = ReadEvaNC(file_in=file_2_name, get_years=True, aod550=True)
        data_3 = ReadEvaNC(file_in=file_3_name, get_years=True, aod550=True)
        # Store the metadata
        for key in data_1.metadata.keys():
            metadata['File 1: ' + key] = data_1.metadata[key]
        for key in data_2.metadata.keys():
            metadata['File 2: ' + key] = data_2.metadata[key]
        for key in data_3.metadata.keys():
            metadata['File 3: ' + key] = data_3.metadata[key]

    # Merge first two files into a temp file
    merge_files(files[file_order[0]-1], files[file_order[1]-1], temp_filename, 1, stitch_at_times[0], metadata, merge_metadata=False, truncate=truncate, trop_file=trop_file, time_desc=time_desc, time_units=time_units, lat_units=lat_units)
    # Merge last file with temp file
    merge_files(temp_filename, files[file_order[2]-1], output_file, 1, stitch_at_times[1], metadata, merge_metadata=False, truncate=truncate, trop_file=trop_file, time_desc=time_desc, time_units=time_units, lat_units=lat_units)


################################################################################
# Do not edit above this point (unless you have a good reason)
# Edit this section only

if __name__ == '__main__':

    # Write file names here
    data_dir = '../Data_In/'
    data_out_dir = '../Data_Out/'
    #file_1_name = 'CMIP_VOLMIP550_radiation_v3.nc'
    file_1_name = 'CMIP_VOLMIP550_radiation_v4_1850-2018.nc'
    #file_2_name = 'eVolv2k_v2_EVA_AOD_-500_1900_1.nc'
    file_2_name = 'eVolv2k_v3_EVA_AOD_-500_1900_1.nc'
    output_file = 'merged_EVA_eVolv2k_v3p1_CMIP6_v4_SAOD_stitched_at_1850.nc'

    # Set which file should be earlier data in time for stitching
    early_file = 2

    # Set time we will stitch at -- set to "None" to automatically stitch
    stitch_at_time = 1850

    # Set these parameters if file should be truncated at the tropopause
    truncate = True
    trop_file = data_dir + 'GloSSAC_V2.0.nc'

    # Set if we should merge file metadata or only use added metadata
    merge_metadata = True

    # Write added meta data here.
    metadata = {'Title': "Merged SAOD, eVolv2k(v3) and CMIP6(v4)",
                'Creation Time': datetime.now().strftime("%b %d %Y at %H:%M"),
                'Source': 'File created by C.J. Ogilvie using merge_eva.py script for Matthew Toohey',
                'Description': 'Zonal mean stratospheric aerosol optical depth at 550 nm from 500 BCE to 2014 CE. From 500 BCE to 1849, data is from the EVA(eVolv2k) (version 2.1) reconstruction of Toohey and Sigl (2017). From 1850-2014, data is from the CMIP6 reconstruction (version 3) from Beiping Luo et al. (in prep). Some details of the CMIP6 reconstruction can be found in papers from Thomason et al. (2017) and Revell et al. (2017). CMIP6 aerosol extinction has been truncated at the climatological tropopause based on the tropopause heights included in the GloSSAC data set (Thomason et al., 2017).',
                'File 1 Name': file_1_name,
                'File 2 Name': file_2_name,
                'Stitch Point': '1850',
                'Authors': 'C.J. Ogilvie and Matthew Toohey',
                'Contact': 'cfo188@usask.ca or matthew.toohey@usask.ca',
                'References': 'Toohey, M. and Sigl, M.: Volcanic stratospheric sulfur injections and aerosol optical depth from 500 BCE to 1900 CE, Earth Syst. Sci. Data_In, 9(2), 809-831, doi:10.5194/essd-9-809-2017, 2017. Thomason et al. (2018): Thomason, L. W., Ernest, N., Millán, L., Rieger, L., Bourassa, A., Vernier, J.-P., Manney, G., Luo, B., Arfeuille, F., and Peter, T.: A global space-based stratospheric aerosol climatology: 1979–2016, Earth Syst. Sci. Data, 10, 469–492, https://doi.org/10.5194/essd-10-469-2018, 2018.'}

    # Get path to files needed
    file_1_name = data_dir + file_1_name
    file_2_name = data_dir + file_2_name
    output_file = data_out_dir + output_file
    merge_files(file_1_name=file_1_name, file_2_name=file_2_name, output_file=output_file, stitch_at_time=stitch_at_time, early_file=early_file, metadata=metadata, merge_metadata=merge_metadata, truncate=truncate, trop_file=trop_file)

















