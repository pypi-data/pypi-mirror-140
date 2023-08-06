#!/usr/bin/env python
# coding: utf-8

import numpy as np

class Statistica:
   
    # Наблюдаемое значение критерия Пирсона для проверки гипотезы о равномерности распределения
    # f_observed - матрица наблюдаемых частот попадания в подобласти
    @staticmethod
    def pirsonCriterion(f_observed):        
        # общее число наблюдений:
        n = sum(sum(f_observed))
        # число интервалов:
        (nx,ny) = np.shape(f_observed)
        k = nx*ny
        # теоретическая частота:
        f_teor = n/k
        # Наблюдаемое значение критерия Пирсона:
        pirs_obs = sum(sum((f_observed - f_teor)**2/f_teor))
        
        return pirs_obs        
    
    @staticmethod
    def uniformity(blobs, height, width, sizeBlock):
        heightBlocks = math.ceil(height/sizeBlock)
        widthBlocks = math.ceil(width/sizeBlock)     
        
        if ( (sizeBlock*heightBlocks != height) or (sizeBlock*widthBlocks != width) ):
            print("\nWARNING: Высота или длина изображения не делится на заданный размер блока нацело!\n")
        
        counter = np.zeros((heightBlocks, widthBlocks), dtype=int)
        
        for blob in blobs:
            y,x,r = blob
            i = math.ceil(y/sizeBlock)-1
            j = math.ceil(x/sizeBlock)-1
            counter[i, j] += 1
        
        print("Размер подобласти (NxN) в пикселях:", sizeBlock, "\tЧисло подобластей:", heightBlocks*widthBlocks)
        pirs_obs = Statistica.pirsonCriterion(counter)
        print("Наблюдаемое значение критерия Пирсона:", pirs_obs)
        print("Наблюдаемое значение критерия Пирсона, деленное на число подобластей:",
              pirs_obs/(heightBlocks*widthBlocks))       
        
        return counter

    @staticmethod
    def printStat(arr):
        print('\tчисло различных значений:', len(set(arr)))
        print('\tминимум:', np.min(arr))
        print('\tмаксимум:', np.max(arr))      
        print('\tсреднее:', np.mean(arr))              
        print('\tмедиана:', np.median(arr))
        print('\tСКО:', np.std(arr))
    
    @staticmethod
    def showRadiusInformation(blobs):
        R = blobs[:, 2]
        print('Всего найдено наночастиц: ', blobs.shape[0])
        print('Cтатистика по размерам:')
        Statistica.printStat(R)
        radius, count = np.unique(R, return_counts=True)
        print('Количество частиц каждого из радиусов (радиус:количество частиц)')
        print([str(np.round(radius[i], 2))+":"+str(count[i]) for i in range(0, len(radius))])
    
    # Евклидово расстояние
    @staticmethod
    def findEuclideanDistances(blobs):
        nblobs = np.shape(blobs)[0]
        dist = np.zeros((nblobs, nblobs),dtype = float)
        for i in range(nblobs):
            for j in range(nblobs):
                dist[i,j] = np.sqrt((blobs[i,0]-blobs[j,0])**2 + (blobs[i,1]-blobs[j,1])**2)
        return dist
    
    # Расстояние Чебышева
    @staticmethod
    def findModulDistances(blobs):
        nblobs = np.shape(blobs)[0]
        dist = np.zeros((nblobs, nblobs),dtype = float)
        for i in range(nblobs):
            for j in range(nblobs):
                dist[i,j] = max(np.abs(blobs[i,0]-blobs[j,0]), np.abs(blobs[i,1]-blobs[j,1]))
        return dist
    
    # 
    # distance - набор расстояний, для которых считается доп. статистика
    #    о числе ближайших частиц (если список пуст, статистика не считается)
    @staticmethod
    def distance(blobs):
        dist = Statistica.findEuclideanDistances(blobs)
        
        nblobs = np.shape(blobs)[0]
        minDist = np.min(dist+np.eye(nblobs, nblobs)*99999,0)
        
        print('Статистика по расстояниям до ближайшей наночастицы:')
        Statistica.printStat(minDist)        
        
        return dist, minDist