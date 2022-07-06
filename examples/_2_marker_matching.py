import sys
from pathlib import Path
from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from MRI_DistortionQA.MarkerAnalysis import MatchedMarkerVolumes

this_file_loc = Path(__file__).parent.resolve()
data_loc = Path('/Users/nataliegironda/Desktop/MR_LinacTest/') #this_file_loc / '_newphantom_example'

# distorted centroids
distorted_volume = MarkerVolume(data_loc / '08 gre_cor_RL_330' / 'Original', verbose=True, iterative_segmentation=True, n_markers_expected=529, gaussian_image_filter_sd=1,r_max=160)
distorted_volume_rev = MarkerVolume(data_loc / '09 gre_cor_LR_330' / 'Original', verbose=True, iterative_segmentation=True, n_markers_expected=529, gaussian_image_filter_sd=1,r_max=160)
distorted_volume_rev.export_to_slicer()
distorted_volume.export_to_slicer()
# ground truth centroids
ground_truth_volume = MarkerVolume(data_loc / 'CT' / 'slicer_centroids.mrk.json', verbose=False, r_max=300)

# matched volumes
matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume, ReverseGradientData=distorted_volume_rev,
                                    ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv(data_loc / 'Matched_Markers.csv')  # for use in later examples

