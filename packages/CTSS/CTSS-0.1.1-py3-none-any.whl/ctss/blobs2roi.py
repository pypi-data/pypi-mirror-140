#!/usr/bin/env python
# coding: utf-8

import numpy as np

def blobs2roi(_blobs, _heightImg, _widthImg):
    roi = np.zeros(4, dtype='int')
    roi[0] = max(0, (_blobs[:,0]-_blobs[:,2]).min()) 
    roi[1] = max(0, (_blobs[:,1]-_blobs[:,2]).min())
    roi[2] = min(_heightImg, (_blobs[:,0]+_blobs[:,2]).max() - roi[0]+1)
    roi[3] = min(_widthImg, (_blobs[:,1]+_blobs[:,2]).max() - roi[1]+1)
    return roi 
