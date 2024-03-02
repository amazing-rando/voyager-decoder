# Decoding Voyager's Golden Record

![Photograph of the engraved case that houses the Voyager probe's golden record.](./images/record.png)

In the event that an intelligent extraterrestrial being ever comes across either of the two [Voyager](https://voyager.jpl.nasa.gov/) probes, they'll be able to get a good idea about humanity by the data stored in an enclosed time-capsule-like [golden record](https://en.wikipedia.org/wiki/Voyager_Golden_Record).  Above is a depiction of the engraved case containing each of these golden records.  These engravings explain how the record's data can be accessed.

![Detailed diagram of the Voyager probe's engraved record case.](./images/explanation.png)

One side of the record contains [audio recordings](https://ozmarecords.com/pages/voyager) that include greetings in multiple languages as well as sounds and music from around the world.  The other side of this record, however, contains a series of 115 images compiled by [Carl Sagan](https://en.wikipedia.org/wiki/Carl_Sagan).  These images are stored as audio split across both left and right stereo channels.  Using the instructions engraved on the record's cover, Voyager's encoded images can be visualized using Python!

![Decoded image depicting the composition of DNA.](./extracted/mono020.png)

Above is an example of the image data contained on the record.  These images span a range of subject matter including the natural, cultural, and scientific.  Although many of the [original images](https://voyager.jpl.nasa.gov/golden-record/whats-on-the-record/images/) are available online, there is something special about extracting them from the record's signal.

![Decoded color image of the Earth with the chemical composition of our atmosphere superimposed.](./extracted/color016-018.png)

The code provided here takes a user specified WAV file containing images encoded in the same manner as those found on the Voyager space probe's golden record and outputs each of these images as separate grayscale PNG files.  Images that come in sets of 3 are in color and represent blue, green, and red channels in order.  All graphics extracted from the golden record's data (including color images like the one seen above) have been included here in the *extracted* folder.

## Dependencies

To install dependencies, run:

```
pip install -r requirements.txt
```

## Decoding Images

For this code to successfully run, it must be provided with an audio file containing images encoded in the same manner as those found on the Voyager space probe's golden record.  For reference, an archival copy of the golden record's encoded images has been provided as a [WAV (1.4GB)](https://archive.org/details/voyager_images_384khz).

The decoding script is executed by running:

```
python voyager_decoder.py voyager_images_384khz.wav
```

Images are extracted using a signal processing based approach.  This works because image and row indices are indicated by audible beeps.  These beeps are referenced using a simple peak detection algorithm.  Image scan width and row thickness constants were discovered emperically through the use of the calibration circle encoded as the first image on the left channel.

Indices for color image groups and portrait image representation were manually determined.


## Acknowledgements

This project was inspired by [foodini](https://github.com/foodini/voyager)'s decoder written in C++.
