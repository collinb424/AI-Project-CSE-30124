import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense

class TextProcessor:
    def __init__(self, filepath, max_length=1000):
        self.filepath = filepath
        self.max_length = max_length
        self.tokenizer = Tokenizer()
        self.max_seq_length = None

    def read_and_split_text(self):
        with open(self.filepath, 'r') as file:
            text = file.read()[:self.max_length]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def prepare_data(self):
        sentences = self.read_and_split_text()
        self.tokenizer.fit_on_texts(sentences)
        sequences = []
        for sentence in sentences:
            for i in range(1, len(sentence)):
                encoded = self.tokenizer.texts_to_sequences([sentence[:i]])[0]
                sequences.append(encoded)
        self.max_seq_length = max(len(seq) for seq in sequences)
        padded_sequences = pad_sequences(sequences, maxlen=self.max_seq_length, padding='pre')
        return padded_sequences

class NextWordPredictor:
    def __init__(self, vocab_size, seq_length):
        self.vocab_size = vocab_size
        self.seq_length = seq_length
        self.model = self._build_model()

    def _build_model(self):
        input_seq = Input(shape=(self.seq_length - 1,))
        embedding_layer = Embedding(self.vocab_size, 10)(input_seq)
        lstm_layer = LSTM(128)(embedding_layer)
        output_layer = Dense(self.vocab_size, activation='softmax')(lstm_layer)
        model = Model(inputs=input_seq, outputs=output_layer)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    def train(self, X, y, epochs=500):
        self.model.fit(X, y, epochs=epochs, verbose=1)

    def predict_sequence(self, tokenizer, seed_text, num_words=1):
        for _ in range(num_words):
            encoded = tokenizer.texts_to_sequences([seed_text])[0]
            encoded = pad_sequences([encoded], maxlen=self.seq_length - 1, padding='pre')
            pred_vector = self.model.predict(encoded)
            next_index = np.argmax(pred_vector)
            next_word = tokenizer.index_word[next_index]
            seed_text += " " + next_word
        return seed_text

# Usage
processor = TextProcessor('data/large.txt')
sequences = processor.prepare_data()
X, y = sequences[:, :-1], sequences[:, -1]
y = tf.keras.utils.to_categorical(y, num_classes=len(processor.tokenizer.word_index) + 1)

predictor = NextWordPredictor(len(processor.tokenizer.word_index) + 1, processor.max_seq_length)
predictor.train(X, y)

seed_text = "I like to relax by"
predicted_text = predictor.predict_sequence(processor.tokenizer, seed_text)
print("Predicted Text:", predicted_text)