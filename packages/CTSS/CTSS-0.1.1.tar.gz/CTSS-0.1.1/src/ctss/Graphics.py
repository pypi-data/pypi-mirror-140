#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt

class Graphics:

    @staticmethod
    def createTwoPlot(image, blobs, title = "", flagPaintParticles = False, color = 'blue', size = 6):
        fig, (ax_im, ax_second) = plt.subplots(1, 2, figsize=(size*2,size), sharex=False, sharey=False)

        ax_im.imshow(image, cmap='gray', aspect='auto')       
        ax_im.set_axis_off()        
        ax_im.set_title(title)

        if (flagPaintParticles):
            for blob in blobs:
                y, x, r = blob
                c = plt.Circle((x, y), r, color=color, linewidth=1, fill=False)
                ax_im.add_patch(c)

        plt.tight_layout()
        return ax_second
    
    # Формирует столбчатую диаграмму
    # array - полный набор данных, по которому строится диаграмма
    # axis - оси в которых будет отображаться диаграмма
    # gap - процентное отношение ширины столбца к ширине зазора между соседними столбцами
    # is_norm - нормированная диаграмма (по умолчанию не нормированная)
    @staticmethod
    def createBar(array, axis, gap=0.08, is_norm=False):
        value, hieght = np.unique(array, return_counts=True)
        width = np.diff(value)
        width = np.append(width, width[-1])   

        if (is_norm):
            axis.bar(value, hieght/len(array), width - width*gap, alpha = 0.5)
            axis.set_ylim(0, 1)
        else:
            axis.bar(value, hieght, width - width*gap, alpha = 0.5)

        axis.set_xticks(value)
        axis.set_xticklabels(["{0:.0f}".format(value[i]) for i in range(0, len(value))])
