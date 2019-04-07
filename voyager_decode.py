import peakutils
import scipy.io.wavfile
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt


#Set variables - Most determined emperically.
WAVFILE = "./voyager_images.wav"    #Encoded image WAV file
SAVDIR = "./extracted/"                #Directory to save extracted images
OFFSET = 10**6                      #Samples to ignore at start of file
IMGDIST = 25 ** 4                   #Samples between images
IMGTHR = 0.85                       #Peak threshold %-age for image start
LINDIST = 10 ** 3                   #Samples between lines of an image
LINTHR = 0.7                        #Peak threshold %-age for line start
SCNWDTH = 700                       #Samples per image line


#Read audio file, split into left and right channels, then normalize.
rate, data = scipy.io.wavfile.read(WAVFILE)


#For each channel of audio (left and right).
for ch in range(2):

    #Keep track of which channel is being analyzed.
    chan = np.array(data[OFFSET:, ch])
    if ch == 0:
        ch_lbl = "L"
    else:
        ch_lbl = "R"

    #Make list of  containing image timepoint indices.
    image_idx = peakutils.indexes(chan, thres = IMGTHR, min_dist = IMGDIST)
    image_idx = np.hstack([image_idx, len(chan) - 1])
    
    #For each encoded message.
    for i in range(len(image_idx) - 1):
        #Define signal for this image.
        start = image_idx[i]
        end = image_idx[i + 1]
        signal = chan[start:end]
        
        #Estimate line start locations.
        peaks = peakutils.indexes(signal, thres = LINTHR, min_dist = LINDIST)
        
        image_data = np.zeros(SCNWDTH)
        for peak in peaks[:-1]:
            #Represent each scan line 3 times to result in 4:3 aspect ratio
            line = signal[peak:peak + SCNWDTH]
            image_data = np.vstack([image_data, line, line, line])
            
        #Correct image orientation.
        image_data = np.flip(ndimage.rotate(image_data, -90), 1)

        #Save PNG file.
        plt.imsave(SAVDIR + ch_lbl + str(i + 1) + ".png", image_data,
            format = "png", cmap = "Greys")
        plt.close("all")
