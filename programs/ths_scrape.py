#%%
# Import required libraries
from typing import List, Any
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import schedule 
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy import String, text
from sqlalchemy import inspect
from sqlalchemy.types import Integer
from sqlalchemy.types import String 
from sqlalchemy.types import Boolean
from sqlalchemy.types import Date
from sqlalchemy.types import DateTime
from sqlalchemy.types import Text
from datetime import datetime
import os
import sys

# Global variables
all_data = None
cleaned_data = None

def login_with_selenium(email: str, password: str) -> webdriver.Chrome:
    """
    Login to TrustedHousesitters using Selenium WebDriver
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Chrome WebDriver instance after successful login
    """
    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('start-maximized')
    
    # Initialize driver and navigate to login page
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.trustedhousesitters.com/login/')
    
    # Wait for login form and enter credentials
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.NAME, "email")))
    time.sleep(1)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="app"]/main/div/div[1]/div/form/button').click()
    
    # Navigate to assignments page after login
    time.sleep(2)
    driver.get('https://www.trustedhousesitters.com/house-and-pet-sitting-assignments/')
    return driver

def get_data(driver: webdriver.Chrome, javascript_req: str) -> List[Any]:
    """
    Execute JavaScript code to fetch data and close driver
    
    Args:
        driver: Chrome WebDriver instance
        javascript_req: JavaScript code to execute
        
    Returns:
        List of data from JavaScript execution
    """
    result = driver.execute_async_script(javascript_req)
    driver.quit()
    return result

def clean_data(data: List[dict]) -> pd.DataFrame:
    """
    Clean and transform raw data into structured DataFrame
    
    Args:
        data: List of dictionaries containing listing data
        
    Returns:
        Cleaned pandas DataFrame
    """
    global cleaned_data
    
    # Define column types for cleaning
    string_cols = ['user_firstname', 'title', 'hometype', 'location_name', 
                  'pets_animal_name', 'pets_breed', 'pets_name', 'user_membershiptier',
                  'amenities_bedtypes', 'amenities_workspacetypes']
    text_cols = ['features', 'introduction', 'responsibilities', 'assignments_feedback_description']
    int_cols = ['id', 'assignments_durationindays', 'assignments_numberofapplicants']
    bool_cols = ['assignments_isconfirmed', 'assignments_isreviewing', 'amenities_hasbikeaccess', 'carincluded']
    date_cols = ['published', 'assignments_startdate', 'assignments_enddate', 'assignments_lastmodified', 'indexeddate']

    flattened_data = []
    
    # Flatten nested dictionaries
    for listing in data:
        flat_dict = {}
        
        def flatten_dict(d: dict, prefix: str='') -> None:
            for key, value in d.items():
                new_key = f"{prefix}_{key}".lower() if prefix else key.lower()
                new_key = new_key.replace(r'assignments_\d+_', '')
                
                if isinstance(value, dict):
                    flatten_dict(value, new_key)
                elif isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        for item in value:
                            flatten_dict(item, new_key)
                    else:
                        flat_dict[new_key] = ','.join(str(x) for x in value)
                else:
                    if isinstance(value, str):
                        # Remove emojis and non-UTF8 characters
                        value = value.encode('ascii', 'ignore').decode('ascii')
                    flat_dict[new_key] = value
        
        flatten_dict(listing)
        flattened_data.append(flat_dict)
    
    # Convert to DataFrame
    cleaned_data = pd.DataFrame(flattened_data)
    
    # Move ID column to front
    id_column = cleaned_data.pop("id")
    cleaned_data.insert(0, "id", id_column)
    
    # Clean data based on column types
    for col in string_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = cleaned_data[col].fillna('').astype('string')
            
    for col in text_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = cleaned_data[col].fillna('').astype('string')
            
    for col in int_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce').fillna(0).astype('Int64')
            
    for col in bool_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = cleaned_data[col].fillna(False).astype(int)
            
    for col in date_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = pd.to_datetime(cleaned_data[col], errors='coerce').fillna('')
            
    print(cleaned_data.columns)
    
    # Select final columns
    cleaned_data = cleaned_data[['id','assignments_id','user_firstname','published','title','assignments_durationindays','assignments_startdate',
                  'assignments_enddate','assignments_isconfirmed','assignments_isreviewing','assignments_lastmodified',
                  'assignments_numberofapplicants','features','hometype','indexeddate','introduction','location_name','pets_animal_name',
                  'pets_breed','pets_name','responsibilities','user_membershiptier','amenities_bedtypes','amenities_hasbikeaccess','amenities_workspacetypes',
                  'assignments_feedback_description','carincluded']]
    
    cleaned_data['date_scraped'] = datetime.now()
    
    return cleaned_data


