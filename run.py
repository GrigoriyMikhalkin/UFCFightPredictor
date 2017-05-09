#!bin/python3
import argparse

import requests
from lxml import etree

from classifiers import NBClassifier


COLUMN_ORDER = [
    'age_diff', 'height_diff', 'weight_diff', 'hand_reach_diff',
     'leg_reach_diff', 'wins_diff', 'loses_diff', 'draws_diff', 'result'
]


def main(fighter1, fighter2, classifier, refresh):
    print(
        "Predicting result for fight {fighter1} vs. {fighter2}".format(
            fighter1=fighter1, fighter2=fighter2
        )
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fighter1')
    parser.add_argument('fighter2')
    parser.add_argument('--clf')
    parser.add_argument('--refresh', action="store_true")

    args = parser.parse_args()
    main(
        fighter1=args.fighter1,
        fighter2=args.fighter2,
        classifier=args.clf,
        refresh=args.refresh
    )
