# Lottery Number Generator

A Django web application that generates unique sets of lottery numbers based on past draws.

## Features

- Import historical lottery data from Excel files
- Generate unique lottery number combinations that haven't been drawn before
- User-friendly web interface
- API endpoint for mobile app integration

## Installation Guide

Follow these steps to set up and run the Lottery Number Generator project locally:

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/tanzeelgcuf/lottery-number-generator.git
cd lottery-number-generator
Step 2: Create a Virtual Environment
On Windows:
bashpython -m venv venv
venv\Scripts\activate
On macOS/Linux:
bashpython3 -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
bashpip install -r requirements.txt
Step 4: Set Up the Database
bashpython manage.py migrate
Step 5: Create a Media Directory
bashmkdir -p media
Step 6: Run the Development Server
bashpython manage.py runserver
The application will be available at http://127.0.0.1:8000/
Usage Instructions

Import Lottery Data:

Click on the "Import Data" section
Upload your Excel file containing historical lottery data
The file should have columns for Draw Date, Winning Numbers, and Mega Ball


Generate Unique Lottery Numbers:

Select the number of combinations you want to generate
Click "Generate Numbers"
The application will display unique number combinations not found in past draws


View Results:

Generated combinations will be displayed with main numbers and the Mega Ball
Each combination is guaranteed to be unique and not previously drawn



Project Structure

lottery_project/: Main Django project folder
lottery_generator/: The lottery application

models.py: Database models for lottery data
views.py: View functions for handling requests
utils.py: Utility functions for lottery number generation
templates/: HTML templates for the web interface



Development
To contribute to this project:

Fork the repository
Create a feature branch
Make your changes
Submit a pull request
