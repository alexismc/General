# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:51:16 2013

@author: Administrator
"""
import numpy as np
import os
import fnmatch
import textwrap as wrap
from osgeo import gdal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats


def create_filelist(processing_dir, pattern):
    
    filelist = []
    
    for root, dirs, files in os.walk(processing_dir):
        for filename in fnmatch.filter(files, pattern):
            filelist.append(os.path.join(root, filename))
        
    return filelist
    
def find_size(LS7size, LS8size):
    if (LS7size - LS8size) > 0:
        if LS8size%2 != 0:
            size = LS8size - 1
        else:
            size = LS8size

    else:
        if LS7size%2 != 0:
            size = LS7size - 1
        else:
            size = LS7size
    
    return size
    
def plot_data(LS7_subset_path, LS8_subset_path):
    
    path = os.path.basename(LS7_subset_path).split('_')[5]
    row = os.path.basename(LS7_subset_path).split('_')[6]
    date = os.path.basename(LS7_subset_path).split('_')[7]
    
    LS7image = gdal.Open(LS7_subset_path)
    LS8image = gdal.Open(LS8_subset_path)

    LS7band = LS7image.GetRasterBand(1)
    LS8band = LS8image.GetRasterBand(1)
        
    LS7y, LS7x = LS7band.YSize, LS7band.XSize
    LS8y, LS8x = LS8band.YSize, LS8band.XSize

    
    overlap_x = find_size(LS7x, LS8x)
    overlap_y = find_size(LS7y, LS8y)
    print overlap_y, overlap_x
    half_overlap_x = overlap_x/2
    
    parameters = [(0,0,half_overlap_x, overlap_y), (half_overlap_x+1, 0, half_overlap_x, overlap_y)]
    
#    LS7 = np.zeros((2,2))
#    LS8 = np.zeros((2,2))

    LS7max = []
    LS8max = []
    
    for n in parameters:
        
        x_off = n[0]
        y_off = n[1]
        x = n[2]
        y = n[3]
        
        LS7array = LS7band.ReadAsArray(x_off, y_off, x, y)
        print LS7array.shape
        LS8array = LS8band.ReadAsArray(x_off, y_off, x, y)
               
        LS7array = LS7array.reshape(y/2, 2, x/2, 2).transpose(0,2,1,3)
        LS7array = LS7array.reshape(y/2, x/2, 4).mean(axis=-1)
        
        LS7max.append(LS7array.max())
        
#        if LS7.max() ==0:
#            LS7 = LS7array
#        else:
#            LS7 = np.vstack((LS7, LS7array))
#
#        LS7array = None
        
        LS8array = LS8array.reshape(y/2, 2, x/2, 2).transpose(0,2,1,3)
        LS8array = LS8array.reshape(y/2, x/2, 4).mean(axis=-1)
        
        LS8max.append(LS8array.max())
        
#        if LS8.max() ==0:
#            LS8 = LS8array
#        else:
#            LS8 = np.vstack((LS8, LS8array))
#        
#        LS8array = None
        plt.plot(LS7array, LS8array, 'bo', alpha=0.3)
        
    LS7image = None
    LS8image = None
    LS7band = None
    LS8band = None

#    plt.plot(LS7, LS8, 'bo', alpha=0.3)
#    print LS7.max(), LS8.max()
    
    maxval = max(max(LS7max), max(LS8max))
    a = [0, maxval + 500, 0, maxval + 500]
    plt.axis(a)     

    title = 'Correlation of tandem data for Landsat 7 Band %s and Landsat 8 Band %s for Path %s, Row %s - %s' % (find_bandnumber(LS7_subset_path), find_bandnumber(LS8_subset_path), path, row, date)
    plt.title(title)
    
    plt.ylabel('Landsat 7')
    plt.xlabel('Landsat 8')

    return plt
    
def plot_data_subset(LS7band, LS8band, image_section, LS7bandnumber, path, row, date, processing_dir):
    
    bandnames = {1: 'Blue', 2: 'Green', 3: 'Red', 4: 'NIR', 5: 'SWIR1', 7: 'SWIR2'}
    months = {'01': 'January', '03': 'March', '10': 'October'}
             
#    LS7y, LS7x = LS7band.YSize, LS7band.XSize
#    LS8y, LS8x = LS8band.YSize, LS8band.XSize

    LS7max = []
    LS8max = []
    
       
    x_off = image_section[0]
    y_off = image_section[1]
    x = image_section[2]
    y = image_section[3]
    
    LS7array = LS7band.ReadAsArray(x_off, y_off, x, y)
    print LS7array.shape
    LS8array = LS8band.ReadAsArray(x_off, y_off, x, y)
           
    LS7array = LS7array.reshape(y/2, 2, x/2, 2).transpose(0,2,1,3)
    LS7array = LS7array.reshape(y/2, x/2, 4).mean(axis=-1)
    
    LS7max.append(LS7array.max())
           
    LS8array = LS8array.reshape(y/2, 2, x/2, 2).transpose(0,2,1,3)
    LS8array = LS8array.reshape(y/2, x/2, 4).mean(axis=-1)
    
    LS8max.append(LS8array.max())
    
    fig = plt.figure(LS7bandnumber)
    fig, ax = plt.subplots(1)
    plt.plot(LS7array, LS8array, 'bo', alpha=0.3)

        

#    plt.plot(LS7, LS8, 'bo', alpha=0.3)
#    print LS7.max(), LS8.max()
    
    maxval = max(max(LS7max), max(LS8max))
    plt.plot(np.arange(0, maxval+500), np.arange(0, maxval+500), 'k')
    print 'maxval =', maxval
    a = [0, maxval + 500, 0, maxval + 500]
    plt.axis(a)     
    
    LS8bandnumber = LS7bandnumber+1
    if LS7bandnumber == 6:
        LS7bandnumber = 7
    title = 'Tandem data for the %s band \n Path %s, Row %s - %s %s %s' % (bandnames[LS7bandnumber], path, row, date[6:], months[date[4:6]], date[0:4])
    plt.title(title)
#    plt.title('\n'.join(wrap(title,60)))
    
#    LS7arrayT = np.vstack([LS7array, np.ones(len(LS7array))]).T   
#    m, c = np.linalg.lstsq(LS7arrayT, LS8array)[0]
#    plt.plot(LS7array, m*LS7array + c, 'r', label='Fitted line')

    flatLS7array = LS7array.reshape(1,-1)
    flatLS7array[flatLS7array<0] = 0
    print flatLS7array
    flatLS8array = LS8array.reshape(1,-1)
    flatLS8array[flatLS7array==0] = 0
    print flatLS8array
    gradient, intercept, r_value, p_value, std_err = stats.linregress(flatLS7array, flatLS8array)
    print "Gradient and intercept", gradient, intercept
    print "R-squared", r_value**2
    print "p-value", p_value
    plt.plot(LS7array, gradient*LS7array + intercept, color='0.75', linewidth=0.1, label='Fitted line')
    r_sqd_text = "R-squared = %.4f" %r_value**2
    eq_text = "y = %.4fx + %.4f" % (gradient, intercept)
    plt.text(0.1,0.9, r_sqd_text, transform=ax.transAxes, fontsize=14, verticalalignment='top')
    plt.text(0.1,0.8, eq_text, transform=ax.transAxes, fontsize=14, verticalalignment='top')
    
    plt.ylabel('Landsat 8 surface reflectance x 1000')
    plt.xlabel('Landsat 7 surface reflectance x 1000')
    
    png_name = ''.join(["Tandem_LS7_", str(LS7bandnumber), "_LS8_", str(LS8bandnumber), '_', '_'.join([path, row, date, str(image_section[0]), str(image_section[1]), str(image_section[2]), str(image_section[3])])])

    output_png = os.path.join(processing_dir, "Output_graphs", png_name)
    plt.savefig(output_png)
    return plt

def find_bandnumber(path):
        
        bandnumber = [s[1] for s in fnmatch.filter(os.path.basename(path).split('_'), 'B*')][0]
        
        return bandnumber
        
def create_plots(processing_dir):
    
    LS7pattern = "LS7_ETM_NBAR_P54_GANBAR01-002_*_subset.dat"
    LS7list = create_filelist(processing_dir, LS7pattern)
    LS7pattern = None
    
    LS8pattern = "LS8_OLI_TIRS_NBAR_P54_GANBAR01_*_subset.dat"
    LS8list = create_filelist(processing_dir, LS8pattern)
    LS8pattern = None
    
    if not os.path.exists(os.path.join(processing_dir, "PDFs")):
            os.makedirs(os.path.join(processing_dir, "PDFs"))
    
    
    pdf = PdfPages(os.path.join(processing_dir, "PDFs", "Tandem_data_comparison_095_082_20130329.pdf"))
    
    for LS7_subset_path in LS7list:
        print "Processing: ", os.path.basename(LS7_subset_path)
        
        LS7bandnumber = find_bandnumber(LS7_subset_path)
        
        LS8bandnumber = ''.join(['*B', str(int(LS7bandnumber) + 1), '*'])
        
        fig = plt.figure(int(LS7bandnumber))
        
        LS8_subset_path = fnmatch.filter(LS8list, LS8bandnumber)[0]
        
        plot_data(LS7_subset_path, LS8_subset_path)

        pdf.savefig(fig)
    
    pdf.close()

def create_small_plots(processing_dir, image_section=[0,0,1000,1000], LS7pattern="LS7_ETM_NBAR_P54_GANBAR01-002_*_subset_stack.dat"):
        
    LS7list = create_filelist(processing_dir, LS7pattern)
    print LS7list
    LS7pattern = None
    
    LS8pattern="LS8_OLI_TIRS_NBAR_P54_GANBAR01_*_subset_stack.dat"
    LS8list = create_filelist(processing_dir, LS8pattern)
    print LS8list
    LS8pattern = None
    
    output_dir = os.path.join(processing_dir, "Output_graphs")
    pdf_dir = os.path.join(output_dir, "PDFs")
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

    
    for LS7_subset_path in LS7list:
        print "Processing: ", os.path.basename(LS7_subset_path)
        
        path = os.path.basename(LS7_subset_path).split('_')[5]
        row = os.path.basename(LS7_subset_path).split('_')[6]
        date = os.path.basename(LS7_subset_path).split('_')[7]
        
        LS8_subset_path = fnmatch.filter(LS8list, '_'.join(['*', path, row, date, '*']))[0]
        
        pdf = PdfPages(os.path.join(pdf_dir, '_'.join(["Tandem_data_comparison", path, row, date, str(image_section[0]), str(image_section[1]), str(image_section[2]), str(image_section[3]), ".pdf"])))
        
        LS7image = gdal.Open(LS7_subset_path)
        LS8image = gdal.Open(LS8_subset_path)
        
        for LS7bandnumber in range(1, LS7image.RasterCount+1):
            print "processing band: ", LS7bandnumber
            LS7band = LS7image.GetRasterBand(LS7bandnumber)
            LS8band = LS8image.GetRasterBand(LS7bandnumber)
        
            fig = plt.figure(LS7bandnumber)
        
            plot_data_subset(LS7band, LS8band, image_section, LS7bandnumber, path, row, date, processing_dir)
            

            pdf.savefig(fig)
    
    pdf.close()