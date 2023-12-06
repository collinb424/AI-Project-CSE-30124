# AI-Project-CSE-30124: Text Editor with Autocorrect and Next Word Prediction

This project is a text editor built in Python, featuring autocorrect and next-word prediction capabilities.

## File Description

### autocorrect.py
- This file contains the `AutoCorrect` class, responsible for correcting spelling mistakes in real-time.
- It uses a variation of the Levenshtein distance algorithm to compute the distance between the user's misspelled word and all the possible words within one to two edits away.
- It uses a large corpus of text, `data/large.txt`, and counts the occurrences of every word in the text.
- These counts are used to compute probabilities to decide the most probable correction for the user’s misspelled word.


### next_word.py
- This file includes the `TextProcessor` and `NextWordPredictor` classes.
- The `TextProcessor` class is used for reading and processing text data from `data/sentences.txt` by tokenizing sentences and creating padded sequences.
- The `NextWordPredictor` class uses TensorFlow and Keras to build and train an LSTM model for predicting the next word in a sentence.
- This script generates the file `my_model.h5`.

### text-editor.py
- This file integrates `AutoCorrect` and `NextWordPredictor` into a GUI-based text editor using Tkinter.
- This file is the main interface for the text editor.
- When a user types a word incorrectly and then hits space, if the autocorrect found a word that the user more likely meant, it will automatically change the word to that.
- The next-word predictor will also run after the user hits space, and in a light gray font, it will show the suggested next word. The user can then hit tab to go with this suggested word, or continue typing to ignore this word.

## Setup and Running Instructions

1. **Clone this repository to your local machine**:
   ```bash
   $ git clone https://github.com/collinb424/AI-Project-CSE-30124.git
   ```
2. **Ensure all necessary files are present**:
   - Ensure you have the following python files: `text-editor.py`, `autocorrect.py`, `next_word.py`.
   - Ensure you have the following text files in the data folder: `data/large.text`, `data/sentences.txt`.
   - Ensure you have the model so that you don't need to spend time retraining it: `my_model.h5`
3. **Install Dependencies**:
   - Ensure Python is installed on your system.
   - Also ensure you have pip installed on your system.
   - Then install necessary packages using:
   ```bash
   $ pip install numpy tensorflow re tkinter
   ```
4. **Run the Text Editor**:
   - Run `text-editor.py` to start the application:
   ```bash
   $ python3 text-editor.py
   ```
5. **Using the Text Editor**:
   - The text editor will open in a new window.
   - Simply start typing your text.
   - If you mistype a word and press space, the editor will automatically correct it to the most likely intended word.
   - Upon hitting the space bar, a suggestion for the next word will appear in gray. To accept this suggestion, press Tab. If you wish to ignore it, just keep typing as usual.
