from PIL import Image
from scipy import ndimage
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import glob


#Set variables.
IMGDIR = "./test-images/"           #Directory containing images
OUTFILE = "test.wav"                #Output file name
LINSCALE = 0.6                      #Max scale for "line start" signal
IMGSCALE = 0.4                      #Max scale for image data
SCNWDTH = 700                       #Number of samples per line
IMGWDTH = 512                       #Actual image width
RATE = 44100                        #Sample rate
FREQ = SCNWDTH * 4                  #Frequency for line and image start signals
NSAMP = (SCNWDTH - IMGWDTH) // 3    #Number of samples for image start signals


#Get list of images for encoding.
file_list = glob.glob(IMGDIR + "*.png")

#Initiate signal constituents.
imgsig = np.sin(2 * np.pi * FREQ * np.arange(NSAMP) / RATE)
linsig = LINSCALE * imgsig
spacer = np.zeros(NSAMP)

#Initiate final output channels with leading silence.
lchan = np.zeros(RATE * 2)
rchan = lchan


#Do for each image
for i, f in enumerate(file_list):

    #Load image in grayscale.
    img = Image.open(f).convert("L")

    #Scale "width" to IMGWDTH along with "height".
    wpercent = (IMGWDTH / img.size[1])
    hsize = round(img.size[0] * wpercent)
    img = np.array(img.resize((hsize, IMGWDTH), Image.ANTIALIAS))
    
    #Flip and rotate image.
    img = ndimage.rotate(np.flip(img,1), 90)
    
    #Normalize.
    img = img / np.max(img)

    #Begin encoded message with "new image" blip.
    enc_img = imgsig

    #For each line in the image.
    for row in img:
        enc_img = np.hstack((enc_img, spacer, linsig, spacer,
                             row * IMGSCALE, spacer))

    #If the image is odd in our list, store it in the left channel.
    #Otherwise, store it in the right channel.
    if i % 2 == 0:
        rchan = np.hstack((rchan, spacer, enc_img))
    else:
        lchan = np.hstack((lchan, spacer, enc_img))

#If left and right channels are different lengths, then pad with silence.
if len(lchan) > len(rchan):
    rchan = np.pad(rchan, (0,len(lchan) - len(rchan)), 'constant')
elif len(rchan) > len(lchan):
    lchan = np.pad(lchan, (0,len(rchan) - len(lchan)), 'constant')

#Write WAV file.
wavdata = np.transpose(np.vstack((rchan,lchan)))
wavfile.write(IMGDIR + OUTFILE, RATE, wavdata)
