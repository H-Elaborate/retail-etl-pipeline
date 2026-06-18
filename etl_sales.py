import pandas as pd
import sqlite3 #RDMS
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent #No matter where I run this from, always use the script’s folder.
df = pd.read_csv(BASE_DIR / "sales_data.csv") #DataFrame\
df = df.drop_duplicates() #Drop duplicates
conn = sqlite3.connect(BASE_DIR / "sales_data.db") #Connecting to SQLite database whilst creating the Database called sales_data.db
df.to_sql("sales", conn, if_exists="replace", index=False) #Write DataFrame to SQL database
print("Data has been successfully loaded into the database.")
