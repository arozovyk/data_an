import json
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the data
with open("json/merged_output.json") as f:
    data = json.load(f)

# Convert the data into a Pandas DataFrame
rows = []
for symbol, entries in data.items():
    for entry in entries:
        rows.append({
            "Symbol": symbol,
            "Date": entry["Date"],
            "High": entry["High"],
            "Low": entry["Low"],
            "Open": entry["Open"],
            "Close": entry["Close"],
            "Volume": entry["Volume"],
            "Marketcap": entry["Marketcap"],
        })

df = pd.DataFrame(rows)

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Cryptocurrency Dashboard"),
    html.Label("Select Symbol:"),
    dcc.Dropdown(
        id="symbol_dropdown",
        options=[{"label": symbol, "value": symbol}
                 for symbol in df["Symbol"].unique()],
        value=df["Symbol"].unique()[0]
    ),
    dcc.Graph(id="time_series_graph"),
])

# Define the callback to update the graph


@app.callback(
    Output("time_series_graph", "figure"),
    [Input("symbol_dropdown", "value")]
)
def update_graph(selected_symbol):
    filtered_df = df[df["Symbol"] == selected_symbol]
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
    sorted_df = filtered_df.sort_values(by="Date", ascending=True)

    fig = px.line(
        sorted_df,
        x="Date",
        y="Close",
        title=f"{selected_symbol} Closing Prices",
        labels={"Date": "Date", "Close": "Closing Price"},
        template="plotly_dark",
    )

    fig.update_layout(
        title={
            "text": f"{selected_symbol} Closing Prices",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Date",
        yaxis_title="Closing Price",
        font=dict(family="Arial", size=14, color="white"),
        legend_title_text="Symbol",
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="gray",
        tickformat="%b %d, %Y",
        tickmode="auto",
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="gray",
         tickmode="auto",
        autorange=True,  # Automatically adjust the range to the data
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
