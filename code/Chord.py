#!/usr/bin/env python3

from a440_dict import freq_mapping
from a440_dict import freq_values
from a440_train_vector import labels
from a440_train_vector import freqs

from bisect import bisect_left
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy.stats
import statistics
import sys
import wave


class Chord:
    """
    Create a chord object with a list of the three largest frequencies,

    A chord is made up of at least three distinct notes: while it seems
    reasonable to assume that the three discrete frequencies could be
    extracted by means of the fourier transform for straightforward chord
    identification, this is not the case. For that reason, a training
    set is necessary to tune noise consideration parameters.
    """

    def __init__(self, filename):
        """
        Initalizes chord object and attempts detection as well.
    
        filename : .wav file with associated music note.
                   As for this repository, the /data/music_notes directory
                   contains a variety of music files.
        """
        # Size of sampling chunk for wav file.
        self.chunk =  2048
        # Waveform object of existing file.
        self.waveform = wave.open(filename, 'rb')
        # Sample width.
        self.sample_width = self.waveform.getsampwidth()
        # Frame rate.
        self.frame_rate = self.waveform.getframerate()
        # List of most common frequencies.
        self.frequency_list = self.detect_frequency()
        self.chord = self.detect_chord()
        
    def __str__(self):
        """
        Returns value of the note for easy printing.
        """
        # TODO Return chord and classifier
        return self.chord


    def detect_frequency(self, num_notes=3):
        """
        Detects three most common frequencies in the chord. 
        """
        #### We average individual peaks to facilitate accurate extraction.
        # Create a list of the detected frequencies.
        frequency_list = []
        # Create a list of integers, useful to find the mode.
        frequency_int_list = []
        # Incorrect value facilitates debug nicely.
        frequency = -1

        #### Set up window functions and dataset.
        # Create a specific window for this process. Window should be 
        # double chunk size because values are interpolated.
        window = np.blackman(self.chunk*2)
        # Break the data into pieces in line with this window.
        data = self.waveform.readframes(self.chunk)
        
        #### Process each individual chunk.
        # Go through the dataset chunk-by-chunk.
        while (len(data) > self.chunk * self.sample_width) and \
              (len(data) % self.chunk * self.sample_width == 0):
            # Unpack dataset by piece of the sample set.
            data_set = np.array(wave.struct.unpack('%dh' % \
                                (len(data)/self.sample_width), data))*window
            # Take the square of the real fft because we only care about reals.
            fft_values = abs(np.fft.rfft(data_set))**2
            # Find the peak and then use quadratic interpolation to pull out 
            # the frequency unless we're just pulling out an endpiece.
            maximum_value = fft_values[1:].argmax() + 1
            if maximum_value != len(fft_values) - 1:
                a, b, c = np.log(fft_values[maximum_value-1:maximum_value+2:])
                interp = (c - a) * .5 / (2 * b - c - a)
                frequency = ((maximum_value + interp) * self.frame_rate)/ \
                            (self.chunk * 2)
            else:
                frequency = (maximum_value * self.frame_rate)/self.chunk
            # Increment location in dataset.
            data = self.waveform.readframes(self.chunk)
            # It needs to exist and humans should be able to hear it.
            if frequency > 0 and frequency < 20000:
                frequency_list.append(frequency)
                frequency_int_list.append(int(round(frequency)))
        
        #### Grab the average of the peaks.
        chord = []
        for i in range(num_notes):
            frequency = scipy.stats.mode(frequency_int_list)
            chord.append(frequency[0])
            frequency_int_list = [x for x in frequency_int_list if x != chord[i]]
        
        return chord

    def detect_chord(self):
        """
        Uses chord frequency list and KNN to determine value of a chord. 
        """
        distances = {}
        for i in range(len(labels)):
            distances[labels[i]] = \
                  Chord.euclidean_distance(freqs[i], self.frequency_list, len(freqs[i]))
       

        chord = min(distances.items(), key=lambda x: x[1])
        print(chord)
        return chord 

    @staticmethod
    def euclidean_distance(a, b, l):
        """
        Returns euclidean distance between two points in space. Exciting.

        a : First list (or other iterable) with coordinate.
        b : Second list (or other iterable) with coordinate.
        l : The length of the list.

        Returns the euclidean distance. Thanks geometry.
        """
        dist = 0
        for i in range(l):
            dist += pow((a[i] - b[i]), 2)
        return math.sqrt(dist)

 
def main():
    """
    Run the program, grabbing the first command line argument for the file
    to detect the note of and printing the predicted note.
    """
    filename = sys.argv[1]
    r = Chord(filename)


if  __name__ =='__main__':
    main()
