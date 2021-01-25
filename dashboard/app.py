import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import numpy as np
from pymongo import MongoClient
from dash.dependencies import Output, Input
from layout_util import create_data_table, rangeSliderPositive, rangeSliderNegative, interactiveMap, scatterPlot, interactiveMapTransparent

token = open("mapbox_token.txt").read()

client = MongoClient("localhost:27017")
db = client["hotel-reviews-database"]

app = dash.Dash(
    __name__, assets_external_path='http://assets/dashstylesheet.css')

tab_selected_style = {
    'backgroundColor': '#061e44',
    'color': 'white',
    'borderLeft': '1px solid #ffffff',
    'borderRight': '1px solid #ffffff',
    'padding': '6px'
}

data_table_hotels = db.hotelReviewsDashBoard.find({})
sourceDataTable = list(data_table_hotels)
dfHotelsDataTable = pd.DataFrame(sourceDataTable)
dfHotelsDataTable = dfHotelsDataTable.drop(columns=["_id", "lat", "lng"])
print(dfHotelsDataTable.info())

app.layout = html.Div(id="OuterOuterDiv", children=[
    html.Div(id="banner", children=[html.Img(src="/assets/shield.png", id="shield"),
                                    html.H1(
        "Dashboard"), html.H5("Jamal Aartsen", id="name")]),

    dcc.Tabs(id="tabs", children=[
        dcc.Tab(id="tab_layout_grafiek", label="Interactive map", selected_style=tab_selected_style, children=[
            html.Div(children=[
                html.Div(className="inline_block_layout",
                         children=[dcc.Graph(id="graph-hotel-reviews")]),
                html.Div(className="background",
                         children=[html.H2("Hotels in Paris", id="h2Title"),
                                   html.Div(children=[
                                       html.H3("Number of positive reviews",
                                               id="h3TitlePos", className="h3Title"),
                                       html.Div(children=[html.P(id="numberOnePos", className="numberOne"),
                                                          html.P(id="numberTwoPos", className="numberTwo")]),
                                       rangeSliderPositive()
                                   ]),
                                   html.Div(children=[
                                       html.H3("Number of negative reviews",
                                               id="h3TitleNegative", className="h3Title"),
                                       html.Div(children=[
                                           html.P(id="numberOneNegative",
                                                  className="numberOne"),
                                           html.P(id="numberTwoNegative", className="numberTwo")]),
                                       rangeSliderNegative(),
                                       html.Div(id="custum_data_div", children=[
                                           html.H3("Hotel Information: ",
                                                   id="hotel_information"),
                                           html.Div(id="titleHotel"),
                                           html.Div(
                                               id="adress", className="click_data"),
                                           html.Div(
                                               id="score", className="click_data"),
                                           html.Div(id="positiveReview",
                                                    className="click_data"),
                                           html.Div(id="negativeReview",
                                                    className="click_data")
                                       ])

                                   ])
                                   ])
            ], id='divOuterContainer')]),
        dcc.Tab(id="tab_layout_data_table", label="Data Table", selected_style=tab_selected_style, children=[
            html.Div([
                html.Div(id="background_scatterplot",
                         children=[dcc.Graph(id="scatter_plot")]),
                html.Div(id="background_datatable",
                         children=[html.H1("Hotel scores", id="hotel_scores_title"), create_data_table(dfHotelsDataTable)])
            ], id="divOuterContainerTable")
        ])], colors={
        "primary": "white",
        "background": "#082255"
    })

], style={'overflow': 'scroll'})


@ app.callback(dash.dependencies.Output("graph-hotel-reviews", "figure"),
               dash.dependencies.Output("numberOnePos", "children"),
               dash.dependencies.Output("numberTwoPos", "children"),
               dash.dependencies.Output("numberOneNegative", "children"),
               dash.dependencies.Output("numberTwoNegative", "children"),
               dash.dependencies.Output("titleHotel", "children"),
               dash.dependencies.Output("adress", "children"),
               dash.dependencies.Output("score", "children"),
               dash.dependencies.Output("positiveReview", "children"),
               dash.dependencies.Output("negativeReview", "children"),
               [dash.dependencies.Input(
                   "range-slider-positive-reviews", "value"), dash.dependencies.Input("range-slider-negative", "value"), dash.dependencies.Input("graph-hotel-reviews", "clickData")]
               )
def update_fig(value_positive, value_negative, click_data_marker):

    results = db.hotelReviewsDashBoard.find({"$and": [{"Positive": {"$gte": value_positive[0], "$lt": value_positive[1]}}, {
                                            "Negative": {"$gte": value_negative[0], "$lt": value_negative[1]}}]})

    source = list(results)
    reviewsDf = pd.DataFrame(source)
    print(reviewsDf.info())

    if click_data_marker is None:
        print("No data")
        click_data_name = ""
        click_data_adress = ""
        click_data_score = ""
        click_data_positive = ""
        click_data_negative = ""

    else:
        click_data_name = click_data_marker['points'][0]['customdata'][0]
        click_data_adress = "Adress: " + \
            click_data_marker['points'][0]['customdata'][1]
        click_data_score = "Score: " + \
            str(click_data_marker['points'][0]['customdata'][2])
        click_data_positive = "Total positive reviews: " + \
            str(click_data_marker['points'][0]['customdata'][3])
        click_data_negative = "Total negative reviews: " + \
            str(click_data_marker['points'][0]['customdata'][4])

    emptyDataframe = pd.DataFrame(
        columns=["Hotel_Name", "Reviewer_Score", "lat", "lng", "Positive", "Negative"])
    emptyDataframe = emptyDataframe.append(
        {"Hotel_Name": "ExampleHotel", "Reviewer_Score": 8.0, "lat": 48.864716, "lng": 2.349014, "Positive": 200, "Negative": 50}, ignore_index=True)

    if reviewsDf.empty:
        interactiveMapFig = interactiveMapTransparent(
            px, emptyDataframe, token)
    else:
        reviewsDf["text"] = "<b>" + reviewsDf["Hotel_Name"] + "</b><br><br>" + "Adress: " + reviewsDf["Hotel_Address"] + "<br>Reviewer score: " + reviewsDf['Reviewer_Score'].astype(
            str) + "<br>Total positive reviews: " + reviewsDf['Positive'].astype(str) + "<br>Total negative reviews: " + reviewsDf['Negative'].astype(str)
        interactiveMapFig = interactiveMap(px, reviewsDf, token)

    return interactiveMapFig, value_positive[0], value_positive[1], value_negative[0], value_negative[1], click_data_name, click_data_adress, click_data_score, click_data_positive, click_data_negative


@ app.callback(dash.dependencies.Output("scatter_plot", "figure"), [dash.dependencies.Input("data_table", "selected_rows")])
def update_datatable(selected_rows):
    if len(selected_rows) == 0:
        dfFiltered = dfHotelsDataTable[dfHotelsDataTable.index.isin([50])]
    else:
        dfFiltered = dfHotelsDataTable[dfHotelsDataTable.index.isin(
            selected_rows)]
        print(dfFiltered.head())

    return scatterPlot(px, dfFiltered)


server = app.server
if __name__ == "__main__":
    app.run_server(debug=True)
