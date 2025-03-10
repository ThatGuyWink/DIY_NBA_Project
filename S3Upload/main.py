import boto3
import botocore
import time
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from datetime import date  

# AWS configuration
AWS_ACCESSKEY = ""
AWS_SECRET_KEY = ""
AWS_BUCKET_NAME = "nbadiyproject"
AWS_REGION = 'us-east-2'

def file_exists(s3_client, bucket, key):
    # Checks if file already exists in bucket
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        # A 404 error indicates that the file does not exist.
        if e.response['Error']['Code'] == '404':
            return False
        else:
            # Something else has gone wrong.
            raise

def upload_file_with_increment(s3_client, bucket, local_file, s3_key):
    """
    Uploads a file to S3 and, if a file with that key already exists,
    adds a numeric suffix (_1, _2, etc.) until a unique key is found.
    """
    # Split the filename into the base and extension.
    if '.' in s3_key:
        base, ext = s3_key.rsplit('.', 1)
        ext = '.' + ext
    else:
        base, ext = s3_key, ''
    
    new_key = s3_key
    counter = 1
    # Checks if the file exists and keep incrementing until we find a unique key.
    while file_exists(s3_client, bucket, new_key):
        new_key = f"{base}_{counter}{ext}"
        counter += 1

    s3_client.upload_file(local_file, bucket, new_key)
    print(f"Uploaded {local_file} as {new_key}")

def create_nba_csv():
    # Fetch NBA game logs, filter by target dates, and save to a CSV file.
    # Define player names and their IDs
    player_ids = {
        "Stephen Curry": "201939",
        "Kevin Durant": "201142",
        "Shai Gilgeous-Alexander": "1628983",
        "LeBron James": "2544",
        "Nikola Jokić": "203999",
        "Anthony Edwards": "1630162",
        "Anthony Davis": "203076",
        "James Harden": "201935",
        "Jaren Jackson Jr.": "1628991",
        "Alperen Sengun": "1630578",
        "Jalen Williams": "1631113",
        "Victor Wembanyama": "1641705"
    }

    # Dynamically set the target dates to the current date (YYYY-MM-DD format)
    # current_date = date.today().strftime("%Y-%m-%d")
    # Set your own dates
    start_date = "2025-02-19"
    end_date = "2025-03-08"
    target_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d").tolist()

    # Create an empty DataFrame to store filtered player data
    filtered_players_df = pd.DataFrame()

    # Loop through each player and fetch their game logs
    for player_name, player_id in player_ids.items():
        print(f"Fetching game logs for {player_name}...")
        game_logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
        game_logs_df = game_logs.get_data_frames()[0]

        if not game_logs_df.empty:
            game_logs_df["Player"] = player_name  # Add a player name column
            # Convert GAME_DATE from MM/DD/YYYY to YYYY-MM-DD
            game_logs_df["GAME_DATE"] = pd.to_datetime(game_logs_df["GAME_DATE"]).dt.strftime("%Y-%m-%d")
            # Filter only the dates we want
            game_logs_df = game_logs_df[game_logs_df["GAME_DATE"].isin(target_dates)]
            # Append to the final DataFrame
            filtered_players_df = pd.concat([filtered_players_df, game_logs_df], ignore_index=True)

        # Sleep to prevent hitting rate limits
        time.sleep(1)

    # Save the filtered data to a CSV file
        # Can change CSV file name
    csv_filename = "nba_filtered_game_logs.csv"
    filtered_players_df.to_csv(csv_filename, index=False)
    print(f"Filtered game logs saved to {csv_filename}")
    return csv_filename

def main():
    # Initialize the S3 client
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESSKEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    # Create your CSV from NBA data
    csv_filename = create_nba_csv()

    # Upload the CSV file to S3 with incremented filename if needed
    upload_file_with_increment(s3_client, AWS_BUCKET_NAME, csv_filename, csv_filename)

if __name__ == '__main__':
    main()


