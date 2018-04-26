#!/usr/bin/env python

import numpy as np
import statistics
import sys
import wave


class Note:
    """
    Generalized note class for single musical note.
    
    
    """
    def __init__(self, filename):
        """
        Initalizes note object and attempts detection as well.
    
        filename : .wav file with associated music note.
        """
        # Frequency of the note. Found during value calculation.
        # Initialize to invalid frequency to simplfy debugging.
        self.frequency = -1
        # Confidence in note value detection.
        # Based on naive guess based on statistics.
        self.confidence = -1

        # Waveform object of existing file.
        self.waveform = wave.open(filename,'rb')
        # Sample width of existing waveform - bits required / second.
        self.sample_width = self.waveform.getsampwidth()
        # Frame rate of existing waveform - frames / second.
        self.frame_rate = self.waveform.getframerate()
        # Size of sampling chunk.
        self.chunk = 2048
        # Predicted note and confidence. In array [value confidence].
        self.value = self.detect_note()
        


    def __str__(self):
        """
        Returns value of the note.
        """
        return str(self.frequency)

    def detect_frequency(self):
        # Create a specific window for this process. Window should be 
        # double chunk size because values are interpolated.
        window = np.blackman(self.chunk*2)
        # Break the data into pieces in line with this window.
        data = self.waveform.readframes(self.chunk)
        # Set the frequency to something incorrect by definition such that
        # we can go back and debug easily.
        frequency = -1
        # Go through the dataset chunk-by-chunk
        while (len(data) > self.chunk * self.sample_width) and \
              (len(data) % self.chunk * self.sample_width == 0):
            # Unpack dataset by piece of the sample set.
            data_set = np.array(wave.struct.unpack('%dh' % \
                                (len(data)/self.sample_width), data))*window
            fft_values = abs(np.fft.rfft(data_set))**2
            maximum_value = fft_values[1:].argmax() + 1
            if maximum_value != len(fft_values) - 1:
                a, b, c = np.log(fft_values[maximum_value-1:maximum_value+2:])
                interp = (c - a) * .5 / (2 * b - c - a)
                frequency = ((maximum_value + interp) * self.frame_rate)/ \
                            (self.chunk * 2)
            else:
                frequency = (maximum_value * self.frame_rate)/self.chunk
            data = self.waveform.readframes(self.chunk)
        if frequency != -1:
            self.frequency = frequency
            return frequency
        else:
            print("Frequency calculation failed.") 

    def detect_note(self):
        frequency = self.detect_frequency()
        print(frequency)



def main():
    """
    Run the program, grabbing the first command line argument for the file
    to detect the note of and printing the predicted note.
    """
    filename = sys.argv[1]
    print(filename)
    r = Note(filename)
    print(r)


if  __name__ =='__main__':
    main()
