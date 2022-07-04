from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from pathlib import Path

'''
download example data and unzip:
https://cloudstor.aarnet.edu.au/plus/s/Wm9vndV47u941JU
'''

data_loc = Path('/Users/nataliegironda/Desktop/MR_LinacTest/')
# ^^ update to where you put the sample data!!
this_file_loc = Path(__file__).parent.resolve()

gt_data_loc = data_loc / 'CT'
mr_data_loc = data_loc / '04 gre_trans_AP_330'/ 'Original'
mr_data_loc_reverse_gradient = data_loc / '05 gre_trans_PA_330'/ 'Original'

gt_volume = MarkerVolume(gt_data_loc / 'slicer_centroids.mrk.json', r_max=180)
# gt_volume.plot_3D_markers()  # produce a quick plot of marker positions
gt_volume.export_to_slicer(save_path=this_file_loc / '_newphantom_example' / 'CT')

mr_volume = MarkerVolume(mr_data_loc, cutoff_point=57)
mr_volume.save_dicom_data(save_path=this_file_loc / '_newphantom_example' / 'MR' / '04 gre_trans_AP_330')
# save necessary acquisition data as json for easy use later (only works for MR data)
mr_volume.export_to_slicer(save_path=this_file_loc / '_newphantom_example' / 'MR' / '04 gre_trans_AP_330')

mr_volume_rev = MarkerVolume(mr_data_loc_reverse_gradient, cutoff_point = 57)
mr_volume_rev.save_dicom_data(save_path=this_file_loc / '_newphantom_example' / 'MR' / '05 gre_trans_PA_330')
mr_volume_rev.export_to_slicer(save_path=this_file_loc / '_newphantom_example' / 'MR' / '05 gre_trans_PA_330')
