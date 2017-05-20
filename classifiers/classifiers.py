from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split


class BaseClassifier:
    def __init__(self, dataset, params):
        """
        :param dataset: pandas.DateFrame
        """
        self.clf = self.CLASSIFIER(**params)
        self.accuracy = None
        self.fit_classifier(dataset)

    def fit_classifier(self, dataset):
        """
        :param dataset: pandas.DateFrame
        """
        data = []
        labels = []

        for ind, row in dataset.iterrows():
            row_list = row.tolist()
            label = row_list.pop()
            data.append(row_list)
            labels.append(label)

        X_train, X_test, y_train, y_test = train_test_split(
            data, labels, test_size=0.2, random_state=0
        )

        self.clf.fit(X_train, y_train)
        self.accuracy = self.clf.score(X_test, y_test)

    def predict(self, data):
        """
        :param data: list
        """
        return self.clf.predict(data)


class NBClassifier(BaseClassifier):
    """
    Naive Bayes classifier
    """
    CLASSIFIER = GaussianNB


class SVCClassifier(BaseClassifier):
    """
    SVC Classifier
    """
    CLASSIFIER = SVC


class AdaBoostClassifier(BaseClassifier):
    """
    AdaBoost Classifier
    """
    CLASSIFIER = AdaBoostClassifier
