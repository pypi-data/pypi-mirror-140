#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

# Приведение разметки экспертов к унифицированному виду: "центр_по_У, центр_по_Х, радиус"
def gt2blobs(_pathCoordGT, _pathRadiiGT, _heightImg):
    gt_coords = pd.read_excel(_pathCoordGT, header = None, nrows = 2, engine='openpyxl')
    gt_unit = pd.read_csv(_pathRadiiGT, sep = ';')

    # replace не работае, если вещественное число уже записано через точку
    temp_length_pix = gt_unit[gt_unit['Unit']=='pixels']['Length'][0]
    if (not isinstance(temp_length_pix, float)):    
        length_pix = float(temp_unit.replace(',', '.'))
    else:
        length_pix = temp_length_pix
    length_nm = np.linalg.norm(gt_coords[[0,1]].diff(),axis=1)[1]
    coeff_nm2pix = length_pix/length_nm
    
    gt_blobs = []
    for col in range(2,gt_coords.shape[1],2):
        line = gt_coords[[col, col+1]]
        x,y = np.array(line.mean())*coeff_nm2pix
        r = np.linalg.norm(line.diff(),axis=1)[1]*coeff_nm2pix / 2.
        gt_blobs.append([_heightImg-y,x,r])
    gt_blobs = np.array(gt_blobs)
    
    return gt_blobs
