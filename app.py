import sys
import subprocess
import boto3
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


# Ensure required packages are installed
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


for package in ["pandas", "plotly", "dash", "boto3"]:
    try:
        __import__(package)
    except ImportError:
        install_package(package)

# AWS configuration
AWS_ACCESSKEY = ""
AWS_SECRET_KEY = ""
AWS_BUCKET_NAME = "nbadiyproject"
AWS_REGION = 'us-east-2'
LOCAL_FILE = "nba_filtered_game_logs.csv"


def get_latest_s3_file():
    # Retrieve the latest incremented CSV file from S3.
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESSKEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix="nba_filtered_game_logs_")
    if "Contents" not in response:
        print("No matching files found in S3.")
        exit(1)

    files = [obj['Key'] for obj in response['Contents']]
    latest_file = sorted(files, key=lambda x: int(x.split('_')[-1].split('.')[0]), reverse=True)[0]
    print(f"Latest file found: {latest_file}")
    return latest_file


def download_s3_file():
    # Download the latest game log CSV from S3.
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESSKEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    latest_file = get_latest_s3_file()
    s3_client.download_file(AWS_BUCKET_NAME, latest_file, LOCAL_FILE)
    print(f"Downloaded {latest_file} from S3.")


# Fetch latest data from S3
download_s3_file()
df = pd.read_csv(LOCAL_FILE)

# Define available players and stat columns
players = df["Player"].unique()
stat_options = ["PTS", "REB", "AST", "TOV", "FGA", "FTA", "FGM", "FTM"]

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("NBA Player Game Log Dashboard"),

    # Player selection dropdown
    html.Label("Select Player:"),
    dcc.Dropdown(
        id="player-dropdown",
        options=[{"label": player, "value": player} for player in players],
        value=players[0] if len(players) > 0 else None,
        multi=False
    ),

    # Scatter plot selection
    html.Label("Select X-axis Stat:"),
    dcc.Dropdown(
        id="x-axis-dropdown",
        options=[{"label": stat, "value": stat} for stat in stat_options],
        value="PTS"
    ),

    html.Label("Select Y-axis Stat:"),
    dcc.Dropdown(
        id="y-axis-dropdown",
        options=[{"label": stat, "value": stat} for stat in stat_options],
        value="REB"
    ),

    # Scatter plot
    dcc.Graph(id="scatter-plot"),
])


@app.callback(
    Output("scatter-plot", "figure"),
    [Input("player-dropdown", "value"),
     Input("x-axis-dropdown", "value"),
     Input("y-axis-dropdown", "value")]
)
def update_graph(selected_player, x_stat, y_stat):
    if selected_player is None:
        return px.scatter(title="No Data Available")
    filtered_df = df[df["Player"] == selected_player]
    fig = px.scatter(
        filtered_df,
        x=x_stat,
        y=y_stat,
        color="WL",
        title=f"{selected_player}: {x_stat} vs {y_stat}",
        labels={"WL": "Win/Loss"},
        size_max=10
    )
    return fig


# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
