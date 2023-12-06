import re
from collections import defaultdict
from string import punctuation

class AutoCorrect:
    def __init__(self):
        self.words_count = defaultdict(int)
        self.total_words = 0
        self.cache = defaultdict(str)
        self.count_words()
    
    def count_words(self):
        '''
        Reads words from a file and counts their occurrences. This data is used for calculating word 
        probabilities later.
        '''

        with open('big.txt') as file:
            words = self.get_words(file.read())
        self.total_words = len(words)
        for word in words:
            self.words_count[word] += 1

    def get_words(self, text): 
        '''
        Extracts words from a given text string, converting them to lowercase.
        '''

        return re.findall(r'\w+', text.lower())
    
    def word_probability(self, word): 
        '''
        Calculates the probability of a word based on its frequency in the text.
        '''

        return self.words_count[word] / self.total_words

    def correct_word(self, word): 
        '''
        Attempts to find the most probable correct form of a given word.
        It utilizes caching for efficiency.
        '''

        # Handle punctuation at the end of the word
        end = ''
        if word[-1] in punctuation:
            end = word[-1]
            word = word[:-1]
        if word.lower() in self.words_count:
            return word if not end else word + end
        if word.lower() in self.cache:
            return self.cache[word] if not end else self.cache[word] + end
        
        max_probability = 0
        corrected_word = word
        for possibility in self.possibilities(word):
            probability = self.word_probability(possibility)
            if probability > max_probability:
                max_probability = probability
                corrected_word = possibility

        self.cache[word] = corrected_word
        return corrected_word if not end else corrected_word + end 

    def possibilities(self, word): 
        '''
        Generates a set of possible corrections for a given word, considering
        validated words, one-edit and two-edit distance words.
        '''

        valid_words = self.validate_word([word])
        if valid_words:
            return valid_words

        one_edit_words = self.validate_word(self.one_edit(word))
        if one_edit_words:
            return one_edit_words

        two_edit_words = self.validate_word(self.two_edits(word))
        return two_edit_words if two_edit_words else [word]  


    def validate_word(self, words): 
        '''
        Filters a list of words, keeping only those that exist in the known words dictionary.
        '''
        exist = set()
        for word in words:
            if word in self.words_count:
                exist.add(word)
        return exist

    def one_edit(self, word):
        '''
        Generates all possible words that are one edit distance away from the given word.
        Edits include deletion, transposition, replacement, and insertion of characters.
        '''

        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        one_edit_words = set()

        # Create all possible splits of the word
        splits = []
        for i in range(len(word) + 1):
            splits.append((word[:i], word[i:]))

        # Remove one character
        for left, right in splits:
            if right:
                one_edit_words.add(left + right[1:])

        # Swap two adjacent characters
        for left, right in splits:
            if len(right) > 1:
                one_edit_words.add(left + right[1] + right[0] + right[2:])

        # Change one character to another
        for left, right in splits:
            if right:
                for char in alphabet:
                    one_edit_words.add(left + char + right[1:])

        # Add one character
        for left, right in splits:
            for char in alphabet:
                one_edit_words.add(left + char + right)

        return one_edit_words

    def two_edits(self, word): 
        '''
        Creates words that are two edits away from the given word by applying one-edit operations twice.
        '''

        two_edit_words = set()
        for e1 in self.one_edit(word):
            for e2 in self.one_edit(e1):
                two_edit_words.add(e2)
        return two_edit_words


def main():
    a = AutoCorrect()
    print(a.correct_word('artifcil'))
    print(a.correct_word('incorect'))
    print(a.correct_word('teh'))
    print(a.correct_word('Heey'))
    print(a.correct_word('Heey?'))

if __name__ == "__main__":
    main()