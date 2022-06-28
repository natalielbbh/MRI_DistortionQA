from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from pathlib import Path
import numpy as np
import pandas as pd

# data_loc = Path('/Users/nataliegironda/Desktop/MRI_distortion_QA_sample_data')
# gt_data_loc = data_loc / 'CT'
# ^^ update to where you put the sample data!!
# gt_volume = MarkerVolume(gt_data_loc, r_max=300)
# gt_volume.plot_3D_markers()  # produce a quick plot of marker positions

distorted_data_loc = Path('/Users/nataliegironda/Desktop/20220624QAQA/02 gre_trans_AP_330/Original/slicer_centroids.mrk.json')
dis_volume = MarkerVolume(distorted_data_loc, n_markers_expected=336, iterative_segmentation=True)

