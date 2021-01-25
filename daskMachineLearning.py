from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
import dask.dataframe as ddf
import joblib
import dask.distributed
from distributed import Client, LocalCluster
from pymongo import MongoClient
import pandas as pd
import time
from dask_ml.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from dask_ml.model_selection import train_test_split
from sklearn.utils import shuffle
import dask.bag as db

# Database
client = MongoClient("localhost:27017")

# Collection name
db = client["hotel-reviews-database"]

# Get result and put it in a dataframe = positive reviews
resultsPos = db.hotelReviews.find({'label': 1}).limit(20000)
sourcePos = list(resultsPos)
resultDfPos = pd.DataFrame(sourcePos)
resultDfPos.head()
resultDfPos.info()

# Get result and put it in a dataframe = negative reviews
resultsNeg = db.hotelReviews.find({'label': 0}).limit(20000)
sourceNeg = list(resultsNeg)
resultDfNeg = pd.DataFrame(sourceNeg)
resultDfNeg.head()
resultDfNeg.info()

# Merge de positieve en negatieve reviews bij elkaar.
resultDf = pd.concat([resultDfPos, resultDfNeg])

# Reindex dataframe
resultDf = shuffle(resultDf)
resultDf.reset_index(drop=True)

# Transform dataframe into a dask dataframe/ delete id row
dfDask = ddf.from_pandas(resultDf, npartitions=10)
dfDask = dfDask.drop('_id', axis=1)
dfDask.head()
dfDask.compute()

cluster = LocalCluster()
c = Client(cluster)


vocal = joblib.load('vocal.pk1')

cv = CountVectorizer()

# split dataset in features and target variable, X is hoofdletter
X = dfDask['Review'].values
y = dfDask['label'].values

X = X.compute_chunk_sizes()
y = y.compute_chunk_sizes()

# Split data in train set and test set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

X_train = db.from_sequence(X_train, npartitions=2)
X_test = db.from_sequence(X_test, npartitions=2)

cv.fit(X_train)
cv.fit(X_test)

X_traincv = cv.transform(X_train)
X_testcv = cv.transform(X_test)


# Classifier instances
svmClf = SVC()
