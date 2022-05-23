from extract_training_data import FeatureExtractor
import sys
import numpy as np
import tensorflow as tf

def build_model(word_types, pos_types, outputs):
    # TODO: Write this function for part 3
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Embedding(word_types, 32, input_length=6)) #word_type:word_len, input_length=6(3 pos with 3 word)
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(units=100, activation="relu"))
    model.add(tf.keras.layers.Dense(units=10, activation="relu"))
    model.add(tf.keras.layers.Dense(units=outputs, activation='softmax'))
    model.compile(tf.keras.optimizers.Adam(lr=0.01), loss="categorical_crossentropy")
    return model


if __name__ == "__main__":

    WORD_VOCAB_FILE = 'data/words.vocab'
    POS_VOCAB_FILE = 'data/pos.vocab'

    try:
        word_vocab_f = open(WORD_VOCAB_FILE,'r')
        pos_vocab_f = open(POS_VOCAB_FILE,'r') 
    except FileNotFoundError:
        print("Could not find vocabulary files {} and {}".format(WORD_VOCAB_FILE, POS_VOCAB_FILE))
        sys.exit(1) 

    extractor = FeatureExtractor(word_vocab_f, pos_vocab_f)
    print("Compiling model.")
    model = build_model(len(extractor.word_vocab), len(extractor.pos_vocab), len(extractor.output_labels))
    inputs = np.load('data/input_train.npy')
    outputs = np.load('data/target_train.npy')
    print("Done loading data.")
   
    # Now train the model
    model.fit(inputs, outputs, epochs=5, batch_size=100)
    
    model.save('data/model.h5')