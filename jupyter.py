

import os
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import numpy as np

import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
api_key:str=os.environ.get("NEXT_PUBLIC_GOOGLE_API_KEY")  


print("api key yyy y yy ",api_key)

import google.generativeai as genai

# Configure API key
genai.configure(api_key=api_key)  # Use your actual API key here

# Create a GenerativeModel instance with the model name
model = genai.GenerativeModel("gemini-1.5-flash")

# Generate only Python code to calculate the average of an array
response = model.generate_content("Write Python code to find the average of an array. Only return the code, no additional text, just code so that I can run it in command line and the name should be Mean_array")

# Print the generated code
print(response.text.strip())



def check_data_type_google_genAI(nums):
    prompt = f"""
        give me a function named validate_array
        iterate over the array and check if data type is integer or float or not
        If any of the entry is neither integer nor float return -1
        else 1
        Just give me the code ,no additional text ,so to use that code directly
    """

    response = model.generate_content(prompt)

    generated_code = response.text.strip()
    code_lines = generated_code.splitlines()
    code_lines=code_lines = code_lines[1:-1]
    cleaned_code = "\n".join(code_lines)
    # print(cleaned_code)
    exec(cleaned_code, globals())

    # Dynamically call the generated function
    function_name = "validate_array"
    if function_name in globals():
        result = globals()[function_name](nums)  # Pass nums to the dynamically defined function
        return result
    else:
        raise ValueError(f"The function {function_name} was not correctly defined.")
    
    
def make_prompt_google_genAI(operation ,nums):
    
    prompt = f"""
    Write Python code to find the {operation} of an array. The code should:
    - Iterate over the array
    - Check for NaN values
    - Skip the NaN values when performing the {operation}
    - Maintain a count of the NaN values
    - Return the {operation} and number of nan values, no additional text, just code so that I can run it in command line.
    The name of the function should be {operation}_array.
    """
   
    response = model.generate_content(prompt)
    # print(response)
    generated_code = response.text.strip()
    
    code_lines = generated_code.splitlines()
    code_lines=code_lines = code_lines[1:-1]
    cleaned_code = "\n".join(code_lines)
    # print(cleaned_code)
    exec(cleaned_code, globals())

    # Dynamically call the generated function
    function_name = f"{operation}_array"
    if function_name in globals():
        result = globals()[function_name](nums)  # Pass nums to the dynamically defined function
        return result
    else:
        raise ValueError(f"The function {function_name} was not correctly defined.")

    


import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("NEXT_PUBLIC_SUPABASE_KEY")  
url= os.environ.get("NEXT_PUBLIC_SUPABASE_URL") 
# key ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ1cGpsa2h2emFuZHVicHVnb2F6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ3ODQzMTksImV4cCI6MjA1MDM2MDMxOX0.5B7hbvTOF6gm9nYmIZJdD_iigRWtxy2PZEv76eg-fLQ"

print(url)
print("key",key)


supabase: Client = create_client(url, key)

def saving_records_in_sql_db(email ,authId,C3 ,C4 ,operation):
    """saving records in a table format"""
    response = supabase.table("ColRecords").insert({
        "email": email,
        "C3": C3,
        "C4": C4,
        "operation": operation
    }).execute()


from flask import Flask, request, jsonify
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def testprint():
    return "<h1>app</h1>"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    operation = request.form['operation']
    email=request.form['email']
    auth_id = request.form['auth']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Read CSV file into DataFrame
        df = pd.read_csv(filepath)

        # Check if C3 and C4 columns exist
        if 'C3' not in df.columns or 'C4' not in df.columns:
            return jsonify({"error": "Missing columns C3 or C4"}), 400

        # Extract C3 and C4 columns as lists
        c3_data = df['C3'].tolist()
        c4_data = df['C4'].tolist()


        print("email is",email)
        print("email is",auth_id)


        # Validate if NaN values are present in C3 and C4
        number_of_Nans_in_C3 = df["C3"].isna().sum()
        number_of_Nans_in_C4 = df["C4"].isna().sum()

        # Print the NaN count for debugging

        # 1. to check the data type of the column
        is_C3_valid = check_data_type_google_genAI(c3_data)
        is_C4_valid = check_data_type_google_genAI(c4_data)
        
        result_of_C3 =-1
        result_of_C3=-1
        nan_count_c3=0
        nan_count_c4=0
        if is_C3_valid!=-1:
            result_of_C3, nan_count_c3 = make_prompt_google_genAI(operation, c3_data)

        if is_C4_valid!=-1:
            result_of_C4, nan_count_c4 = make_prompt_google_genAI(operation, c4_data)
        
        to_return = {}

        to_return["c3"] = result_of_C3
        to_return["c4"] = result_of_C4 
        
        to_return["c3nans"]=int(number_of_Nans_in_C3)
        to_return["c4nans"]=int(number_of_Nans_in_C4)

        # t= np.array()

        to_return["C3data"]=c3_data

        # calling the function to save the records in my table
        saving_records_in_sql_db(email ,auth_id ,result_of_C3 ,result_of_C4 ,operation)

        return jsonify(to_return)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
