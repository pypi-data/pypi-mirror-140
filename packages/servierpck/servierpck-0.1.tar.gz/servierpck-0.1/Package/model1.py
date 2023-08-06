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
    X, y

    """

    df = pd.read_csv(csv_filepath)
    
    df['extracted features'] = df.apply(lambda row : feature_extractor.fingerprint_features(row['smiles']), axis = 1)

    df['ExplicitBitVect_to_array'] = df.apply(lambda row : np.frombuffer(row['extracted features'].ToBitString().encode(), 'u1') - ord('0'), axis = 1)

    X = df['ExplicitBitVect_to_array']

    y = df['P1']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    X_train = np.stack(X_train.values)

    X_test = np.stack(X_test.values)

    return X_train, X_test, y_train, y_test


def build_model():
    """
    Implement build_model

    Arguements:

    Returnes:
    the builded model
    """

    model = models.Sequential()

    model.add(layers.Dense(512, activation='relu', input_shape=(2048*1,)))

    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    return model


def evaluate_model(model, X_test, Y_test):
    """
    Implement evaluate model

    Retuerns:
    report the f1 score, precision and recall
    """

    # predict on test data
    # Y_pred = model.predict(X_test)

    test_loss, test_acc = model.evaluate(X_test, Y_test)
    print('test_acc:', test_acc)

    # for test, prediction in zip(Y_test.T, Y_pred.T):
    #     print('Classification report for ')
    #     print(classification_report(test, prediction))

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
        X_train, X_test, Y_train, Y_test  = data_prepocessing(database_filepath)
        # X_train, X_test, Y_train, Y_test = train_test_split(
        #     X, Y, test_size=0.2)

        print('Building model...')
        model = build_model()

        print('Training model...')
        model.fit(X_train, Y_train, epochs=10, batch_size=128)

        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test)

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
