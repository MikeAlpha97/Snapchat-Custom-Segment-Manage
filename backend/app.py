import random
import string
import uuid
import csv
from flask import Flask, request, json, jsonify, flash, Blueprint, send_file
from connection import cnxn, cursor
from flask_cors import CORS
from setting.config import ip, app_port
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, 
    get_jwt_identity
)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "\xfd{H\xeddwwt5<\4495\aqwer9\xe3\x321qwer5\xd1\x234234O<!\asdf\xa2\xa0\x9fR"

jwt = JWTManager(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

output_folder = "C:\Work\Snapchat Custom Ads\Generated Files"

country_codes = [
    {'code': '1', 'len': 10, 'name': 'US'},
    {'code': '44', 'len': 10, 'name': 'UK'},
    {'code': '33', 'len': 10, 'name': 'France'},
    {'code': '966', 'len': 9, 'name': 'KSA'},
    {'code': '92', 'len': 10, 'name': 'PAK'}
    # Add more country codes as needed
]
# Define a route '/custom_audience' which supports GET and POST methods
@app.route('/custom_audience', methods=['GET', 'POST'])
def custom_audience():
    try:
        # If the request method is GET
        if request.method == 'GET':
            # Retrieve all data from the 'audience' table
            query_get_audience_data = ("SELECT * FROM audience")
            cursor.execute(query_get_audience_data)
            # Get column names
            desc = cursor.description
            column_names = [col[0] for col in desc]
            # Create a list of dictionaries representing rows of data
            audience = [dict(zip(column_names, row))
                         for row in cursor.fetchall()]
            # Return data in JSON format with a success status code
            return jsonify({"response": "success", "data": audience}), 200
        # If the request method is POST
        elif request.method == 'POST':
            try:
                # Extract email, advertisement ID, and mobile number from the JSON request data
                email = request.json['email'] if request.json['email']!=None else ''
                adv_id = request.json['name'] if request.json['adv_id']!=None else ''
                mobile = request.json['mobile'] if request.json['mobile']!=None else ''
                # Insert the data into the 'AUDIENCE' table, ignoring duplicates based on mobile number
                query = f"""INSERT INTO AUDIENCE (ad_id, email, mobile) VALUES ('{adv_id}', '{email}', '{mobile}') ON CONFLICT (mobile) DO NOTHING;"""
                cursor.execute(query)
                # Commit the transaction
                cnxn.commit()
                # Return success response
                return jsonify({"response": "success"}), 200
            except Exception as e:
                # Handle exceptions, print the error, and return an error response
                print(e)
                return jsonify({"response": "error", "Error": e}), 500
    except Exception as e:
        # Rollback the transaction in case of exceptions and return a failure response
        cursor.execute("ROLLBACK")
        return jsonify({"response": "failed!", "message": e}), 205

# Define a route '/generate_random_data' which supports GET method
@app.route('/generate_random_data', methods=['GET'])
def generate_random_data():
    try:
        # Generate and insert random data into the 'custom_audience' table
        for i in range(0,100):
            # Generate random email, advertisement ID, and mobile number
            email = generate_random_email()
            adv_id = generate_random_advertisement_id()
            mobile = generate_random_mobile_number(country_codes)

            # Insert the generated data into the 'custom_audience' table, ignoring duplicates based on mobile number
            query = f"""INSERT INTO custom_audience (ad_id, email, mobile) VALUES ('{adv_id}', '{email}', '{mobile}') ON CONFLICT (mobile) DO NOTHING;"""
            cursor.execute(query)
            # Commit the transaction
            cnxn.commit()
        # Return success response
        return jsonify({"response": "success"}), 200
    except Exception as e:
        # Rollback the transaction in case of exceptions and return a failure response
        cursor.execute("ROLLBACK")
        return jsonify({"response": "failed!", "message": e}), 205

@app.route('/generate_excel_files', methods=['GET'])
def generate_excel_files():
    try:
        cursor.execute("SELECT email FROM custom_audience")
        emails = cursor.fetchall()
        with open(output_folder + "/emails.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for email in emails:
                writer.writerow(email)

        # Fetch mobile numbers and write to CSV
        cursor.execute("SELECT mobile FROM custom_audience")
        mobile_numbers = cursor.fetchall()
        with open(output_folder + "/mobile_numbers.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for mobile_number in mobile_numbers:
                writer.writerow(mobile_number)

        # Fetch advertisement IDs and write to CSV
        cursor.execute("SELECT ad_id FROM custom_audience")
        ad_ids = cursor.fetchall()
        with open(output_folder + "/ad_ids.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for ad_id in ad_ids:
                writer.writerow(ad_id)

        return jsonify({"response": "Success. CSV files exported successfully!"}), 200
    except Exception as error:
        return jsonify({"response": "failed!", "message": error}), 205

def generate_random_email():
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com'])
    return f"{username}@{domain}"


def generate_random_mobile_number(country_code_data):
    country_code_info = random.choice(country_code_data)
    country_code = country_code_info['code']
    number_length = country_code_info['len']

    # Generate the rest of the number randomly
    phone_number = ''.join(random.choices(string.digits, k=number_length))
    return f"{country_code}{phone_number}"

def generate_random_advertisement_id():
    return str(uuid.uuid4())

# Sample usage
print("Random Email:", generate_random_email())
print("Random Mobile Number:", generate_random_mobile_number(country_codes))
print("Random Advertisement ID:", generate_random_advertisement_id())

if __name__ == '__main__':
    app.run(host=ip, port=app_port, debug=True)