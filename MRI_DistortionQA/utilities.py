"""
General purpose reusable functions
"""

import os
import pathlib
import sys
import glob
import logging
from pathlib import Path
import numpy as np
from scipy.special import lpmv
import pandas as pd
from matplotlib import pyplot as plt
import pydicom
import json


ch = logging.StreamHandler()
formatter = logging.Formatter('[%(filename)s: line %(lineno)d %(levelname)8s] %(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(ch)
logger.setLevel(logging.INFO)  # This toggles all the logging in your app
logger.propagate = False


class bcolors:
    """
    This is just here to enable me to print pretty colors to the linux terminal
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def build_dicom_affine(Dicomfiles):
    """
    Build the dicom affine matrix.
    The reference I used to create the affine is `NIbabel <https://nipy.org/nibabel/dicom/dicom_orientation.html>`_
    (we are using the r/c defined under 'DICOM affines again')

    :param Dicomfiles: list of pydicom.dataset.FileDataset instances (created using pydicom.read_file)
    :type Dicomfiles: list
    :return: CoordinateMatrix, a 4x4 matrix which transforms the image based coordinates (i,j,k) to world coordinates (x,y,z)
    """

    assert isinstance(Dicomfiles, list)
    assert isinstance(Dicomfiles[0], pydicom.dataset.FileDataset)

    ds = Dicomfiles[0]  # just use first one, they all give the same result
    if not np.logical_or(np.equal(np.abs(ds.ImageOrientationPatient), 1),
                         np.equal(np.abs(ds.ImageOrientationPatient), 0)).all():
        '''
        This just checks that the ImageOrientationPatient tag only contains 0 or 1, i.e. that no weird oblique
        orientation is in use. For now I don't want to support or think about non cardinal encoding directions
        '''
        raise NotImplementedError('at the moment we only support cardinal imaging planes')

    CoordinateMatrix = np.zeros([4, 4])
    F = np.array([ds.ImageOrientationPatient[3:], ds.ImageOrientationPatient[:3]]).T
    first_col = np.multiply(F[:, 0], ds.PixelSpacing[0])
    sec_col = np.multiply(F[:, 1], ds.PixelSpacing[1])
    CoordinateMatrix[:, 0][0:3] = first_col
    CoordinateMatrix[:, 1][0:3] = sec_col
    CoordinateMatrix[:, 3][0:3] = [float(i) for i in ds.ImagePositionPatient]
    if Dicomfiles.__len__() > 1:
        # figure out slice direction
        SliceLoc = []
        image_position_patient_list = []
        for file in Dicomfiles:
            # need to extract the slice coordinates one at a time (can't think of a better way anyway...)
            image_position_patient_list.append(file.ImagePositionPatient)
            SliceLoc.append(file.SliceLocation)
        SliceLoc = np.array(SliceLoc)
        image_position_patient_list = np.array(image_position_patient_list)
        if not np.allclose(np.diff(SliceLoc), np.diff(SliceLoc)[0], atol=.1, rtol=.1):
            logger.error(f'it appears there may be missing or inconsistently spaced slices. Continuing')
        k = (image_position_patient_list[-1] - image_position_patient_list[0])/(image_position_patient_list.shape[0]-1)
        CoordinateMatrix[0:3, 2] = k

    return CoordinateMatrix


def dicom_to_numpy(path_to_dicoms, FilesToReadIn=None, file_extension='dcm', return_XYZ=False):
    """
    This function does two things:

    1. Loads all the dicom files in path_to_dicoms in a numpy array. data is ordered according to [row, column, slice]
    2. Builds the matrix that transforms the [r,c,s] indices into [x,y,z] coordinates

    :param path_to_dicoms: folder where all dicoms images are stored
    :type path_to_dicoms: pathlib.Path or string
    :param FilesToReadIn: By default, this function will read in all files of file type file_extension. If you only want
        to read in a subset of files, you can specify them with FilesToReadIn
    :type FilesToReadIn: list, optional
    :param file_extension: extension of dicom files, e.g. 'dcm' or 'IMA'
    :type file_extension: string
    :param return_XYZ: if True, will build and return three matrics containing the X, Y, and Z coords at each i,j,k
        pixel.
    :type return_XYZ: bool
    :returns ImageArray: a numpy array of voxels
    :returns dicom_affine: a matrix that transforms the [r,c,s] indices into [x,y,z] coordinates
    :returns (X, Y, Z): Coordinate arrays the same size as ImageArray. Optional
    """
    if not FilesToReadIn:
        FilesToReadIn = get_all_files(path_to_dicoms, file_extension=file_extension)
    if not FilesToReadIn:
        raise FileNotFoundError(f'could not find any {file_extension} files in input directory {path_to_dicoms}'
                                f'\nTry using the ImExtenstion= input option to look for different image types')
    if isinstance(FilesToReadIn, list):
        CompletePathFiles = [str(Path(path_to_dicoms) / file) for file in FilesToReadIn]
    elif isinstance(FilesToReadIn, (str, pathlib.Path)):
        CompletePathFiles = [str(Path(path_to_dicoms) / FilesToReadIn)]


    dicom_slices = [pydicom.read_file(f) for f in CompletePathFiles]
    dicom_slices = _sort_dicom_slices(dicom_slices)
    dicom_affine = build_dicom_affine(dicom_slices)

    n_rows = dicom_slices[0].Rows
    n_cols = dicom_slices[0].Columns
    n_slices = len(dicom_slices)

    ImageArray = np.zeros([n_rows, n_cols, n_slices])
    for i, file in enumerate(dicom_slices):
        ImageArray[:, :, i] = file.pixel_array
    if return_XYZ:
        rcsMatrix = np.zeros([4, n_rows * n_cols * n_slices])
        r_indices = np.arange(0, n_rows)
        c_indices = np.arange(0, n_cols)
        s_indices = np.arange(0, n_slices)
        [RR, CC, SS] = np.meshgrid(r_indices, c_indices, s_indices, indexing='ij')
        rcsMatrix[0, :] = RR.flatten()
        rcsMatrix[1, :] = CC.flatten()
        rcsMatrix[2, :] = SS.flatten()
        rcsMatrix[3, :] = 1
        XYZtemp = np.matmul(dicom_affine, rcsMatrix)
        X = np.reshape(XYZtemp[0, :], ImageArray.shape)
        Y = np.reshape(XYZtemp[1, :], ImageArray.shape)
        Z = np.reshape(XYZtemp[2, :], ImageArray.shape)

        return ImageArray, dicom_affine, (X, Y, Z)
    else:
        return ImageArray, dicom_affine


def _sort_dicom_slices(dicom_datasets):
    """
    sort slices by instance number
    :param dicom_datasets: list of pydicom files
    :return: sorted list of pydicom files
    """
    instance_number = [el.InstanceNumber for el in dicom_datasets]
    sort_ind = np.argsort(instance_number)
    return list(np.array(dicom_datasets)[sort_ind])


def get_all_files(PathToData, file_extension):
    """
    quick script to just collect all the files in the Analysis path

    :param PathToData: folder where the files are
    :type PathToData: pathlib.Path or string
    :param file_extension: extension of files to return, e.g. 'dcm'
    :type file_extension: str
    :returns Files: list of all found files
    """

    if not file_extension[0] == '.':
        # handles the case where the user entered 'dcm' instead of '.dcm'
        file_extension = '.' + file_extension
    file_extension = '*' + file_extension
    # check that this is now in the format we require
    if not file_extension[0:2] == '*.':
        logger.error('please enter the file_extension parameter like this : file_extension = "jpg"')
        sys.exit(1)

    if not isinstance(PathToData,Path):
        PathToData = Path(PathToData)

    if not os.path.isdir(PathToData):
        raise FileNotFoundError(f'invalid path supplied; {PathToData} does not exist')
    AllFiles = glob.glob(str(PathToData / file_extension))
    Files = []
    for file in AllFiles:
        head, tail = os.path.split(file)
        Files.append(tail)
    if not Files:
        logging.error(f'no {file_extension} files in {PathToData}')

    return Files


def convert_cartesian_to_spherical(InputCoords):
    """
    Converts cartesian coordinates [x,y,z] to spherical coordinates [r, azimuth, elevation].
    If r, azimuth, or elevation already exist as column names they are overwritten.
    The convention used here matches the convention
    `matlab uses <https://www.mathworks.com/help/matlab/ref/cart2sph.html>`_;
    this is because parts of this code were ported from an earlier version in matlab.

    - 0 <= azimuth <= 2*pi
    - 0 <= elevation <= pi

    :param InputCoords: a data frame containing (at least) columns x, y, z.
    :returns InputCoords: same data frame with additional columns [r, azimuth, elevation]
    """
    if 'r' in InputCoords.columns:
        InputCoords = InputCoords.drop(columns='r')
    if 'azimuth' in InputCoords.columns:
        InputCoords = InputCoords.drop(columns='azimuth')
    if 'elevation' in InputCoords.columns:
        InputCoords = InputCoords.drop(columns='elevation')

    InputCoords.insert(3, "r", np.sqrt(InputCoords.x ** 2 + InputCoords.y ** 2 + InputCoords.z ** 2))
    InputCoords.insert(4, "azimuth", np.arctan2(InputCoords.y, InputCoords.x) + np.pi)
    InputCoords.insert(5, "elevation", np.arctan2(InputCoords.z, np.sqrt(InputCoords.x ** 2 + InputCoords.y ** 2)) + np.pi/2)


    return InputCoords


def convert_spherical_to_cartesian(InputCoords):
    """
    Converts spherical coordinates [r, azimuth, elevation] to cartesian coordinates [x,y,z].
    if the cartesian columns 'x', 'y', 'z' already exist, they will be overwritten

    :param InputCoords: a data frame containing columns r, azimuth, elevation
    :returns InputCoords:   same data frame with additional columns [x,y,z]
    """
    if 'x' in InputCoords.columns:
        InputCoords = InputCoords.drop(columns='x')
    if 'y' in InputCoords.columns:
        InputCoords = InputCoords.drop(columns='y')
    if 'z' in InputCoords.columns:
        InputCoords = InputCoords.drop(columns='z')

    # InputCoords.insert(3, "x", InputCoords.r * np.sin(InputCoords.azimuth - np.pi) * np.cos(InputCoords.elevation - np.pi/2))
    # InputCoords.insert(4, "y", InputCoords.r * np.sin(InputCoords.azimuth - np.pi) * np.sin(InputCoords.elevation - np.pi/2))
    # InputCoords.insert(5, "z", InputCoords.r * np.cos(InputCoords.azimuth))

    InputCoords.insert(3, "x", InputCoords.r * np.cos(InputCoords.azimuth - np.pi) * np.cos(InputCoords.elevation - np.pi/2))
    InputCoords.insert(4, "y", InputCoords.r * np.sin(InputCoords.azimuth - np.pi) * np.cos(InputCoords.elevation - np.pi/2))
    InputCoords.insert(5, "z", InputCoords.r * np.sin(InputCoords.elevation - np.pi/2))

    return InputCoords


def generate_legendre_basis(InputCoords, n_order):
    """
    Produce spherical base at all coordinate values.
    This utilises the 'fully normalised' convention described here <https://au.mathworks.com/help/matlab/ref/legendre.html>`_
    Note that we scale all r values by 1000, which is to help ensure numerical stability. This is based on the assumption
    that this input data is in mm. The code will throw a warning if this does not appear to the case.

    :param InputCoords: a data frame which can contain whatever you want, but MUST contain columns called
        elevation, azimuth, and r
    :type InputCoords: Dataframe
    :param n_order: order of harmonic fit
    :type n_order: int
    :returns legendre_basis: a pandas data frame of size [Ncoords, (n_order +1)**2)]
    """

    if InputCoords.r.mean() < 10:
        logger.warning('it appears that your input data is in m, not mm - please use mm!')

    legendre_basis = np.zeros([len(InputCoords.index), (n_order+1)**2])
    k = 0
    coeff_names = []
    for n in range(0, n_order+1):  # the plus 1 is because range stops at -1 for some reason
        Norm = np.sqrt(n+0.5)
        P = Norm * lpmv(0, n, np.cos(InputCoords.elevation))
        legendre_basis[:, k] = np.multiply((InputCoords.r/1000) ** n, P)  # m=0 terms
        coeff_names.append(f'A_{n}_0')
        k = k + 1
        for j in range(0, n):
            m = j+1  # this looks weird but it works to give values m=1:n
            Norm = ((-1)**m) * np.sqrt( (n+0.5)*(np.math.factorial(n-m)) / np.math.factorial(n+m))
            P = Norm * lpmv(m, n, np.cos(InputCoords.elevation))
            legendre_basis[:,k] = np.multiply(np.multiply((InputCoords.r/1000) ** n, P), np.cos(m * InputCoords.azimuth))
            coeff_names.append(f'A_{n}_{m}')
            k = k + 1
            legendre_basis[:, k] = np.multiply(np.multiply((InputCoords.r/1000) ** n, P), np.sin(m * InputCoords.azimuth))
            coeff_names.append(f'B_{n}_{m}')
            k = k + 1

    return pd.DataFrame(legendre_basis, columns=coeff_names)


def convert_spherical_harmonics(harmonics, input_format, output_format):
    """
    NOT WRITTEN YET! function to convert between different harmonic formalisms

    :param harmonics:
    :param input_format:
    :param output_format:
    :return:
    """

    case_string = input_format + '_' + output_format
    converted_harmonics = harmonics.copy()

    if case_string == 'none_normalised':
        k = 0
        coeff_names = []
        n_order = 8

        for n in range(0, n_order + 1):  # the plus 1 is because range stops at -1 for some reason
            Norm = np.sqrt(n + 0.5)
            coeff_names.append(f'A_{n}_0')
            converted_harmonics[k] = converted_harmonics[k]/Norm
            k = k + 1

            for j in range(0, n):
                m = j + 1  # this looks weird but it works to give values m=1:n
                Norm = ((-1) ** m) * np.sqrt((n + 0.5) * (np.math.factorial(n - m)) / np.math.factorial(n + m))
                converted_harmonics[k] = converted_harmonics[k] / Norm
                coeff_names.append(f'A_{n}_{m}')
                k = k + 1
                converted_harmonics[k] = converted_harmonics[k] / Norm
                coeff_names.append(f'B_{n}_{m}')
                k = k + 1

    elif case_string == 'normalised_none':
        pass

    return converted_harmonics


def plot_MarkerVolume_overlay(MarkerVolumeList, legend=None):  # pragma: no cover
    """
    Plot overlaid 3D scatter plots of the marker positions in each MarkerVolume

    :param MarkerVolumeList: list of MarkerVolume instances
    :param legend: legend to display on plot
    :return: None
    """

    assert isinstance(MarkerVolumeList, list)

    fig = plt.figure()
    axs = fig.add_subplot(111, projection='3d')
    for MarkerVolume in MarkerVolumeList:
        axs.scatter(MarkerVolume.MarkerCentroids.x, MarkerVolume.MarkerCentroids.y, MarkerVolume.MarkerCentroids.z)
        axs.set_xlabel('X [mm]')
        axs.set_ylabel('Y [mm]')
        axs.set_zlabel('Z [mm]')
        axs.set_title('3D marker positions')
    axs.set_box_aspect((np.ptp(MarkerVolume.MarkerCentroids.x),
                        np.ptp(MarkerVolume.MarkerCentroids.y),
                        np.ptp(MarkerVolume.MarkerCentroids.z)))
    if legend:
        plt.legend(legend)
    plt.show()


def plot_compressed_MarkerVolumes(MarkerVolumeList, z_max=20, z_min=-20, title=None, legend=None): # pragma: no cover
    """
    plot overlay of compressed marker volumes (z coord is ignored)

    :param MarkerVolumeList:  list of MarkerVolume instances
    :type MarkerVolumeList: list
    :param z_max: max z data to include
    :type z_max: float, optional
    :param z_min: min z data to include
    :type z_min: float, optional
    :param title: title of plot
    :type title: str, optional
    :param legend: legend of plot
    :type legend: list, optional
    :return: None
    """

    fig, axs = plt.subplots(figsize=[8, 8], ncols=1, nrows=1)
    for MarkerVolume in MarkerVolumeList:
        data_ind = np.logical_and(MarkerVolume.MarkerCentroids.z > z_min, MarkerVolume.MarkerCentroids.z < z_max)
        plot_data = MarkerVolume.MarkerCentroids[data_ind]
        axs.scatter(plot_data.x, plot_data.y)
        axs.set_xlim([-150, 150])
        axs.set_ylim([-150, 150])
        axs.set_xlabel('x [mm]', fontsize=15)
        axs.set_ylabel('y [mm]', fontsize=15)
        axs.tick_params(axis='both', which='major', labelsize=12)
        axs.tick_params(axis='both', which='minor', labelsize=12)
        axs.axis("equal")
        axs.grid()
        plt.subplots_adjust(bottom=0.25)
        if legend:
            plt.legend(legend)
        if title:
            plt.title(title)


def get_gradient_spherical_harmonics(Gx_Harmonics, Gy_Harmonics, Gz_Harmonics):
    """
    return the gradient spherical harmonics as as pandas series. this function is simply a clean way to handle
    the different ways users can specify harmonics to other componets of this code

    :param Harmonics:

    :param Gx_Harmonics: either a pandas series or a path to a csv. If it is already a series we do nothing, but handle
        this option for cleaner code elsewhere. Gy_Harmonics and Gz_Harmonics are the same
    :returns: Gx_Harmonics, Gy_Harmonics, Gz_Harmonics as Pandase series
    """

    if isinstance(Gx_Harmonics, pd.Series):
        Gx_Harmonics = Gx_Harmonics
    elif isinstance(Gx_Harmonics, (str,Path)):
        Gx_Harmonics = pd.read_csv(Gx_Harmonics, index_col=0).squeeze("columns")
    else:
        raise AttributeError('could not read in Gx harmonics...please input either a series or a '
                     'path to a saved csv file')


    if isinstance(Gy_Harmonics, pd.Series):
        Gy_Harmonics = Gy_Harmonics
    elif isinstance(Gy_Harmonics, (str,Path)):
        Gy_Harmonics = pd.read_csv(Gy_Harmonics, index_col=0).squeeze("columns")
    else:
        raise AttributeError('could not read in Gy harmonics...please input either a series or a '
                     'path to a saved csv file')


    if isinstance(Gz_Harmonics, pd.Series):
        Gz_Harmonics = Gz_Harmonics
    elif isinstance(Gz_Harmonics, (str,Path)):
        Gz_Harmonics = pd.read_csv(Gz_Harmonics, index_col=0).squeeze("columns")
    else:
        raise AttributeError('could not read in Gz harmonics...please input either a series or a '
                     'path to a saved csv file')

    return Gx_Harmonics, Gy_Harmonics, Gz_Harmonics

def get_dicom_data(dicom_data):
    """
    figures out whether dicom data is a dict or a path to a json file
    if the latter, reads into  a dict and returns
    """

    if isinstance(dicom_data, dict):
        return dicom_data
    elif isinstance(dicom_data,(pathlib.Path, str)):
        with open(dicom_data, 'r') as f:
            dicom_data = json.load(f)
        return dicom_data
    else:
        raise AttributeError(f'could not read in dicom_data of type {type(dicom_data)}')


def reconstruct_Bz(harmonics, coords, quantity='uT', r_outer=None):
    """
    Reconstruct Bz at an arbitrary set of coordinates.
    n_order of reconstruction is derived from the shape of harmonics

    :param harmonics: a pandase series of size (n_order+1)^2, such as that defined within
        FieldAnalysis.SphericalHarmonicFit
    :param coords: a pandas Dataframe which can contain whatever you want, but MUST contain columns called:
        elevation, azimuth, and r
    :param quantity:
        - 'T': return raw field in T
        - 'uT': return field in uT, with A00 set to 0.
    :param r_outer: optional parameter; if you try to reconstruct points with r > r_outer a warning is thrown
    :type r_outer: float or None
    :returns Bz_recon: Pandase series with the value of Bz at each element in coords
    """

    if not quantity in ['uT', 'T']:
        logger.error(f'unsupported quantity "{quantity}" entered for recon.'
                       f'\n valid options are "field" or "uT". Using uT')
        quantity = 'uT'

    if any(abs(coords.r) > r_outer):
        logger.warning(f'you are trying to reconstruct {np.count_nonzero(abs(coords.r) > r_outer)} '
                       f'data points outside rOuter. You can do it, but the futher away'
                       'from rOuter you get the less you should trust this.')

    n_order = int(np.sqrt(harmonics.shape[0])-1)
    legendre_recon = generate_legendre_basis(coords, n_order)
    if quantity == 'uT':  # field in uT, with A00 set to 0 (e.g. only looking at perturbation)
        harmonics_temp = harmonics.copy()
        harmonics_temp.A_0_0 = 0
        Bz_recon = legendre_recon @ harmonics_temp
        Bz_recon = Bz_recon * 1e6
    elif quantity == 'T':  # raw field in T
        Bz_recon = legendre_recon @ harmonics
    else:
        raise NotImplementedError(f'unknown reconstruction option entered: {quantity}')

    return Bz_recon


def compare_recon_report_with_ground_truth_report(ground_truth_report, recon_report, tolerance=1):  # pragma: no cover
    """
    This is to compare the distortion data contained within two Reports.MRI_QA_recon_reporter
    objects. The original purpose was to compare a recon_report generated from direct data, and one
    generated via harmonics, although in principle it can take any two recon_reports.

    :param ground_truth_report: Reports.MRI_QA_recon_reporter instance
    :param recon_report: Reports.MRI_QA_recon_reporter instance
    :param tolerance: tolerance in mm
    """
    # direct overlay of real versus recon
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=[10, 10])
    if ground_truth_report.r_outer == recon_report.r_outer:
        # then use r_outer to filter the data
        gt_data = ground_truth_report._extract_data_from_MatchedMarkerVolume(r_max=ground_truth_report.r_outer)
        recon_data = recon_report._extract_data_from_MatchedMarkerVolume(r_max=recon_report.r_outer)
    else:
        gt_data = ground_truth_report._extract_data_from_MatchedMarkerVolume()
        recon_data = recon_report._extract_data_from_MatchedMarkerVolume()

    axs[0, 0].scatter(gt_data.r_gt, gt_data.abs_dis)
    axs[0, 0].scatter(recon_data.r_gt, recon_data.abs_dis)
    axs[0, 0].legend(['original_data', 'recon_data'])
    axs[0, 0].set_xlabel('r [mm]')
    axs[0, 0].set_ylabel('absolute distortion [mm]')

    # scatter of real versus recon
    axs[0, 1].scatter(gt_data.abs_dis, recon_data.abs_dis)
    axs[0, 1].set_xlabel('original data')
    axs[0, 1].set_ylabel('recon data')

    # box plot of errors
    error = gt_data.abs_dis - recon_data.abs_dis
    axs[1, 0].boxplot(error)
    axs[1, 0].set_ylabel('recon error [mm]')


    # get index of outliers
    outliers_ind = error > tolerance
    print(f'{np.count_nonzero(outliers_ind)} outliers exist, at index {np.where(outliers_ind)}')
    outliers_ind = np.where(outliers_ind)
    for ind in outliers_ind[0]:
        print(f'index {ind} is at {gt_data.x_gt.iloc[ind]: 1.1f},'
              f' {gt_data.y_gt.iloc[ind]: 1.1f},'
              f' {gt_data.z_gt.iloc[ind]: 1.1f}  the value in the ground truth is'
              f' {gt_data.abs_dis.iloc[ind]: 1.1f}'
              f' and the value in the reconstructed is {recon_data.abs_dis.iloc[ind]: 1.1f}')

