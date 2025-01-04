# Twitter Trending Topics Scraper

This project automates Twitter login and scrapes trending topics using Selenium, storing the results in MongoDB. It features a Flask web app where users can run the script and view trending topics, IP address, and a JSON extract of the data.

## Requirements

- Python 3.x
- Selenium
- Flask
- requests
- pymongo
- python-dotenv

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
2. **Navigate to the project directory:**
    ```sh
   cd your-repo
3. **Create a virtual environment:**
    ```sh
   .venv\Scripts\activate
   On macOS and Linux:
   source .venv/bin/activate
4. **Install the required packages:**
    ```sh
   pip install -r requirements.txt
5. **reate a .env file and add your environment variables:**
   ```sh
   touch .env
6. **Populate the .env file with your environment variables, e.g.:**
   ```sh
    TWITTER_USERNAME= 
    TWITTER_PASSWORD= 
    TWITTER_EMAIL= 
    PROXY_HOST= 
    PROXY_PORT= 
    PROXY_USERNAME= 
    PROXY_PASSWORD= 
    MONGO_URI= 
7. **Start the Flask application:**
   ```sh
    python main.py

**Open your web browser and navigate to:**

http://127.0.0.1:5000/

```sh
Directory Structure
project_directory/
│
├── main.py                  # Flask application
├── .env                     # Environment variables
├── app.py                   # Selenium script
├── requirements.txt         # Required Python packages
│
└── templates/
    └── index.html           # HTML template
