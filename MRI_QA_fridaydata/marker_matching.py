from pathlib import Path
from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from MRI_DistortionQA.MarkerAnalysis import MatchedMarkerVolumes
from MRI_DistortionQA.utilities import plot_MarkerVolume_overlay
from MRI_DistortionQA.utilities import plot_compressed_MarkerVolumes

data_loc = Path('/Users/nataliegironda/Desktop/MRI_distortion_QA_sample_data')
data_loc1 = Path('/Users/nataliegironda/Desktop/20220624QAQA')

# distorted centroids
distorted_volume = MarkerVolume(data_loc1 / '02 gre_trans_AP_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)
distorted_volume1 = MarkerVolume(data_loc1 / '03 gre_trans_PA_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)
distorted_volume2 = MarkerVolume(data_loc1 / '04 gre_sag_AP_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)
distorted_volume3 = MarkerVolume(data_loc1 / '05 gre_sag_PA_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)
distorted_volume4 = MarkerVolume(data_loc1 / '06 gre_cor_RL_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)
#distorted_volume5 = MarkerVolume(data_loc1 / '07 gre_cor_LR_330'/ 'Original'/'slicer_centroids.mrk.json', r_max = 300)



# ground truth centroids
ground_truth_volume = MarkerVolume(data_loc / 'CT', r_max=300)

# matched volumes
matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume, ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv('Matched_Markers.csv')  # for use in later examples

matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume1, ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv('Matched_Markers1.csv')  # for use in later examples

matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume2, ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv('Matched_Markers2.csv')  # for use in later examples

matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume3, ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv('Matched_Markers3.csv')  # for use in later examples

matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume4, ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv('Matched_Markers4.csv')  # for use in later examples

#matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume5, ReferenceMarkers=11)
#matched_volume.MatchedCentroids.to_csv('Matched_Markers5.csv')  # for use in later examples


plot_MarkerVolume_overlay([distorted_volume, distorted_volume1,distorted_volume2, distorted_volume3])
plot_compressed_MarkerVolumes([distorted_volume, distorted_volume1,distorted_volume2,distorted_volume3])
