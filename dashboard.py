# import dash
# from dash.dependencies import Output, Input
# from dash import dcc, html
# import plotly.graph_objs as go
# import pandas as pd

# # File path to the CSV data file
# DATA_FILE = 'sensor_data.csv'

# # Initialize the Dash app
# app = dash.Dash(__name__)
# app.title = "Sensor Data Dashboard"

# # Define the layout of the dashboard
# app.layout = html.Div([
#     html.H1("Real-Time Sensor Data Dashboard"),
#     dcc.Graph(id='live-chart'),
#     dcc.Interval(
#         id='interval-component',
#         interval=5*1000,  # Refresh every 5 seconds
#         n_intervals=0
#     ),
#     html.Div(id='last-update', style={'marginTop': 20, 'fontWeight': 'bold'})
# ])

# # Callback to update the graph
# @app.callback(
#     [Output('live-chart', 'figure'),
#      Output('last-update', 'children')],
#     [Input('interval-component', 'n_intervals')]
# )
# def update_graph_live(n):
#     try:
#         # Read the CSV file
#         df = pd.read_csv(DATA_FILE)
#     except Exception as e:
#         return go.Figure(), f"Error reading data: {e}"

#     # Parse the timestamp column to datetime
#     df['timestamp'] = pd.to_datetime(df['timestamp'])

#     # Create traces for temperature and pressure
#     trace_temp = go.Scatter(
#         x=df['timestamp'], y=df['temperature'],
#         mode='lines+markers',
#         name='Temperature',
#         marker=dict(color='blue')
#     )

#     trace_pressure = go.Scatter(
#         x=df['timestamp'], y=df['pressure'],
#         mode='lines+markers',
#         name='Pressure',
#         marker=dict(color='green')
#     )

#     # Highlight anomalies
#     anomaly_data = df[df['anomaly'] == "Yes"]
#     trace_anomaly = go.Scatter(
#         x=anomaly_data['timestamp'], y=anomaly_data['temperature'],
#         mode='markers',
#         name='Anomaly (Temperature)',
#         marker=dict(color='red', size=12, symbol='x')
#     )

#     layout = go.Layout(
#         title='Sensor Readings Over Time',
#         xaxis=dict(title='Timestamp'),
#         yaxis=dict(title='Value'),
#         legend=dict(orientation="h"),
#         margin=dict(l=40, r=40, t=40, b=40)
#     )

#     fig = go.Figure(data=[trace_temp, trace_pressure, trace_anomaly], layout=layout)
#     last_update = f"Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     return fig, last_update

# if __name__ == '__main__':
#     app.run(debug=True, port=8050)

import dash
from dash.dependencies import Output, Input
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

#DATA_FILE = 'sensor_data.csv'
DATA_FILE = '/data/sensor_data.csv'

app = dash.Dash(__name__)
app.title = "Sensor Data Dashboard"

app.layout = html.Div([
    html.H1("Real‑Time Sensor Data Dashboard"),
    dcc.Graph(id='live-chart'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Refresh every 5 seconds
        n_intervals=0
    ),
    html.Div(id='last-update', style={'marginTop': 20, 'fontWeight': 'bold'})
])

@app.callback(
    [Output('live-chart', 'figure'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    try:
        # 1. Read CSV, coerce types
        df = pd.read_csv(
            DATA_FILE,
            dtype={
                'rule_anomaly': str,
                'ml_anomaly': str,
                'failure': 'Int64',          # pandas nullable int
                'failure_prob': float         # force to float
            },
            parse_dates=['timestamp'],        # parse timestamp right away
            infer_datetime_format=True
        )
        # 2. Ensure failure_prob exists
        if 'failure_prob' not in df.columns:
            df['failure_prob'] = 0.0
        else:
            df['failure_prob'] = pd.to_numeric(df['failure_prob'], errors='coerce').fillna(0.0)

        # 3. Base traces
        trace_temp = go.Scatter(
            x=df['timestamp'], y=df['temperature'],
            mode='lines+markers', name='Temperature'
        )
        trace_pressure = go.Scatter(
            x=df['timestamp'], y=df['pressure'],
            mode='lines+markers', name='Pressure'
        )

        # 4. Rule anomalies
        df_rule = df[df['rule_anomaly'] == "Yes"]
        trace_rule = go.Scatter(
            x=df_rule['timestamp'], y=df_rule['temperature'],
            mode='markers', name='Rule Anomaly',
            marker=dict(color='red', symbol='x', size=10)
        )

        # 5. ML anomalies
        df_ml = df[df['ml_anomaly'] == "Yes"]
        trace_ml = go.Scatter(
            x=df_ml['timestamp'], y=df_ml['temperature'],
            mode='markers', name='ML Anomaly',
            marker=dict(color='orange', symbol='triangle-up', size=10)
        )

        # 6. Failure risk trace
        trace_fail = go.Scatter(
            x=df['timestamp'], y=df['failure_prob'],
            mode='lines+markers', name='Failure Risk',
            marker=dict(color='purple', symbol='star', size=8),
            yaxis='y2'
        )

        # 7. Build the figure with two y‑axes
        fig = go.Figure(
            data=[trace_temp, trace_pressure, trace_rule, trace_ml, trace_fail],
            layout=go.Layout(
                title='Sensor Readings, Anomalies & Failure Risk',
                xaxis=dict(title='Timestamp'),
                yaxis=dict(title='Temperature / Pressure'),
                yaxis2=dict(
                    title='Failure Probability',
                    overlaying='y',
                    side='right',
                    range=[0, 1]
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=40, r=40, t=40, b=40)
            )
        )

        last_update = f"Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return fig, last_update

    except Exception as e:
        # If anything at all goes wrong, log it and return an empty figure
        print("🚨 Dashboard update error:", e)
        return go.Figure(), f"Error: {e}"

if __name__ == '__main__':
    # app.run(debug=True, port=8050)
    app.run(host='0.0.0.0', port=8050, debug=True)
