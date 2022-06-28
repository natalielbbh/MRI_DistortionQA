from pathlib import Path
from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from MRI_DistortionQA.MarkerAnalysis import MatchedMarkerVolumes

data_loc = Path('/Users/nataliegironda/Desktop/MRI_distortion_QA_sample_data')
data_loc1 = Path('/Users/nataliegironda/Desktop/20220624QAQA')

# distorted centroids
distorted_volume = MarkerVolume(data_loc1 / '02 gre_trans_AP_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)
#distorted_volume_rev = MarkerVolume(data_loc1 / '03 gre_trans_PA_330'/ 'Original', r_max = 300)

# ground truth centroids
ground_truth_volume = MarkerVolume(data_loc / 'CT', r_max=300)

# matched volumes
matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume, ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv('Matched_Markers.csv')  # for use in later examples

# plot the match
matched_volume.plot_3D_markers()
