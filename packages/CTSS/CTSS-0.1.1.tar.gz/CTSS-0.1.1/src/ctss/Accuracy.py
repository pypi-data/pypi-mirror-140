#!/usr/bin/env python
# coding: utf-8

import numpy as np

class Accuracy:
    @staticmethod
    def blobs_in_roi(blobs, roi):
        """Check if the center of blob is inside ROI  

        Arguments
        blobs -- list or array of areas oссupied by the nanoparticle 
                (y, x, r) y and x are coordinates of the center and r - radius    
        roi -- (y,x,h,w)

        Return blobs list
        """
        indexes = list(map(lambda blob: int(blob[0]) >= roi[0]                                     and int(blob[1]) >= roi[1]                                     and int(blob[0]) < roi[0]+roi[2]                                      and int(blob[1]) < roi[1]+roi[3],                                         blobs))
        return np.copy(blobs[indexes])

    @staticmethod
    def findIOU4circle(c1, c2):
        """Finds Jaccard similarity measure for two circles, 
           defined by the coordinates of centers and radii.
           c1=[x1,y1,r1], c2=[x2,y2,r2]  
        """

        d = np.linalg.norm(c1[:2] - c2[:2]) #distance betweem centers

        rad1sqr = c1[2] ** 2
        rad2sqr = c2[2] ** 2

        if d == 0:
            # the circle centers are the same
            return min(rad1sqr, rad2sqr)/max(rad1sqr, rad2sqr)

        angle1 = (rad1sqr + d ** 2 - rad2sqr) / (2 * c1[2] * d)
        angle2 = (rad2sqr + d ** 2 - rad1sqr) / (2 * c2[2] * d)

        # check if the circles are overlapping
        if (-1 <= angle1 < 1) or (-1 <= angle2 < 1):
            theta1 = np.arccos(angle1) * 2
            theta2 = np.arccos(angle2) * 2

            area1 = (0.5 * theta2 * rad2sqr) - (0.5 * rad2sqr * np.sin(theta2))
            area2 = (0.5 * theta1 * rad1sqr) - (0.5 * rad1sqr * np.sin(theta1))

            return (area1 + area2)/(np.pi*(rad1sqr+rad2sqr) - area1 - area2)

        elif angle1 < -1 or angle2 < -1:
            # Smaller circle is completely inside the largest circle.
            # Intersection area will be area of smaller circle
            # return area(c1_r), area(c2_r)
            return min(rad1sqr, rad2sqr)/max(rad1sqr, rad2sqr)
        return 0

    @staticmethod
    def СonformBlobs(blobs_gt, blobs_est, roi, thres):
        blobs_gt = Accuracy.blobs_in_roi(blobs_gt, roi)
        blobs_est = Accuracy.blobs_in_roi(blobs_est, roi)  

        length_gt = blobs_gt.shape[0]
        length_est = blobs_est.shape[0]

        iou = np.zeros((length_gt, length_est))
        for i in range(length_gt):
            for j in range(length_est):
                iou[i,j] = Accuracy.findIOU4circle(blobs_gt[i], blobs_est[j])

        diff_blobs = []

        for i in range(length_gt):
            if (max(iou[i]) >= thres):
                imax = np.argmax(iou[i])
                if (i == np.argmax(iou[:, imax])):            
                    diff_blobs.append(blobs_gt[i] - blobs_est[imax])

        return diff_blobs
    
    @staticmethod
    def AccInfo(blobs_gt, blobs_est, roi, thres):
        blobs_gt = Accuracy.blobs_in_roi(blobs_gt, roi)
        blobs_est = Accuracy.blobs_in_roi(blobs_est, roi)  

        length_gt = blobs_gt.shape[0]
        length_est = blobs_est.shape[0]

        iou = np.zeros((length_gt, length_est))
        for i in range(length_gt):
            for j in range(length_est):
                iou[i,j] = Accuracy.findIOU4circle(blobs_gt[i], blobs_est[j])

        match = 0
        no_match = 0
        fake = 0
        no_match_index = np.zeros(length_gt,dtype = 'bool')

        match_matr = np.zeros((length_gt, length_est), dtype = int)

        for i in range(length_gt):
            if max(iou[i])>=thres:
                imax = np.argmax(iou[i])
                match_matr[i,imax] = 1

        fake_index = np.zeros(length_est,dtype = 'bool')
        for j in range(length_est):
            if sum(match_matr[:,j])>1: 
                imax = np.argmax(iou[:,j])
                match_matr[:, j] = np.zeros(length_gt, dtype = int)
                match_matr[imax, j] = 1 
            if sum(match_matr[:,j]) == 0:
                fake+=1
                fake_index[j] = True
        fake_blobs = blobs_est[fake_index]

        for i in range(length_gt): 
            if sum(match_matr[i,:]) == 0: 
                no_match_index[i] = True

        no_match = sum(no_match_index)
        match = sum(sum(match_matr))        
        no_match_gt_blobs =  blobs_gt[no_match_index]       

        return match, no_match, fake, no_match_gt_blobs, fake_blobs
    
    @staticmethod
    def Acc(blobs_gt, blobs_est, roi, thres):
        blobs_gt = Accuracy.blobs_in_roi(blobs_gt, roi)
        blobs_est = Accuracy.blobs_in_roi(blobs_est, roi)  

        length_gt = blobs_gt.shape[0]
        length_est = blobs_est.shape[0]

        iou = np.zeros((length_gt, length_est))
        for i in range(length_gt):
            for j in range(length_est):
                iou[i,j] = Accuracy.findIOU4circle(blobs_gt[i], blobs_est[j])

        match = 0
        for i in range(length_gt):
            if (max(iou[i]) >= thres):
                imax = np.argmax(iou[i])
                if (i == np.argmax(iou[:, imax])):            
                    match = match + 1 
                            
        return match/(length_gt+length_est-match)
    
    @staticmethod
    def TableMatchAlgoritms(reviewAreas:list, roi):
        countAreas = len(reviewAreas)
        table = np.ones([countAreas, countAreas],'float')

        for i in range(countAreas):
            for j in range(i, countAreas):
                if (i != j):                                   
                    table[i,j] = Accuracy.Acc(reviewAreas[i], reviewAreas[j], roi, 0.25) 
                    table[j,i] = table[i,j]

        return table