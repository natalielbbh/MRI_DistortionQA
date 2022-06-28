from MRI_DistortionQA.Reports import MRI_QA_Reporter
import pandas as pd
from pathlib import Path

# Direct data case: pass matched marker volume to MRI_QA_Reporter
# ---------------------------------------------------------------
data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/')
dicom_data_loc = data_loc /'02 gre_trans_AP_330' / 'Original'/ 'dicom_data.json'  # previosly saved from a MarkerVolume
Matched_Markers = pd.read_csv('Matched_Markers.csv', index_col=0).squeeze("columns")

# Harmonic case: pass harmonics to MRI_QA_Reporter so that data can be recontructed
# ----------------------------------------------------------------------------------
G_x_harmonics = pd.read_csv('G_X_harmonics.csv', index_col=0).squeeze("columns")
G_y_harmonics = pd.read_csv('G_y_harmonics.csv', index_col=0).squeeze("columns")
G_z_harmonics = pd.read_csv('G_z_harmonics.csv', index_col=0).squeeze("columns")

report = MRI_QA_Reporter(gradient_harmonics=[G_x_harmonics, G_y_harmonics, G_z_harmonics],
                         r_outer=150, dicom_data=dicom_data_loc)
report.write_html_report()