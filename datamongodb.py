
import pandas as pd
from pymongo import MongoClient
import re
import numpy as np
import time

# Read csv files
dfKaggleReviews = pd.read_csv('Hotel_Reviews.csv')

dfKaggleReviews = dfKaggleReviews.drop(dfKaggleReviews[(dfKaggleReviews['Review_Total_Negative_Word_Counts'] == 0) & (
    dfKaggleReviews['Review_Total_Positive_Word_Counts'] == 0)].index)

# drop columns
dropping_columns = {'Hotel_Address', 'Additional_Number_of_Scoring', 'Average_Score', 'Reviewer_Nationality',
                    'Total_Number_of_Reviews', 'Total_Number_of_Reviews_Reviewer_Has_Given', 'Tags', 'days_since_review', 'Review_Date', 'Review_Total_Positive_Word_Counts', 'Review_Total_Negative_Word_Counts', 'lat', 'lng'}

dfKaggleReviews.drop(dropping_columns, inplace=True, axis=1)

dfKaggleReviews2 = dfKaggleReviews.head(1000)


def split_review(target_df):
    df = pd.DataFrame()

    for index, row in target_df.iterrows():
        df = df.append([[row.Hotel_Name, row.Reviewer_Score, row.Positive_Review,
                         1]], ignore_index=True)
        df = df.append([[row.Hotel_Name, row.Reviewer_Score, row.Negative_Review,
                         0]], ignore_index=True)
        # df.columns = cols

    return df


start_time = time.time()
dfKaggleReviews = split_review(dfKaggleReviews2)
print(time.time() - start_time, ' Seconds')

dfKaggleReviews.columns = ['Hotel_Name', 'Reviewer_Score', 'Review', 'label']


def clean_review(text):
    if text is not None and text is not '':
        # Removes special tekens/ spaties en zet alles naar lower case
        text = re.sub(r'[^\w\s]', '', str(text).lower().strip())

    return text


dfKaggleReviews['Review'] = dfKaggleReviews['Review'].apply(
    clean_review)


# Cleaning
dfKaggleReviews['Review'] = dfKaggleReviews['Review'].str.replace(
    'no negative', '')
dfKaggleReviews['Review'] = dfKaggleReviews['Review'].str.replace(
    'no positive', '')


dfKaggleReviews.duplicated()
dfKaggleReviews = dfKaggleReviews.drop_duplicates(keep='first')

dfKaggleReviews['Review'].replace('', np.nan, inplace=True)
dfKaggleReviews.dropna(subset=['Review'], inplace=True)

dfKaggleReviews.info()

# Database
client = MongoClient("localhost:27017")

# Collection name
db = client["hotel-reviews-database"]
db.clean_reviews.insert_many(dfKaggleReviews.to_dict('records'))

results = db.hotelReviews.find({})
source = list(results)
resultDf = pd.DataFrame(source)
resultDf.head()
