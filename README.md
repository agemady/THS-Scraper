# THS-Scraper Data Flow

## Overview
A Selenium-based web scraper for TrustedHousesitters that collects listing data and stores it in a SQL database.

## Data Flow

1. **Web Scraping**
   - Logs into TrustedHousesitters using Selenium
   - Executes JavaScript to fetch listing data
   - Returns raw JSON data

2. **Data Processing** 
   - Flattens nested JSON structure
   - Cleans and standardizes data types
   - Converts to pandas DataFrame with defined schema
   - Adds timestamp for when data was scraped

3. **Database Operations**
   - Connects to SQL Server database
   - Compares new data with existing records
   - Handles 3 scenarios:
     - New listings: Inserted as new records
     - Updated listings: Old record marked inactive, new version inserted
     - Removed listings: Marked as inactive

4. **Scheduling**
   - Runs initial scrape on startup
   - Schedules hourly scrapes
   - Logs all operations to file and console

## Key Components

- `login_with_selenium()`: Handles authentication
- `get_data()`: Executes JavaScript scraping
- `clean_data()`: Data transformation
- `SQLWriter`: Database operations
- Scheduled job system for automated runs

## Data Schema
Collects listing details including:
- Listing IDs and metadata
- Intro, Description, Responsibilities, 
- Assignment details (dates, duration, status)
- Location and property info
- Pet details
- Amenities and features
