import re
from collections import defaultdict

class AutoCorrect:
    def __init__(self):
        self.words_count = defaultdict(int)
        self.total_words = 0
        self.cache = defaultdict(str)
        self.count_words()
    
    def count_words(self):
        words = self.get_words(open('data/large.txt').read())
        self.total_words = len(words)
        for word in words:
            self.words_count[word] += 1

    def get_words(self, text): 
        return re.findall(r'\w+', text.lower())
    
    def word_probability(self, word): 
        "Probability of `word`."
        return self.words_count[word] / self.total_words

    def correct_word(self, word): 
        "Most probable spelling correction for word."
        if word in self.cache:
            return self.cache[word]
        
        max_probability = 0
        corrected_word = word
        for possibility in self.possibilities(word):
            probability = self.word_probability(possibility)
            if probability > max_probability:
                max_probability = probability
                corrected_word = possibility

        self.cache[word] = corrected_word
        return corrected_word   

    def possibilities(self, word): 
        "Generate possible spelling corrections for word."
        return (self.validate_word([word]) or self.validate_word(self.one_edit(word)) 
                or self.validate_word(self.two_edits(word)) or [word])

    def validate_word(self, words): 
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.words_count)

    def one_edit(self, word):
        "All edits that are one edit away from `word`."
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        one_edit_words = set()

        # Create all possible splits of the word.
        splits = []
        for i in range(len(word) + 1):
            splits.append((word[:i], word[i:]))

        # Delete operation: remove one character.
        for left, right in splits:
            if right:
                one_edit_words.add(left + right[1:])

        # Transpose operation: swap two adjacent characters.
        for left, right in splits:
            if len(right) > 1:
                one_edit_words.add(left + right[1] + right[0] + right[2:])

        # Replace operation: change one character to another.
        for left, right in splits:
            if right:
                for char in alphabet:
                    one_edit_words.add(left + char + right[1:])

        # Insert operation: add one character.
        for left, right in splits:
            for char in alphabet:
                one_edit_words.add(left + char + right)

        return one_edit_words

    def two_edits(self, word): 
        "All edits that are two edits away from `word`."
        one_edit_away = self.one_edit(word)
        
        for first_edit in one_edit_away:
            for second_edit in self.one_edit(first_edit):
                yield second_edit



def main():
    a = AutoCorrect()
    print(a.correct_word('artifcil'))
    print(a.correct_word('incorect'))
    print(a.correct_word('teh'))


if __name__ == "__main__":
    main()