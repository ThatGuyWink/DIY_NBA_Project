--- Western Conference All-Stars Dashboard ---

This project is a Python Dash web application that visualizes NBA stats for the 2025 Western Conference All-Stars, correlating individual performance with team success using interactive scatter plots.

Game log data is fetched from the nba_api, saved to a CSV, uploaded to an AWS S3 bucket, and the dashboard reads from the latest version of that file stored in the bucket.

-- Features --
* Pulls recent player game logs for selected All-Stars.
* Filters data for a specific date range (e.g., 2025-02-19 to 2025-03-30).
* Automatically uploads the data to S3 using an incremented filename format.
* The Dash dashboard downloads and loads the most recently uploaded file.
* Interactive dropdowns for player and stat selection.
* Scatter plot visualizations (e.g., Points vs Rebounds, FGAs vs TOs).

-- How to Run --

Pre-reqs

Python 3.7+
An AWS account with an S3 bucket.
Virtual environment (recommended).


1. Clone the repository 
https://github.com/ThatGuyWink/DIY_NBA_Project.git

2. python -m venv venv
On MacOS: source venv/bin/activate
On Windows: venv\Scripts\activate

3. 3. Configure AWS Credentials
Open both Python files and fill in:

AWS_ACCESSKEY = "your_access_key"
AWS_SECRET_KEY = "your_secret_key"
AWS_BUCKET_NAME = "your_bucket_name"

4. Install Required Dependencies
Dependencies are installed dynamically by the script. However, you may install them manually for control:

pip install
* pandas
* dash
* plotly
* boto3
* nba_api

5. Run the Data Upload Script
This will:
* Fetch game logs.
* Filter them by date.
* Save them to a CSV file.
* Upload them to your S3 bucket with a unique name.

bash: python upload_nba_data.py

6. Run the Dashboard
This will:
* Download the latest file from S3.
* Load the CSV data.
* Launch the Dash app in your browser.

bash: python app.py

-- How It Works -- 

* upload_nba_data.py
  * Uses nba_api to collect game logs.
  * Filters logs between user-defined start and end dates.
  * Saves logs to nba_filtered_game_logs.csv.
  * Uploads this file to your AWS S3 bucket.
  * If a file already exists, the script adds _1, _2, etc., to the filename.

* app.py
  * Connects to S3 using your AWS credentials.
  * Finds the most recent file (by filename suffix).
  * Downloads and loads it into a pandas DataFrame.
  * Creates an interactive Dash web app:
    * Player selection dropdown.
    * X and Y stat selectors.
    * Color-coded by Win/Loss outcome.







