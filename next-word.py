import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

class TextProcessor:
    def __init__(self, filepath, max_length=17400):
        self.filepath = filepath
        self.max_length = max_length
        self.tokenizer = Tokenizer()
        self.max_seq_length = None

    def read_and_split_text(self):
        '''
        Reads text from a file, truncating to max_length, and splits into sentences.
        '''

        with open(self.filepath, 'r') as file:
            text = file.read()[:self.max_length]
        sentences = re.split(r'(?<=[.!?])\s+', text) # Splits text into sentences
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def prepare_data(self):
        '''
        Prepares data for model training, tokenizing sentences and creating padded sequences.
        '''

        sentences = self.read_and_split_text()
        self.tokenizer.fit_on_texts(sentences)
        sequences = self.create_sequences(sentences)

        # Padding sequences to ensure uniform length
        padded_sequences = pad_sequences(sequences, maxlen=self.max_seq_length, padding='pre')
        return padded_sequences
    

    def create_sequences(self, sentences):
        '''
        Creates sequences of tokens for each sentence in the text.
        '''

        sequences = []
        for sentence in sentences:
            # Generates token sequences for each possible prefix of the sentence
            for i in range(1, len(sentence)):
                encoded = self.tokenizer.texts_to_sequences([sentence[:i]])[0]
                sequences.append(encoded)
        self.max_seq_length = max(len(seq) for seq in sequences)
        return sequences



class NextWordPredictor:
    def __init__(self, vocab_size, seq_length, model=None):
        self.vocab_size = vocab_size
        self.seq_length = seq_length
        self.model = model if model else self.build_model()

    def build_model(self):
        '''
        Builds an LSTM model for next-word prediction.
        '''

        # Follow the typical steps for setting up and training an LSTM model
        input_seq = Input(shape=(self.seq_length - 1,))
        embedding_layer = Embedding(self.vocab_size, 10)(input_seq)
        lstm_layer = LSTM(128)(embedding_layer)
        output_layer = Dense(self.vocab_size, activation='softmax')(lstm_layer)
        model = Model(inputs=input_seq, outputs=output_layer)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    def train(self, X, y, epochs=59):
        '''
        Trains the model on the provided data for the specified number of epochs.
        '''

        self.model.fit(X, y, epochs=epochs, verbose=1)

    def predict_sequence(self, tokenizer, seed_text, num_words=1):
        '''
        Predicts the next 'num_words' words in the given 'seed_text'.
        '''

        for _ in range(num_words):
            encoded = tokenizer.texts_to_sequences([seed_text])[0]
            if not encoded:
                # If the seed text cannot be encoded, return it as is.
                return seed_text
            encoded = pad_sequences([encoded], maxlen=self.seq_length - 1, padding='pre')
            pred_vector = self.model.predict(encoded)
            next_index = np.argmax(pred_vector)
            next_word = tokenizer.index_word[next_index]
            seed_text += " " + next_word
        return seed_text
    
    def save(self, filepath):
        '''
        Saves the model to the specified filepath.
        '''

        self.model.save(filepath)

    @classmethod
    def load(cls, model_path, tokenizer, seq_length):
        '''
        Loads a model from the specified path.
        '''

        model = load_model(model_path)
        return cls(len(tokenizer.word_index) + 1, seq_length, model=model)





def train_model(X, y, processor):
    '''
    Trains a new NextWordPredictor model using the provided data.
    '''

    predictor = NextWordPredictor(len(processor.tokenizer.word_index) + 1, processor.max_seq_length)
    predictor.train(X, y)
    predictor.save('my_model.h5')
    return predictor

def load_or_train_model(X, y, processor):
    '''
    Loads an existing model or trains a new one if no model is found.
    '''

    if os.path.exists('my_model.h5'):
        print("Loading existing model...")
        loaded_model = load_model('my_model.h5')
        return NextWordPredictor(len(processor.tokenizer.word_index) + 1, processor.max_seq_length, model=loaded_model)
    else:
        print("Training new model...")
        return train_model(X, y, processor)

processor = TextProcessor('data/sentences.txt')
sequences = processor.prepare_data()
X, y = sequences[:, :-1], sequences[:, -1]
y = tf.keras.utils.to_categorical(y, num_classes=len(processor.tokenizer.word_index) + 1)
predictor = load_or_train_model(X, y, processor)