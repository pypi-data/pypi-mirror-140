from .Accuracy import Accuracy
from .blobs2roi import blobs2roi
import csv
import numpy

def jakkarAccuracy(pathFileGT, pathFileEst, roi=None, threshold=0.25):

    with open(pathFileGT, 'r') as FileGT:
        reader = csv.reader(FileGT)
        gt_blobs = numpy.array(list(reader), dtype=float)

    with open(pathFileEst, 'r') as FileEst:
        reader = csv.reader(FileEst)
        est_blobs = numpy.array(list(reader), dtype=float)

    if (roi==None):
        roi = blobs2roi(gt_blobs, 960, 1280)
        print("Warning! TODO: размеры изображения!")
    
    return Accuracy.Acc(gt_blobs, est_blobs, roi, threshold)