import pandas as pd
import sqlite3
from flask import Flask, request, jsonify

# Step 1: Load the Excel file
df = pd.read_excel("20210309_2020_1 - 4 (1) (1).xls", engine='xlrd')

# Step 2: Strip spaces from column names
df.columns = df.columns.str.strip()

# Step 3: Group by 'API WELL NUMBER' and sum the production columns
annual_data = df.groupby('API WELL  NUMBER')[['OIL', 'GAS', 'BRINE']].sum().reset_index()

# Step 4: Create SQLite Database and insert the data
conn = sqlite3.connect('production_data.db')
annual_data.to_sql('annual_production', conn, if_exists='replace', index=False)

# Close connection
conn.close()

# Step 5: Create Flask API
app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_well_data():
    well_number = request.args.get('well')
    
    # Connect to the database
    conn = sqlite3.connect('production_data.db')
    cursor = conn.cursor()
    
    # Fetch the data for the given well
    cursor.execute("SELECT OIL, GAS, BRINE FROM annual_production WHERE `API WELL  NUMBER`=?", (well_number,))
    data = cursor.fetchone()
    
    conn.close()
    
    # If well data is found, return it as JSON
    if data:
        response = {
            "oil": data[0],
            "gas": data[1],
            "brine": data[2]
        }
        return jsonify(response)
    else:
        return jsonify({"error": "Well not found"}), 404

# Step 6: Run the app on port 8080
if __name__ == '__main__':
    app.run(port=8080)
