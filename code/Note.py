#!/usr/bin/env python3

from a440_dict import freq_mapping
from a440_dict import freq_values

from bisect import bisect_left
import numpy as np
import statistics
import sys
import wave


class Note:
    """
    Generalized note class for single musical note.
    Assumes that A4 is tuned to 440 Hz.

    Given a wav file with the note, this program uses the fft algorithm
    for real values to evaluate the pitch class profile and match the 
    frequency of the note to its value.

    Considering this blindly uses frequency, it is highly susceptible to 
    noise across variables such as background frequencies and instruments.
    
    """
    def __init__(self, filename):
        """
        Initalizes note object and attempts detection as well.
    
        filename : .wav file with associated music note.
                   As for this repository, the /data/music_notes directory
                   contains a variety of music files.
        """
        #### Variables populated during value calculation. Initialized to
        #### unlikely values to facilitate debugging.
        # Frequency of the note. Found during value calculation.
        self.frequency = -1
        # Confidence in note value detection.
        self.confidence = -1
        # The actual note, as a string.
        self.note = ''

        ##### Existing class variables. Thanks python wave library.
        # Waveform object of existing file.
        self.waveform = wave.open(filename,'rb')
        # Sample width of existing waveform - bits required / second.
        self.sample_width = self.waveform.getsampwidth()
        # Frame rate of existing waveform - frames / second.
        self.frame_rate = self.waveform.getframerate()
        # Size of sampling chunk.
        self.chunk = 2048
        
        #### Finally, perform note detection.
        self.value = self.detect_note()


    def __str__(self):
        """
        Returns value of the note for easy printing.
        """
        if (self.value[0][1] == "S"):
            return ("Note: %s# Octave: %s Confidence: %.2f" % (self.value[0][0], \
                                                               self.value[0][2], \
                                                               self.value[1]))
        else:
            return ("Note: %s Octave: %s Confidence: %.2f" % (self.value[0][0], \
                                                              self.value[0][2], \
                                                              self.value[1]))


    def detect_frequency(self):
        """
        Returns dominant frequency of the waveform.
        
        Takes in most setup variables, chunks up the data, and then 
        uses real fft, chunk by chunk, to calculate frequency.
        Then uses quadratic interpolation to pinpoint peak.

        Returns frequency in Hertz (Hz)    
        
        This works surprisingly well for a few octaves below and above
        middle C. It loses accuracy at frequencies which are too low due
        to similar bins and 
        """

        #### We want to average the peaks to find the best possible value.
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
            if frequency > 0:
                frequency_list.append(frequency)
                frequency_int_list.append(int(round(frequency)))
        
        
        #### Grab the average of the peaks.
        frequency = statistics.mode(frequency_int_list)
        float_freq = 0
        float_freq_count = 0
        for i in range(len(frequency_list)):
            if frequency_int_list[i] == frequency:
                float_freq += frequency_list[i]
                float_freq_count += 1
        frequency = float_freq/float_freq_count
        
        # Double check it at least sort of worked and then return it.    
        if frequency > -1:
            self.frequency = frequency
            return frequency
        else:
            print("Frequency calculation failed.") 
            return -1
    
    def detect_note(self):
        """
        Note detection and confidence calculation - leverages setup from 
        object initialization and note and confidence values.

        Returns an array where the first element is the note as a string
        and the second element is the confidence as a decimal.
        """

        frequency = self.detect_frequency()
        find_closest = lambda num,collection:min(collection,key=lambda x:abs(x-num))
        closest_frequency = find_closest(frequency, freq_values)
        
        # Returns note in the form [LETTER][N OR S][OCTAVE]
        self.note = freq_mapping[closest_frequency]
        
        # Returns confidence based on literally just division
        self.confidence = 100 * ( 1 - 
                          abs((frequency - closest_frequency)/(frequency)))
        
        # Create data structure
        value = [self.note, self.confidence]
        
        return value

def main():
    """
    Run the program, grabbing the first command line argument for the file
    to detect the note of and printing the predicted note.
    """
    filename = sys.argv[1]
    r = Note(filename)
    print(r)


if  __name__ =='__main__':
    main()
