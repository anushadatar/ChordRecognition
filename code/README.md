# Code for linearity one final projet.

## Note class
Recognizes note values from .wav files. Running Note.py with python3 and 
providing a .wav file (many exist in /data/music\_notes) will print the 
note and a confidence score to the console.

This defaults to using a scale where A4 is at 440Hz. To provide a new definition
file, include a dictionary of float keys and string values of the frequencies
and notes and also provide a sorted list of the possible frequencies.

To run note recognition on a file, run:




`$ python3 Note.py /your/file/here.wav'

