
import pandas as pd
from pymongo import MongoClient

# Read csv files
dfKaggleReviews = pd.read_csv('Hotel_Reviews.csv')

# drop columns
dropping_columns = {'Additional_Number_of_Scoring', 'Average_Score', 'Reviewer_Nationality',
                    'Total_Number_of_Reviews', 'Total_Number_of_Reviews_Reviewer_Has_Given', 'Tags', 'days_since_review', 'Review_Date'}

dfKaggleReviews.drop(dropping_columns, inplace=True, axis=1)

# Delete rows that dont have any comments
dfKaggleReviews = dfKaggleReviews.drop(dfKaggleReviews[(dfKaggleReviews['Review_Total_Negative_Word_Counts'] == 0) & (
    dfKaggleReviews['Review_Total_Positive_Word_Counts'] == 0)].index)

# Drop rows where the cijfer is between 4 and 6
dfKaggleReviews = dfKaggleReviews.drop(dfKaggleReviews[(
    dfKaggleReviews['Reviewer_Score'] > 4.0) & (dfKaggleReviews['Reviewer_Score'] < 6.0)].index)

# Merge positive/ negative reviews to one review
dfKaggleReviews['Review'] = dfKaggleReviews.loc[(dfKaggleReviews['Review_Total_Negative_Word_Counts'] != 0) & (
    dfKaggleReviews['Review_Total_Positive_Word_Counts'] != 0), 'Review'] = dfKaggleReviews['Positive_Review'] + dfKaggleReviews['Negative_Review']

# drop columns
dfKaggleReviews.drop({'Review_Total_Positive_Word_Counts', 'Review_Total_Negative_Word_Counts',
                      'Positive_Review', 'Negative_Review'}, inplace=True, axis=1)
# Cleaning
dfKaggleReviews['Review'] = dfKaggleReviews['Review'].str.replace(
    'No Negative', '')
dfKaggleReviews['Review'] = dfKaggleReviews['Review'].str.replace(
    'No Positive', '')

# Change order of the dataframe from kaggle
dfKaggleReviews = dfKaggleReviews[[
    'Hotel_Address', 'Hotel_Name', 'Reviewer_Score', 'Review', 'lat', 'lng']]

dfKaggleReviews.duplicated()
dfKaggleReviews = dfKaggleReviews.drop_duplicates(keep='first')


def labelCSVReviews(df, label, cijferHotel):
    df[label] = df.loc[df[cijferHotel] <= 4.0, label] = 0
    df.loc[df[cijferHotel] >= 6.0, label] = 1


# Add a label column, 0=negative, 1=positive drawing hotel
labelCSVReviews(dfKaggleReviews, 'label', 'Reviewer_Score')
dfKaggleReviews.info()

# Make pos and neg dataframes
dfPositive = dfKaggleReviews.loc[dfKaggleReviews["label"] == 1]
dfNegative = dfKaggleReviews.loc[dfKaggleReviews["label"] == 0]

# Filter only hotels from Paris
dfPositive = dfPositive[dfPositive["Hotel_Address"].str.contains(
    "Paris")]
dfNegative = dfNegative[dfNegative["Hotel_Address"].str.contains(
    "Paris")]

# Group hotel names and sum de labbels
dfPositiveGroup = dfPositive.groupby(
    "Hotel_Name", as_index=False)[["label"]].sum()

# Change label from 0 to 1 so i can sum it up
dfNegative["label"] = dfNegative["label"].replace([0], 1)
dfNegativeGroup = dfNegative.groupby(
    "Hotel_Name", as_index=False)[["label"]].sum()

# Filter dataframe only paris
dfKaggleReviews = dfKaggleReviews[dfKaggleReviews["Hotel_Address"].str.contains(
    "Paris")]

dfKaggleReviews.loc[dfKaggleReviews["Hotel_Name"] == "1K Hotel"]

# drop colums
dropping_columns = {'label', 'Review'}
dfKaggleReviews.drop(dropping_columns, inplace=True, axis=1)


# Group by hotel name
dfKaggleReviews = dfKaggleReviews.groupby(
    ["Hotel_Name", "Hotel_Address"], as_index=False).mean()

# Add new columns to kaggle dataframe
dfKaggleReviews["Positive"] = dfPositiveGroup["label"]
dfKaggleReviews["Negative"] = dfNegativeGroup["label"]

# Change Negative from float to int
dfKaggleReviews["Negative"] = dfKaggleReviews["Negative"].fillna(0)
dfKaggleReviews["Negative"] = dfKaggleReviews["Negative"].astype("int64")

# Reviewer score mean round 1 decimal
dfKaggleReviews["Reviewer_Score"] = dfKaggleReviews[[
    "Reviewer_Score"]].round(1)

dfKaggleReviews.loc[dfKaggleReviews["Negative"] > 0]
dfKaggleReviews.info()

# Database
client = MongoClient("localhost:27017")

# Collection name
db = client["hotel-reviews-database"]
db.hotelReviewsDashBoard.insert_many(dfKaggleReviews.to_dict('records'))

results = db.hotelReviewsDashBoard.find({})
source = list(results)
resultDf = pd.DataFrame(source)
resultDf.head()
