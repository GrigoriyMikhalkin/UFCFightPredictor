# Command line UFC fight predictor

## How to use

First of all, you need to clone repository:

    git clone
    cd UFCFightPredictor

Make sure, you have `python 3.2`, or later, installed. Also, install dependencies(i would recommend to set `virtualenv` before that step):

    pip install -r requirements.txt

Then, to predict fight, execute command with following syntax:

    python predict.py [--clf classifier abr.] [--refresh] 'fighter1_name' 'fighter2_name'

Option `--clf` specifies classifier(default is SVM Classifier with linear kernel), `--refresh` -- makes predictor to refresh train dataset(it will take ~10 mins). Both fighters should be current UFC fighters and, their name, should be spelled as on UFC.com. Command will return prediction for `fighter1`, either 'win' or 'lose'.

Available classifiers:

  - Gaussian Naive Bayes [nb]
  - SVC (svc)
  - AdaBoost (ada)

## How it works

When command executed it makes, basically, 2 things.

First step is -- it checks if training dataset exists. If not, loads fighters stats from UFC.com and fight histories from Sherdog.com. Then merges this data into training dataset and store it in data folder.

Second step -- trains chosen classifier(default is Gaussian Naive Bayes). After classifier is train, it lloks for given fighters stats on UFC.com, calculates features from that stats and makes prediction.
