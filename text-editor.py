import tkinter as tk
from autocorrect import AutoCorrect
from next_word import TextProcessor, NextWordPredictor
from string import punctuation

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.text = tk.Text(root, wrap='word', width=70, height=20, font=("Arial", 15), selectforeground="black", undo=True)
        self.text.pack(expand=True, fill='both')

        self.text.bind('<space>', self.on_space)
        self.text.bind('<Control-z>', self.undo)
        self.text.bind('<Command-z>', self.undo)
        self.text.bind('<Tab>', self.on_tab)
        self.text.bind('<Key>', self.on_key_press)
        self.text.tag_configure('suggestion', foreground='gray')

        # History for undo functionality
        self.history = []
        self.undo_button = tk.Button(root, text="Undo", command=self.undo)
        self.undo_button.pack()

        # Initializing AutoCorrect and NextWordPredictor
        self.autocorrect = AutoCorrect()
        self.processor = TextProcessor('test.txt')
        self.processor.prepare_data()
        self.predictor = NextWordPredictor.load('my_model.h5', self.processor.tokenizer, self.processor.max_seq_length)
        self.next_word_suggestion = ''
        self.suggestion_start = None

    def on_space(self, event):
        '''
        Handles space key press event to perform autocorrect and show next word suggestions.
        '''

        self.text.insert(tk.INSERT, ' ')
        words = self.text.get('1.0', 'end-1c').split()
        current_index = self.text.index(tk.INSERT)
        line, column = current_index.split('.')
        new_index = f"{line}.{int(column) + 1}"
        self.history.append((words, new_index))

        if words:
            last_word = words[-1]
            print(last_word)
        
            # if last_word[-1] not in punctuation:
            corrected_word = self.autocorrect.correct_word(last_word)
            if corrected_word != last_word:
                # Capitalize if the word is at the beginning of a sentence
                if len(words) > 1 and words[-2][-1] in '.!?':
                    corrected_word = corrected_word[0].upper() + corrected_word[1:]
                self.replace_last_word(corrected_word)

            if last_word[-1] not in punctuation:
                # Predict next word
                predicted_sentence = self.predictor.predict_sequence(self.processor.tokenizer, ' '.join(words), num_words=1)
                predicted_word = predicted_sentence.split()[-1]
                # Handle special edge case
                if predicted_word == 'i':
                    predicted_word = predicted_word.upper()

                self.next_word_suggestion = predicted_word
                self.show_suggestion()

        return 'break'

    def show_suggestion(self):
        '''
        Displays the next word suggestion.
        '''

        if self.next_word_suggestion:
            current_index = self.text.index(tk.INSERT)
            self.text.insert(tk.INSERT, self.next_word_suggestion, 'suggestion')
            self.suggestion_start = current_index
            self.text.mark_set(tk.INSERT, current_index)

    def remove_suggestion(self):
        '''
        Removes the current word suggestion from the text editor.
        '''

        if self.suggestion_start:
            end_index = self.text.index(f"{self.suggestion_start} + {len(self.next_word_suggestion)} chars")
            self.text.delete(self.suggestion_start, end_index)
            self.suggestion_start = None
            self.next_word_suggestion = ''

    def on_tab(self, event):
        '''
        Handles the tab key press to accept the current word suggestion.
        '''

        if self.next_word_suggestion and self.suggestion_start:
            end_index = self.text.index(f"{self.suggestion_start} + {len(self.next_word_suggestion)} chars")
            self.text.delete(self.suggestion_start, end_index)
            self.text.insert(self.suggestion_start, self.next_word_suggestion)

            # Add it to history list so undo button/Ctrl-Z works
            words = self.text.get('1.0', 'end-1c').split()
            current_index = self.text.index(tk.INSERT)
            line, column = current_index.split('.')
            new_index = f"{line}.{int(column) + 1}"
            self.history.append((words, new_index))

            self.next_word_suggestion = ''
            self.suggestion_start = None
        return 'break'
    
    def on_key_press(self, event):
        '''
        Removes the suggested next word on any key press
        '''

        if self.next_word_suggestion:
            self.remove_suggestion()

    def undo(self, event=None):
        '''
        Undoes the last change made.
        '''

        if self.history:
            last_state, last_index = self.history.pop()
            
            last_text = ' '.join(last_state) + ' '
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', last_text)

            self.text.mark_set(tk.INSERT, last_index)
        return 'break'

    def replace_last_word(self, new_word):
        '''
        Replaces the last word in the text editor with the corrected word.
        '''

        content = self.text.get('1.0', 'end-1c')
        words = content.split()
        words[-1] = new_word
        new_content = ' '.join(words)
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', new_content)
        self.text.insert(tk.INSERT, ' ')

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Text Editor")
    editor = TextEditor(root)
    root.mainloop()