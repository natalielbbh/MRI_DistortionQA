import sys
from pathlib import Path
import math
import numpy as np

from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from MRI_DistortionQA.MarkerAnalysis import MatchedMarkerVolumes

this_file_loc = Path(__file__).parent.resolve()
data_loc = Path('/Users/nataliegironda/Desktop/MR_LinacTest/') #this_file_loc / '_newphantom_example'

# distorted centroids
distorted_volume = MarkerVolume(data_loc / '04 gre_trans_AP_330' / 'Original', verbose=True, iterative_segmentation=True, n_markers_expected=529, gaussian_image_filter_sd=1,r_max=160)
distorted_volume_rev = MarkerVolume(data_loc / '05 gre_trans_PA_330' / 'Original', verbose=True, iterative_segmentation=True, n_markers_expected=529, gaussian_image_filter_sd=1,r_max=160)
distorted_volume_rev.export_to_slicer()
distorted_volume.export_to_slicer()
# ground truth centroids
ground_truth_volume = MarkerVolume(data_loc / 'CT' / 'slicer_centroids.mrk.json', verbose=False, r_max=300)
# matched volumes
matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume, ReverseGradientData=distorted_volume_rev,
                                    ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv(data_loc / 'Matched_Markers.csv')  # for use in later examples

# check if max distortion exceeds some threshold
threshold = 5 #change this threshold if needed
distanceBetweenMarkers = []
for index in range(0,528): #distorted_volume_rev.MarkerCentroids.T:
    val = math.sqrt(pow(matched_volume.MatchedCentroids['x_gnl'][index] - matched_volume.MatchedCentroids['x_gt'][index], 2)
                              + pow(matched_volume.MatchedCentroids['y_gnl'][index] - matched_volume.MatchedCentroids['y_gt'][index], 2)
                              + pow(matched_volume.MatchedCentroids['z_gnl'][index] - matched_volume.MatchedCentroids['z_gt'][index], 2))
    distanceBetweenMarkers.append(val) #magnitude
    if val > threshold:
        print('The max distortion has exceeded the threshold')



# check if he distortion feild is not smoothly varying
tolerance = 10 # acceptable smoothing variation

nearby = 30 #acceptable distance between nearby markers
#for index1 in range(0,528): #change the number of points depending on marker points on phantom
xDirection = matched_volume.MatchedCentroids['x_gnl'] - matched_volume.MatchedCentroids['x_gt']
yDirection = matched_volume.MatchedCentroids['y_gnl'] - matched_volume.MatchedCentroids['y_gt']
zDirection = matched_volume.MatchedCentroids['z_gnl'] - matched_volume.MatchedCentroids['z_gt']

for index3 in range(0, 528):  # distorted_volume_rev.MarkerCentroids.T:
    xcoordinate = xDirection[index3]
    ycoordinate = yDirection[index3]
    zcoordinate = zDirection[index3]
    for index4 in range(0,528):
        if index3 != index4: #dont check the same point against itself
            xCalc = xcoordinate - xDirection[index4]
            yCalc = ycoordinate - yDirection[index4]
            zCalc = zcoordinate - zDirection[index4]
            value = math.sqrt(pow(xCalc, 2)
                              + pow(yCalc, 2)
                              + pow(zCalc, 2))
            if value < nearby: #if nearby check if its within the tolerance
                if (xCalc or yCalc or zCalc) > tolerance:
                    print('distortion field is not smoothly varying')
