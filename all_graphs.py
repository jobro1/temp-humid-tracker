import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objs as go
import os
from dotenv import load_dotenv


load_dotenv()

def get_db_engine():
    user = os.getenv("POSTGRESQL_USER")
    password = os.getenv("POSTGRESQL_PASSWORD")
    host = os.getenv("POSTGRESQL_SERVER")
    database = os.getenv("POSTGRESQL_DATABASE")
    port = os.getenv("POSTGRESQL_PORT", "5432")
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url)

def get_analytics_data():
    engine = get_db_engine()
    query = """
    SELECT timestamp, location, measurement_type, value, 
           voortschrijdend_gemiddelde_10min, daggemiddelde, is_incident
    FROM view_sensor_analytics
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
    ORDER BY timestamp ASC
    """
    df = pd.read_sql(query, engine)
    return df

def get_incident_report():
    engine = get_db_engine()
    query = """
    SELECT timestamp, value_at_incident, previous_value, incident_type
    FROM fact_incidents
    WHERE timestamp >= NOW() - INTERVAL '1 month'
    ORDER BY timestamp DESC
    """
    df = pd.read_sql(query, engine)
    return df

app = dash.Dash(__name__)

GRAPH_STYLE = {'border': '1px solid #ddd', 'padding': '15px', 'margin-bottom': '20px', 'border-radius': '8px', 'background-color': '#f9f9f9'}

app.layout = html.Div(style={'font-family': 'Segoe UI, Arial', 'padding': '30px', 'max-width': '1200px', 'margin': 'auto'}, children=[
    html.H1("IoT Data Mart: Sensor & Incident Rapportage", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.P("Deelopdracht 2.6: Aggregatie in een data mart (Week 6)", style={'textAlign': 'center', 'color': '#7f8c8d'}),

    dcc.Interval(id='interval-component', interval=20 * 1000, n_intervals=0),

    html.Div(style=GRAPH_STYLE, children=[
        html.H2("Rapport A: Tijd vs Temperatuur Meting (°C)"),
        dcc.Graph(id='graph-temp-raw'),
    ]),

    html.Div(style=GRAPH_STYLE, children=[
        html.H2("Rapport B: Tijd vs Luchtvochtigheid Meting (%)"),
        dcc.Graph(id='graph-hum-raw'),
    ]),

    html.Div(style=GRAPH_STYLE, children=[
        html.H2("Rapport C: Analyse Voortschrijdende Gemiddelden"),
        html.P("Vergelijking van 10 minuten vs Daggemiddelde om trends te spotten."),
        dcc.Graph(id='graph-moving-averages'),
    ]),

    html.Div(style=GRAPH_STYLE, children=[
        html.H2("Rapport D: Incidentenrapport (Afgelopen Maand)"),
        dash_table.DataTable(
            id='incident-table',
            columns=[{"name": i.replace('_', ' ').title(), "id": i} for i in
                     ['timestamp', 'value_at_incident', 'previous_value', 'incident_type']],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#ecf0f1', 'fontWeight': 'bold'},
            page_size=10
        )
    ]),
])

@app.callback(
    [Output('graph-temp-raw', 'figure'),
     Output('graph-hum-raw', 'figure'),
     Output('graph-moving-averages', 'figure'),
     Output('incident-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df_analytics = get_analytics_data()
    df_incidents = get_incident_report()

    temp_df = df_analytics[df_analytics['measurement_type'] == 'temperature']
    hum_df = df_analytics[df_analytics['measurement_type'] == 'humidity']

    def create_sensor_fig(df, title, y_label):
        fig = go.Figure()
        locations = df['location'].unique()

        for loc in locations:
            d = df[df['location'] == loc]

            fig.add_trace(go.Scatter(
                x=d['timestamp'],
                y=d['value'],
                name=f"Locatie: {loc}",
                mode='lines'
            ))

            incidents = d[d['is_incident'] == True]
            if not incidents.empty:
                fig.add_trace(go.Scatter(
                    x=incidents['timestamp'],
                    y=incidents['value'],
                    mode='markers',
                    name=f"Incident @ {loc}",
                    marker=dict(color='Red', size=12, symbol='x'),
                    showlegend=False  # Voorkomt dat de legenda te vol wordt
                ))

        fig.update_layout(
            height=400,
            margin={'t': 30},
            yaxis_title=y_label,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    fig_temp = create_sensor_fig(temp_df, "Temp", "°C")
    fig_hum = create_sensor_fig(hum_df, "Hum", "%")

    fig_averages = go.Figure()
    if not temp_df.empty:
        target_loc = temp_df['location'].unique()[0]
        loc_data = temp_df[temp_df['location'] == target_loc]

        fig_averages.add_trace(go.Scatter(x=loc_data['timestamp'], y=loc_data['value'],
                                          name="value Waarde", line=dict(color='rgba(46, 204, 113, 0.4)')))
        fig_averages.add_trace(go.Scatter(x=loc_data['timestamp'], y=loc_data['voortschrijdend_gemiddelde_10min'],
                                          name="10 Min Gemiddelde", line=dict(width=3, color='#2980b9')))
        fig_averages.add_trace(go.Scatter(x=loc_data['timestamp'], y=loc_data['daggemiddelde'],
                                          name="Daggemiddelde", line=dict(dash='dash', color='#c0392b')))

    fig_averages.update_layout(title=f"Trend Analyse: {target_loc if not temp_df.empty else 'Geen Data'}", height=400, template='plotly_white')

    return fig_temp, fig_hum, fig_averages, df_incidents.to_dict('records')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')