#!/usr/bin/env python

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

    Some valuable and achievable TODOs to reduce this noise include:
        - Evaluating different window types instead of just going with 
          what is generally standard practice (Blackman window).
          - Go to numpy directories and compare confidence scores based 
            on changing window sizes. Window type is set at line 81. 
        - Takking a weighted average of found frequencies for windows instead
          of blindly choosing the final value calculated. Probably involves 
          storing all of the values in a list and then moving them around.
          - Accounting for harmonics and large outliers in this calculation.
    
    Stretch considerations:
        - Using a training set to determine sliding parameters instead of just
          basic statistics calculations.
        - Filtering for various outside noises.
    
    Software TODOs Include:
        - Professional documentation is always a good touch. READMEs, 
          pointing to LaTeX, all of these things are nice to have.
        - Object-orientedness is nice, but so is modularizability. Add in
          some nice default arguments for things and get rid of all the 'self'
        - Define how this fits in with chords, which is decidedly much 
          harder.
        - Real-time functionality would be hard, but also very cool.
          - Need a nice, clean audio stream (microphone? microphone)
          - A gui or something wouldn't hurt.
        - Plotting the fft at some point would be good for the report, if 
          not for the cool and intuitive GUI you're going to totally make.
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


    def __str__(self):
        """
        Returns value of the note for easy printing.
        """
        # TODO This should eventually return a nice string with the name
        #      of the note and the confidence level. 
        return str(self.frequency)

    def detect_frequency(self):
        """
        Returns dominant frequency of the waveform.
        
        Takes in most setup variables, chunks up the data, and then 
        uses real fft, chunk by chunk, to calculate frequency.
        Then uses quadratic interpolation to pinpoint peak.

        Returns frequency in Hertz (Hz)    
        """
        # TODO The range this works for is pretty limited. How to expand?

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

        # Check for valid frequencies and then return.
        if frequency != -1:
            self.frequency = frequency
            return frequency
        else:
            print("Frequency calculation failed.") 
            return -1
    
    def note_and_confidence(self):
        """
        Detects the value of the note and confidence percentage for a given
        frequency.

        Returns an array where the first element is the note as a string and
        the second element is the confidence as a decimal.
        """   
        # TODO Implement this: For that, create a dictionary of the notes
        # and associated frequencies and do some arithmetic to determine
        # the confidence at the point.
        if (self.frequency < 0):
            self.frequency = self.detect_frequency()

    def detect_note(self):
        """
        Note detection and confidence calculation - leverages setup from 
        object initialization and note and confidence values.

        Returns an array where the first element is the note as a string
        and the second element is the confidence as a decimal.
        """
        frequency = self.detect_frequency()
        value = note_and_confidence()
        self.note = value[0]
        self.confidence = value[1]
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
