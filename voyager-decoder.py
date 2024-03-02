import numpy as np
from pathlib import Path
from PIL import Image
import scipy
import sys


# Set constants.
WAVFILE = Path(sys.argv[1])
OUTDIR = Path(Path(__file__).parent / "extracted")

# These constants were discovered empirically.
SCANWIDTH = 3300
THICKNESS = 15

# Define index of grouped color image channels.
color_index = [(7, 8, 9), (13, 14, 15), (16, 17, 18), (28, 29, 30),
               (41, 42, 43), (44, 45, 46), (47, 48, 49), (58, 59, 60),
               (61, 62, 63), (65, 66, 67), (68, 69, 70), (71, 72, 73),
               (78, 79, 80), (85, 86, 87), (105, 106, 107), (118, 119, 120),
               (125, 126, 127), (130, 131, 132), (147, 148, 149),
               (151, 152, 153)]

# Define index of images that are in the portrait orientation.
portrait_index = [12, 13, 14, 15, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                  38, 39, 40, 41, 42, 43, 44, 45, 46, 52, 61, 62, 63, 65, 66,
                  67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 85,
                  86, 87, 90, 91, 93, 95, 96, 103, 114, 124, 125, 126, 127,
                  129, 133, 137, 150, 155]

# Define portrait index requiring counter clockwise rotation.
ccw_index = [12, 13, 14, 15, 74, 155]


# Read in WAV file data and associated sampling rate.
rate, data = scipy.io.wavfile.read(WAVFILE)

# Initialize image list.
images = []

# Iterate across audio channels.
for channel in data.transpose():

    # Normalize data for current channel.
    channel /= np.max(np.abs(channel))

    # Get the first 30s of audio for start tone removal.
    first_30s = channel[:30 * rate]
    
    # Find the end of the audio start tone.
    start_tone, _ = scipy.signal.find_peaks(-first_30s,
                                            height = np.max(-first_30s) - 0.2)

    # Remove start tone from audio data.
    channel = channel[start_tone[-1]:]

    # Get signal peaks corresponding to image timepoint indices.
    img_index, _ = scipy.signal.find_peaks(channel,
                                           height = np.max(channel) - 0.2,
                                           distance = rate / 5)

    # Iterate through each encoded image.
    for start, end in zip(img_index, np.append(img_index[1:], len(channel))):

        # Get signal encoding current image.
        img_signal = channel[start: end]


        # Search for and remove image boundary markers in image signal.
        for _ in range(2):

            # Get image boundary marker locations.
            tenth = img_signal[:len(img_signal) // 10]
            boundary_index, _ = scipy.signal.find_peaks(tenth, height = 0.7)

            # Remove signal peaks corresponding to image boundary markers.
            if boundary_index.size > 0:
                img_signal = img_signal[boundary_index[-1]:]

            # Flip the image.
            img_signal = img_signal[::-1]

        # Get signal peaks corresponding to each image row scan.
        row_index, _ = scipy.signal.find_peaks(img_signal,
                                               height = 0.05,
                                               distance = rate / 100)

        # Initialize blank canvas for extracted image.
        img_data = np.zeros(SCANWIDTH)

        # Iterate through each row in the image.
        for row_signal in row_index[2: -2]:
            line = img_signal[row_signal: row_signal + SCANWIDTH]

            # Ignore blank space flanking each image.
            if np.mean(line[0:100]) >= 0.15:

                # Each line repeats THICKNESS times set by calibration circle.
                img_data = np.vstack([img_data] + [line] * THICKNESS)

        # Correct image orientation.
        img_data = np.flip(scipy.ndimage.rotate(img_data, -90), 1)

        # Get upper and lower percentiles of image data.
        low = np.percentile(img_data, 2)
        high = np.percentile(img_data, 98)
        
        # Normalize image contrast and invert image.
        img_data = np.clip(img_data, low, high)
        img_data = 255 - ((img_data - low) / (high - low)) * 255
        
        # Add extracted image to list of images.
        images.append(img_data)


# Create output directory if it does not already exist.
Path(OUTDIR).mkdir(parents=True, exist_ok=True)

# Render each extracted monochrome image.
for i, img in enumerate(images):

    # Correct orientation of portrait images.
    if i in portrait_index:

        # Rotate counter clockwise if appropriate.
        if i in ccw_index:
            img = scipy.ndimage.rotate(img, 90)

        # Rotate clockwise if appropriate.
        else:
            img = scipy.ndimage.rotate(img, -90)

    # Gamma correct image.
    mono_render = Image.fromarray(img.astype(np.uint8))
    mono_render = mono_render.point(lambda x: ((x / 255) ** 1.3) * 255)

    # Save monochrome image file.
    mono_render.save(OUTDIR / f"mono{i:03d}.png")


# Composite and render each extracted color image.
for colors in color_index:

    # Get RGB channels for color image.
    r, g, b = [images[c] for c in colors]

    # Crop image to smallest sized channel.
    edge = min(max(r.shape), max(g.shape), max(b.shape))
    r, g, b = (r[:,:edge], g[:,:edge], b[:,:edge])

    # Combine color channels into a single image.
    color_img = np.dstack((r,g,b))

    # Rotate the image the correct orientation.
    if colors[0] in portrait_index:

        # Rotate counter-clockwise if appropriate.
        if colors[0] in ccw_index:
            color_img = scipy.ndimage.rotate(color_img, 90)

        # Rotate clockwise if appropriate.
        else:
            color_img = scipy.ndimage.rotate(color_img, -90)

    # Gamma correct image.
    color_render = Image.fromarray(color_img.astype(np.uint8))
    color_render = color_render.point(lambda x: ((x / 255) ** 1.6) * 255)

    # Save color image file.
    color_render.save(OUTDIR / f"color{colors[0]:03d}-{colors[-1]:03d}.png")
