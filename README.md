Gym Lead Scoring System

An automated pipeline designed for marketing agencies to identify and prioritize high-value gym leads. This system ingests raw business data from Excel files, enriches it with web-scraped information, and applies a weighted scoring model to rank prospects based on their potential value and need for marketing services.
Key Features

    Batch Processing: Ingests and combines lead data from multiple Excel files.

    Data Validation: Cleans the dataset by validating email syntax.

    Business Size Analysis: Scores businesses based on indicators of size and market position (e.g., national chains vs. independent gyms).

    Digital Presence Scoring: Analyzes a lead's website for quality indicators like mobile-friendliness, SSL, SEO basics, and the presence of online booking systems.

    Engagement Opportunity Analysis: Scrapes Google Maps to assess the opportunity for review generation campaigns by analyzing review counts and ratings.

    Weighted Scoring & Tiering: Calculates a final weighted score and categorizes leads into actionable tiers (e.g., "HOT", "WARM", "COLD").

    Actionable Insights: Identifies specific needs, such as "Needs Redesign" or "Needs Reviews," to guide the sales pitch.

    Free Tier Operation: Utilizes free-to-use libraries like requests, BeautifulSoup, and Selenium for web scraping, requiring no paid API keys.

How It Works: The Scoring Pipeline

The system processes leads through a sequential pipeline:

    Ingestion: Loads lead data (business name, email, website, etc.) from specified .xlsx files located in the data/raw/ directory.

    Validation: Filters out leads with invalid email addresses to ensure data quality.

    Scoring (Per Lead):

        Business Score: Examines the business name and address for keywords indicating it's part of a large chain or a premium brand.

        Digital Presence Score: Scrapes the business website to evaluate its technical and design quality. A lower score indicates a greater need for web design services.

        Engagement Score: Scrapes the business's Google Maps page to determine its review count and average rating. A low number of reviews represents a high-opportunity score.

    Final Calculation: Combines the individual scores using a predefined weighting system to produce a single TotalScore.

    Tiering: Assigns a priority tier and an estimated monthly value based on the TotalScore.

    Output: Saves the final, sorted list of scored leads to a CSV file (data/output/scored_leads.csv) and prints the top 10 prospects to the console.

Technology Stack

    Core: Python 3.8+

    Data Handling: Pandas, Openpyxl

    Web Scraping: Requests, BeautifulSoup4, Selenium

    Browser Automation: webdriver-manager for automatic ChromeDriver management.

    Data Validation: email-validator (via regex in the current implementation).

    Database (optional): SQLite3 for future data persistence.

Setup and Installation

1. Prerequisites:

    Python 3.8 or higher

    Google Chrome browser installed (for Selenium)

2. Clone the Repository:
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
git clone <your-repository-url>
cd gym-lead-scorer

  

3. Create a Virtual Environment:
It's highly recommended to use a virtual environment to manage dependencies.
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
# For Mac/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate

  

4. Install Dependencies:
The webdriver-manager library will automatically download the correct ChromeDriver for your version of Google Chrome.
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
pip install -r requirements.txt

  

Usage

1. Prepare Your Data:

    Place your lead data in Excel files (.xlsx) inside the data/raw/ directory.

    Ensure your files contain at least the following columns: BusinessName, Address, ZIP, Email, WebsiteURL, Gmaps_URL.

2. Configure the Pipeline:

    Open src/main.py.

    In the if __name__ == "__main__": block, update the file_paths list to point to your input Excel files.

3. Run the Scoring Pipeline:
Execute the main script from the root directory of the project.
code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
python src/main.py

  

4. View the Results:

    The top 10 leads will be printed to your console.

    A full, scored, and sorted list will be saved to data/output/scored_leads.csv.

Example Console Output:
code Code
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
=== TOP PROSPECTS FOR NEW MARKETING AGENCY ===
         BusinessName                      Email    Phone                      Website      City  TotalScore                       Tier EstimatedValue  NeedsRedesign  NeedsReviews
    Example Fitness Hub      contact@example.com  555-1234      https://example.com  Dallas          85  HOT - High Value Prospect  $2000-5000/month           True          True
 Another Gym Center LLC         info@another.gym  555-5678       https://another.gym  Dallas          78  WARM - Good Opportunity    $1000-2500/month          False          True
...

  

Project Structure
code Code
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END

    
gym-lead-scorer/
├── data/
│   ├── raw/              # Input Excel files go here
│   └── output/           # Scored CSV results are saved here
├── src/
│   ├── data/
│   │   ├── ingestion.py    # Handles loading data from files
│   │   └── validation.py   # Data validation logic
│   ├── scoring/
│   │   ├── business_metrics.py
│   │   ├── digital_presence.py
│   │   ├── engagement_metrics.py
│   │   └── priority_calculator.py
│   ├── utils/
│   │   └── db_manager.py     # (Future Use) Handles database interactions
│   ├── free_scraper.py     # (Future Use) Centralized scraping utility
│   └── main.py             # Main pipeline orchestration script
├── requirements.txt
├── setup.py
└── README.md

  

Use Arrow Up and Arrow Down to select a turn, Enter to jump to it, and Escape to return to the chat.