class SQLWriter:
    """Class to handle database operations"""
    
    def __init__(self, server_name):
        """Initialize database connection string and SQLAlchemy engine"""
        self.conn_str = (
            f'mssql+pyodbc://{server_name}/THS?'
            'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
        )
        self.engine = create_engine(self.conn_str)
        
        # Define column data types for SQL table
        self.dtype_mapping = {
            'id': Integer(),
            'assignments_id': Integer(),
            'user_firstname': String(50),
            'published': DateTime(),
            'title': Text(),
            'assignments_durationindays': Integer(),
            'assignments_startdate': DateTime(),
            'assignments_enddate': DateTime(),
            'assignments_isconfirmed': Integer(),  # Changed from Boolean to Integer (0/1)
            'assignments_isreviewing': Integer(),  # Changed from Boolean to Integer (0/1)
            'assignments_lastmodified': DateTime(),
            'assignments_numberofapplicants': Integer(),
            'features': Text(),
            'hometype': String(50),
            'indexeddate': DateTime(),
            'introduction': Text(),
            'location_name': String(100),
            'pets_animal_name': String(500),
            'pets_breed': String(500),
            'pets_name': String(500),
            'responsibilities': Text(),
            'user_membershiptier': String(50),
            'amenities_bedtypes': String(100),
            'amenities_hasbikeaccess': Integer(),  # Changed from Boolean to Integer (0/1)
            'amenities_workspacetypes': String(100),
            'assignments_feedback_description': Text(),
            'carincluded': Integer(),  # Changed from Boolean to Integer (0/1)
            'date_scraped': DateTime()
        }

    def write_data(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Write DataFrame to SQL database, handling updates and new records
        
        Args:
            df: DataFrame to write 
            table_name: Name of target SQL table
        """
        # Prepare incoming data
        df['active'] = 1
        df = df.astype({'id': str, 'assignments_id': str})
        
        # Try to get existing data, create table if doesn't exist
        try:
            with self.engine.connect() as conn:
                existing_df = pd.read_sql_table(table_name, conn)
                existing_df = existing_df.astype({'id': str, 'assignments_id': str})
        except:
            with self.engine.connect() as conn:
                trans = conn.begin()
                try:
                    df.to_sql(
                        table_name,
                        conn,
                        if_exists='append',
                        index=False,
                        dtype={**self.dtype_mapping, 'active': Integer()}
                    )
                    trans.commit()
                except:
                    trans.rollback()
                    raise
            return

        # Compare records between new and existing data
        compare_cols = [col for col in df.columns if col not in [
            'id', 'assignments_id', 'indicator', 'date_scraped', 
            'indexeddate', 'active'
        ]]
        
        merged = df.merge(
            existing_df,
            how='outer',
            on=['id', 'assignments_id'],
            indicator=True,
            suffixes=('_new', '_old')
        )
        
        new_records = merged[merged['_merge'] == 'left_only']
        inactive_records = merged[merged['_merge'] == 'right_only']
        potential_updates = merged[merged['_merge'] == 'both']
        
        needs_update = potential_updates[
            potential_updates.apply(lambda row: any(
                row[f"{col}_new"] != row[f"{col}_old"] 
                for col in compare_cols
            ), axis=1)
        ]
        
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                # 1. Deactivate and update records
                if not needs_update.empty:
                    update_conditions = ' OR '.join([
                        f"(id = {id} AND assignments_id = {assignment})"
                        for id, assignment in needs_update[['id', 'assignments_id']].values
                    ])
                    conn.execute(text(
                        f"UPDATE {table_name} SET active = 0 "
                        f"WHERE ({update_conditions}) AND active = 1"
                    ))
                    
                    update_df = df[df.apply(lambda x: any(
                        x['id'] == id and x['assignments_id'] == assignment
                        for id, assignment in needs_update[['id', 'assignments_id']].values
                    ), axis=1)]
                    update_df.to_sql(
                        table_name,
                        conn,
                        if_exists='append',
                        index=False,
                        dtype={**self.dtype_mapping, 'active': Integer()}
                    )
                
                # 2. Deactivate inactive records
                if not inactive_records.empty:
                    inactive_conditions = ' OR '.join([
                        f"(id = {id} AND assignments_id = {assignment})"
                        for id, assignment in inactive_records[['id', 'assignments_id']].values
                    ])
                    conn.execute(text(
                        f"UPDATE {table_name} SET active = 0 "
                        f"WHERE ({inactive_conditions}) AND active = 1"
                    ))
                
                # 3. Insert new records
                if not new_records.empty:
                    new_df = df[df['id'].isin(new_records['id'])]
                    new_df.to_sql(
                        table_name,
                        conn,
                        if_exists='append',
                        index=False,
                        dtype={**self.dtype_mapping, 'active': Integer()}
                    )
                
                trans.commit()
            except Exception as e:
                trans.rollback()
                raise Exception(f"Database transaction failed: {str(e)}")
        

def job(data: pd.DataFrame, server_name: str) -> None:
    """Execute database write job"""
    writer = SQLWriter(server_name)
    try:
        writer.write_data(data, 'seattle')
    except Exception as e:
        raise

def run_scraper(email, password, js_file_path) -> List[Any]:
    """Main function to run scraper"""
    global all_data
    driver = login_with_selenium(email, password)
    
    with open(js_file_path, 'r') as file:
        javascript_code = file.read()
    all_data = get_data(driver, javascript_code)
    
    if isinstance(all_data, list):
        print(True)
    else:
        print(False)
    return all_data

def main() -> None:
    """Run the complete scraping process"""
    global all_data, cleaned_data
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.append(root_dir)
        
    try:
        from data.config import EMAIL, PASSWORD, JS_FILE_PATH, SERVER_NAME
    except ImportError:
        print("Error: config.py file not found in data directory")
        return

    try:
        # Run scraping process
        all_data = run_scraper(EMAIL, PASSWORD, JS_FILE_PATH)
        cleaned_data = clean_data(all_data)
        job(cleaned_data, SERVER_NAME)
            
    except Exception as e:
        print(f"Error running scraper: {str(e)}")

#%%
if __name__ == "__main__":
    
    # Set up logging
    logging.basicConfig(
        filename='scraper.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Add logging handlers for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)
    
    main()
    
    # Log scraper status
    logging.info(f"Scraper run successfully at {datetime.now()}")

    # Schedule hourly job with logging
    def scheduled_job():
        main()
        logging.info(f"Scheduled scraper run completed at {datetime.now()}")
        
    schedule.every().hour.at(":00").do(scheduled_job)
    
    # Keep script running and check for scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
# %%
