from MRI_DistortionQA.FieldCalculation import ConvertMatchedMarkersToBz
import pandas as pd
from pathlib import Path


data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA')

# load the matched volume calculated in the previous step.
matched_volume = pd.read_csv('Matched_Markers.csv', index_col=0).squeeze("columns")
dicom_data_loc = data_loc / '02 gre_trans_AP_330' / 'Original' / 'dicom_data.json'  # previosly saved from a MarkerVolume using save_dicom_data()

matched_volume1 = pd.read_csv('Matched_Markers1.csv', index_col=0).squeeze("columns")
dicom_data_loc1 = data_loc / '03 gre_trans_PA_330' / 'Original' / 'dicom_data.json'

matched_volume2 = pd.read_csv('Matched_Markers2.csv', index_col=0).squeeze("columns")
dicom_data_loc2 = data_loc / '04 gre_sag_AP_330' / 'Original' / 'dicom_data.json'

matched_volume3 = pd.read_csv('Matched_Markers3.csv', index_col=0).squeeze("columns")
dicom_data_loc3 = data_loc / '05 gre_sag_PA_330' / 'Original' / 'dicom_data.json'

matched_volume4 = pd.read_csv('Matched_Markers4.csv', index_col=0).squeeze("columns")
dicom_data_loc4 = data_loc / '06 gre_cor_RL_330' / 'Original' / 'dicom_data.json'


Bz_field =ConvertMatchedMarkersToBz(matched_volume, dicom_data_loc)
Bz_field.MagneticFields.to_csv('Bfields.csv')  # save for later

Bz_field = ConvertMatchedMarkersToBz(matched_volume1, dicom_data_loc1)
Bz_field.MagneticFields.to_csv('Bfields1.csv')  # save for later

Bz_field = ConvertMatchedMarkersToBz(matched_volume2, dicom_data_loc2)
Bz_field.MagneticFields.to_csv('Bfields2.csv')  # save for later

Bz_field = ConvertMatchedMarkersToBz(matched_volume3, dicom_data_loc3)
Bz_field.MagneticFields.to_csv('Bfields3.csv')  # save for later

Bz_field = ConvertMatchedMarkersToBz(matched_volume4, dicom_data_loc4)
Bz_field.MagneticFields.to_csv('Bfields4.csv')  # save for later



