
import dash_table
import dash_core_components as dcc


def create_data_table(df):
    table = dash_table.DataTable(
        id='data_table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",
        sort_mode="native",
        page_size=20,
        row_selectable='multi',
        selected_rows=[],
        page_action="native",
        style_table={'height': '400px', 'overflowY': 'auto'},
        style_cell={
            'backgroundColor': '#093180',
            'color': 'white',
        },
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Hotel_Name']
        ],
        style_header={
            'backgroundColor': '#041840',
            'fontWeight': 'bold'
        }
    )
    return table


def rangeSliderPositive():
    rangeSlider = dcc.RangeSlider(
        id='range-slider-positive-reviews',
        marks={
            0: '0',
            100: '100',
            200: '200',
            300: '300',
            400: '400',
            500: '500',
            600: '600',
            700: '700',
            800: '800',
            900: '900',
            1000: '1000',
            1100: '1100',
            1200: '1200'
        },
        min=0,
        max=1200,
        step=1,
        value=[0, 1200],
        allowCross=False
    )

    return rangeSlider


def rangeSliderNegative():
    rangerSlider = dcc.RangeSlider(
        id="range-slider-negative",
        marks={
            0: '0',
            10: '10',
            20: '20',
            30: '30',
            40: '40',
            50: '50',
            60: '60',
            70: '70',
            80: '80',
            90: '90',
            100: '100',
        },
        min=0,
        max=100,
        step=1,
        value=[0, 100],
        allowCross=False)

    return rangerSlider


def interactiveMap(px, reviewsDf, token):
    px.set_mapbox_access_token(token)

    fig = px.scatter_mapbox(reviewsDf, lat="lat", lon="lng",
                            hover_name="Hotel_Name",
                            zoom=3, height=600, color="Reviewer_Score", color_continuous_scale='mrybm', hover_data=["Hotel_Name", "Hotel_Address", "Reviewer_Score", "Positive", "Negative"])
    fig.update_traces(marker_sizemin=5,
                      selector=dict(type='scattermapbox'), hovertemplate='%{text}', text=reviewsDf["text"], marker=dict(size=8))

    fig.update_layout(mapbox_style="dark")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox=dict(bearing=0,  pitch=0, zoom=11), clickmode='event+select')
    # fig.update_layout(mapbox_style="open-street-map")

    return fig


def interactiveMapTransparent(px, reviewsDf, token):
    px.set_mapbox_access_token(token)

    fig = px.scatter_mapbox(reviewsDf, lat="lat", lon="lng",
                            zoom=3, height=600, opacity=0)

    fig.update_layout(mapbox_style="dark")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox=dict(bearing=0,  pitch=0, zoom=11))

    return fig


def scatterPlot(px, dfFiltered):
    figScatter = px.scatter(dfFiltered, x="Negative",
                            y="Positive", color="Hotel_Name", height=600, title="Total positive and negative reviews")

    figScatter.update_layout(showlegend=False)
    figScatter.update_traces(marker=dict(size=12))

    return figScatter
