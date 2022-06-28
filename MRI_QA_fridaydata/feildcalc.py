from MRI_DistortionQA.FieldCalculation import ConvertMatchedMarkersToBz
import pandas as pd
from pathlib import Path


data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA')

# load the matched volume calculated in the previous step.
matched_volume = pd.read_csv('Matched_Markers.csv', index_col=0).squeeze("columns")
dicom_data_loc = data_loc / '02 gre_trans_AP_330' / 'Original' / 'dicom_data.json'  # previosly saved from a MarkerVolume using save_dicom_data()

Bz_field = ConvertMatchedMarkersToBz(matched_volume, dicom_data_loc)
Bz_field.MagneticFields.to_csv('Bfields.csv')  # save for later
