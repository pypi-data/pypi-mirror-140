import pandas as pd
import pandas as pd
from feature_extractor import *
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import numpy as np
import sys
from sklearn.metrics import classification_report
from joblib import dump

from keras import models
from keras import layers
from sklearn.model_selection import train_test_split

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from sklearn.pipeline import Pipeline, FeatureUnion

def data_prepocessing(csv_filepath):
    """
    Implement load_data

    Arguements:
    csv_filepath -- the path directory of the csv_filepath in the workspace

    Returnes:
    X_train, X_test, y_train, y_test

    """

    df = pd.read_csv(csv_filepath)

    X = df['smiles'].values
    y = df['P1'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1000)

    vectorizer = CountVectorizer()

    vectorizer.fit(X_train)

    X_train = vectorizer.transform(X_train)

    X_test  = vectorizer.transform(X_test)

    return X_train, X_test, y_train, y_test


def build_model(X_train):
    """
    Implement build_model

    Arguements:

    Returnes:
    the builded model
    """

    input_dim = X_train.shape[1]  # Number of features

    model = Sequential()

    model.add(layers.Dense(10, input_dim=input_dim, activation='relu'))

    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam',  metrics=['accuracy'])
        
    return model

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """
    Implement evaluate model

    Retuerns:
    report the f1 score, precision and recall
    """

    # predict on test data
    # Y_pred = model.predict(X_test)

    loss, accuracy = model.evaluate(X_train, y_train, verbose=False)
    print("Training Accuracy: {:.4f}".format(accuracy))
    loss, accuracy = model.evaluate(X_test, y_test, verbose=False)
    print("Testing Accuracy:  {:.4f}".format(accuracy))


def save_model(model, model_filepath):
    """
    Implement save model

    Retuerns:
    export the model as a pickle file
    """
    model.save(model_filepath)

def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X_train, X_test, y_train, y_test  = data_prepocessing(database_filepath)
        # X_train, X_test, Y_train, Y_test = train_test_split(
        #     X, Y, test_size=0.2)

        print('Building model...')
        model = build_model(X_train)

        print('Training model...')
        model.fit(X_train, y_train, epochs=10, verbose=False, validation_data=(X_test, y_test), batch_size=10)

        print('Evaluating model...')
        evaluate_model(model, X_train, X_test, y_train, y_test)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the dataset '
              'as the first argument and the filepath of the pickle file to '
              'save the model to as the second argument. \n\nExample: python '
              'train_classifier.py ../data/dataset_single.csv classifier.pkl')


if __name__ == '__main__':
    main()





