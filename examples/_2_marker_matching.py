import math
import sys
from pathlib import Path
#sys.path.insert(0, 'C:/Users/Brendan/Documents/python/MRI_DistCorrectionPhantom')
from MRI_DistortionQA.MarkerAnalysis import MarkerVolume
from MRI_DistortionQA.MarkerAnalysis import MatchedMarkerVolumes
import numpy as np
import csv
from csv import writer


this_file_loc = Path(__file__).parent.resolve()
data_loc = this_file_loc / '_example_data'

# distorted centroids
distorted_volume = MarkerVolume(data_loc / 'MR' / '04 gre_trans_AP_330' / 'slicer_centroids.mrk.json', verbose=False)
distorted_volume_rev = MarkerVolume(data_loc / 'MR' / '05 gre_trans_PA_330' / 'slicer_centroids.mrk.json', verbose=False)

# ground truth centroids
ground_truth_volume = MarkerVolume(data_loc / 'CT' / 'slicer_centroids.mrk.json', verbose=False, r_max=300)

# matched volumes
matched_volume = MatchedMarkerVolumes(ground_truth_volume, distorted_volume, ReverseGradientData=distorted_volume_rev,
                                      ReferenceMarkers=11)
matched_volume.MatchedCentroids.to_csv(data_loc / 'Matched_Markers.csv')  # for use in later examples


fileToSearch = open('matchedMarkersRL.csv')
type(fileToSearch)
csvreader = csv.reader(fileToSearch)

header = []
header = next(csvreader)
#print(header)

rows = []
for row in csvreader:
        rows.append(row)
        #print(row)

fileToSearch.close()

#same for other file
fileToMatch = open('matchedMarkersLR.csv')
type(fileToMatch)
csvreader = csv.reader(fileToMatch)

header1 = []
header1 = next(csvreader)
#print(header)

rows1 = []

for row in csvreader:
        rows1.append(row)
        #print(row)

fileToSearch.close()

Searchx_gt = []
Searchy_gt = []
Searchz_gt = []
Matchx_gt = []
Matchy_gt = []
Matchz_gt = []

distance = []

for index in range(0,len(rows)):
    Searchx_gt.append(float(rows[index][5]))
    Searchy_gt.append(float(rows[index][6]))
    Searchz_gt.append(float(rows[index][7]))
    Matchx_gt.append(float(rows1[index][5]))
    Matchy_gt.append(float(rows1[index][6]))
    Matchz_gt.append(float(rows1[index][7]))

min_distance = 1000
min_index = 0
index_used = {}
newRl = []
newLr = []


for index in range(0, len(rows)):

    for index2 in range(0, len(rows1)):

        if index2 in index_used:

            distanceBetweenMarkers = math.sqrt(pow(Searchx_gt[index] - Matchx_gt[index2], 2)
                                               + pow(Searchy_gt[index] - Matchy_gt[index2], 2)
                                               + pow(Searchz_gt[index] - Matchz_gt[index2], 2))

            if len(distance) < len(rows):

                distance.append(distanceBetweenMarkers)

                if distanceBetweenMarkers < min_distance:
                    min_distance = distanceBetweenMarkers
                    min_index = index2

            if index2 == len(rows) - 1:
                newRl.append(rows[index])
                newLr.append(rows1[min_index])
                index_used[index2] = "true"

for index in range(0, len(newRl)):

    with open('newmatchedmarkersRL.csv', 'w+', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(newRl[index])
        f_object.close()

    with open('newmatchedmarkersLR.csv', 'w+', newline='') as object:
        writer_object = writer(object)
        writer_object.writerow(newLr[index])
        object.close()