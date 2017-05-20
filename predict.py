import argparse

import requests
from lxml import etree
import pandas as pd
from sklearn.svm import SVC

import load_data as ld
from classifiers import (
    NBClassifier, SVCClassifier, AdaBoostClassifier
)


DEFAULT_CLASSIFIER = 'svc'

CLASSIFIER_MAPPING = {
    'nb': NBClassifier,
    'svc': SVCClassifier,
    'ada': AdaBoostClassifier,
}

NB_PARAMETERS = {}

SVC_PARAMETERS = {
    'kernel': 'linear',
    'gamma': 'auto'
}

ADABOOST_PARAMETERS = {
    'base_estimator': SVC(**SVC_PARAMETERS),
    'n_estimators': 100,
    'algorithm': 'SAMME'
}

CLASSIFIER_PARAMETERS = {
    'nb': NB_PARAMETERS,
    'svc': SVC_PARAMETERS,
    'ada': ADABOOST_PARAMETERS,
}

COLUMN_ORDER = [
    'age_diff', 'height_diff', 'weight_diff', 'hand_reach_diff',
     'leg_reach_diff', 'wins_diff', 'loses_diff', 'draws_diff', 'result'
]


def prepare_classifier(classifier, refresh):
    clf_to_train = trained_clf = None

    if refresh:
        ld.load_data()

    if classifier:
        if classifier in CLASSIFIER_MAPPING:
            clf_to_train = CLASSIFIER_MAPPING[classifier]
            parameters = CLASSIFIER_PARAMETERS[classifier]
        else:
            raise Exception(
                "'{}' is not valid classifier abreviation".format(classifier)
            )
    else:
        clf_to_train = CLASSIFIER_MAPPING[DEFAULT_CLASSIFIER]
        parameters = CLASSIFIER_PARAMETERS[DEFAULT_CLASSIFIER]
    dataset = pd.read_pickle(ld.DATA_SAVE_PATH)[COLUMN_ORDER]

    trained_clf = clf_to_train(dataset, parameters)
    return trained_clf


def run_scoring(classifier):
    print("Accuracy is {acc}".format(acc=classifier.accuracy))


def run_prediction(fighters, classifier):
    print("Predicting result for fight {fighter1} vs. {fighter2}".format(
        fighter1=fighters[0], fighter2=fighters[1]))


def main(fighters, classifier, refresh, score):
    fitted_classifier = prepare_classifier(classifier, refresh)

    if score:
        run_scoring(fitted_classifier)
    else:
        run_prediction(fitted_classifier)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--score', action="store_true")
    parser.add_argument('--fighters', nargs=2)
    parser.add_argument('--clf')
    parser.add_argument('--refresh', action="store_true")

    args = parser.parse_args()
    main(
        fighters=args.fighters,
        classifier=args.clf,
        refresh=args.refresh,
        score=args.score
    )
