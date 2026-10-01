import os
import requests
from dotenv import load_dotenv

load_dotenv() 
url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"
params = {
    "app_id": os.getenv("ADZUNA_APP_ID"),
    "app_key": os.getenv("ADZUNA_APP_KEY"),
    "what": "software engineer",
    "results_per_page": 5
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.json())