from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from MRI_DistortionQA import calculate_harmonics
from pathlib import Path
import pandas as pd
from MRI_DistortionQA.utilities import get_dicom_data
import numpy as np
'''
the _4_fit_harmonics.py example shows you how to fit harmonics generally, but if you are happy to use default settings
in the marker matching step you can do it the easy way directly from two volumes:
'''

FieldData = pd.read_csv('Bfields.csv', index_col=0).squeeze("columns")
dicom_data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/02 gre_trans_AP_330/Original/dicom_data.json' )# previosly saved from a MarkerVolume
dicom_data = get_dicom_data(dicom_data_loc)
gradient_strength = np.array(dicom_data['gradient_strength']) * 1e3
normalisation_factor = [1/gradient_strength[0], 1/gradient_strength[1], 1/gradient_strength[2], 1]  # this normalised gradient harmonics to 1mT/m

G_x_Harmonics, G_y_Harmonics, G_z_Harmonics, B0_Harmonics = calculate_harmonics(FieldData, norm=normalisation_factor, n_order=8)
# note that B0_harmonics is None as we did not provide distorted_volume_rev to calculate_harmonics
G_x_Harmonics.harmonics.to_csv('G_X_Harmonics.csv')
G_y_Harmonics.harmonics.to_csv('G_y_Harmonics.csv')
G_z_Harmonics.harmonics.to_csv('G_z_Harmonics.csv')


FieldData = pd.read_csv('Bfields1.csv', index_col=0).squeeze("columns")
dicom_data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/03 gre_trans_PA_330/Original/dicom_data.json' )# previosly saved from a MarkerVolume
dicom_data = get_dicom_data(dicom_data_loc)
gradient_strength = np.array(dicom_data['gradient_strength']) * 1e3
normalisation_factor = [1/gradient_strength[0], 1/gradient_strength[1], 1/gradient_strength[2], 1]  # this normalised gradient harmonics to 1mT/m

G_x_Harmonics, G_y_Harmonics, G_z_Harmonics, B0_Harmonics = calculate_harmonics(FieldData, norm=normalisation_factor, n_order=8)
# note that B0_harmonics is None as we did not provide distorted_volume_rev to calculate_harmonics
G_x_Harmonics.harmonics.to_csv('1G_X_Harmonics.csv')
G_y_Harmonics.harmonics.to_csv('1G_y_Harmonics.csv')
G_z_Harmonics.harmonics.to_csv('1G_z_Harmonics.csv')

FieldData = pd.read_csv('Bfields2.csv', index_col=0).squeeze("columns")
dicom_data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/04 gre_sag_AP_330/Original/dicom_data.json' )# previosly saved from a MarkerVolume
dicom_data = get_dicom_data(dicom_data_loc)
gradient_strength = np.array(dicom_data['gradient_strength']) * 1e3
normalisation_factor = [1/gradient_strength[0], 1/gradient_strength[1], 1/gradient_strength[2], 1]  # this normalised gradient harmonics to 1mT/m

G_x_Harmonics, G_y_Harmonics, G_z_Harmonics, B0_Harmonics = calculate_harmonics(FieldData, norm=normalisation_factor, n_order=8)
# note that B0_harmonics is None as we did not provide distorted_volume_rev to calculate_harmonics
G_x_Harmonics.harmonics.to_csv('2G_X_Harmonics.csv')
G_y_Harmonics.harmonics.to_csv('2G_y_Harmonics.csv')
G_z_Harmonics.harmonics.to_csv('2G_z_Harmonics.csv')

FieldData = pd.read_csv('Bfields3.csv', index_col=0).squeeze("columns")
dicom_data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/05 gre_sag_PA_330/Original/dicom_data.json' )# previosly saved from a MarkerVolume
dicom_data = get_dicom_data(dicom_data_loc)
gradient_strength = np.array(dicom_data['gradient_strength']) * 1e3
normalisation_factor = [1/gradient_strength[0], 1/gradient_strength[1], 1/gradient_strength[2], 1]  # this normalised gradient harmonics to 1mT/m

G_x_Harmonics, G_y_Harmonics, G_z_Harmonics, B0_Harmonics = calculate_harmonics(FieldData, norm=normalisation_factor, n_order=8)
# note that B0_harmonics is None as we did not provide distorted_volume_rev to calculate_harmonics
G_x_Harmonics.harmonics.to_csv('3G_X_Harmonics.csv')
G_y_Harmonics.harmonics.to_csv('3G_y_Harmonics.csv')
G_z_Harmonics.harmonics.to_csv('3G_z_Harmonics.csv')

FieldData = pd.read_csv('Bfields4.csv', index_col=0).squeeze("columns")
dicom_data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/06 gre_cor_RL_330/Original/dicom_data.json' )# previosly saved from a MarkerVolume
dicom_data = get_dicom_data(dicom_data_loc)
gradient_strength = np.array(dicom_data['gradient_strength']) * 1e3
normalisation_factor = [1/gradient_strength[0], 1/gradient_strength[1], 1/gradient_strength[2], 1]  # this normalised gradient harmonics to 1mT/m

G_x_Harmonics, G_y_Harmonics, G_z_Harmonics, B0_Harmonics = calculate_harmonics(FieldData, norm=normalisation_factor, n_order=8)
# note that B0_harmonics is None as we did not provide distorted_volume_rev to calculate_harmonics
G_x_Harmonics.harmonics.to_csv('4G_X_Harmonics.csv')
G_y_Harmonics.harmonics.to_csv('4G_y_Harmonics.csv')
G_z_Harmonics.harmonics.to_csv('4G_z_Harmonics.csv')

