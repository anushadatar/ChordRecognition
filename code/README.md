# Code for linearity one final project.

## Note class
Recognizes note values from .wav files. Running Note.py with python3 and 
providing a .wav file (many exist in /data/music\_notes) will print the 
note and a confidence score to the console.

This defaults to using a scale where A4 is at 440Hz. To provide a new definition
file, include a dictionary of float keys and string values of the frequencies
and notes and also provide a sorted list of the possible frequencies.

To run note recognition on a file, run:

`$ python3 Note.py /your/file/here.wav'


## Chord Class
Recognizes chord values (for major chords on fourth octave) from .wav file.
Running Chord.py with python3 and providing a .wave file file (a test set
exists in /data/chords/test) will print the chord and distance from the 
training value (using KNearestNeighbors from the FFT values of the set).

This defaults to using a basic set of major chords. To provide a new definition
file, include a list of values (or add to the current one) and a list of 
frequencies in sublist form. Be sure to change the number of notes as needed as well!

To run chord recognition on a file, run:

`$ python3 Chord.py /your/file/here.wav'


