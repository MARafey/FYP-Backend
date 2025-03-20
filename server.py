from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import firestore
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_config import * 
from Analysis import Calling_for_analysis


from Parinomo import Parinomo

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Resource Sharing (CORS) for React frontend

# Initialize Firestore client
db = firestore.client()

# Route for file upload
@app.route('/upload', methods=['POST'])
def uploadcode():
    data = request.get_json()
    core_type = data.get('core_type')
    ram_type = data.get('ram_type')
    Scode = data.get('code')
    processors_count = data.get('processors_count')

    Pcode = Parinomo(Scode, core_type, ram_type,processors_count)

    if not core_type or not ram_type or not Scode:
        return jsonify({'message': 'All fields are required!', 'status': 'fail'}), 400
    else:
        # returning code to frontend
        return jsonify({'message': 'Code Processed successfully!', 'status': 'success', 'Pcode': Pcode}), 200

# Route for user signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required!'}), 400

    # Check if user already exists by email
    user_ref = db.collection('users').where('email', '==', email).get()
    if len(user_ref) > 0:
        return jsonify({'success': False, 'message': 'Email already exists!'}), 400

    # Hash the password before saving it to the database
    hashed_password = generate_password_hash(password)

    # Save user to Firestore database
    db.collection('users').add({
        'name': name,
        'email': email,
        'password': hashed_password  # Store hashed password
    })

    return jsonify({'success': True, 'message': 'Signup successful!'}), 201


# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required!'}), 400

    # Check if user exists by email
    user_ref = db.collection('users').where('email', '==', email).get()

    if len(user_ref) == 0:
        return jsonify({'success': False, 'message': 'User does not exist!'}), 404

    # Verify the password by comparing hashed passwords
    for user in user_ref:
        user_data = user.to_dict()
        if check_password_hash(user_data['password'], password):
            return jsonify({'success': True, 'message': 'Login successful!'}), 200

    return jsonify({'success': False, 'message': 'Invalid email or password!'}), 401


@app.route('/Analysis', methods=['POST'])
def Analysis():
    data = request.get_json()
    
    # print(f"data= {data}")
    
    # printing the data
    # for key in data:
    #     print(key, ":", data[key], "\n")
    # print(data["P_Code"]) 
    data = data.get('body')
    # print(f"data= {data}")   
    P_Code = data.get('P_Code')
    S_Code = data.get('S_Code')
    
    if P_Code is None or S_Code is None:
        return jsonify({'error': 'P_Code and S_Code are required!'}), 400

    P_Code = '#include<omp.h>\n' + '#define tile_size=16\n' + P_Code
    P_Analysis = Calling_for_analysis(P_Code, 1)
    S_Analysis = Calling_for_analysis(S_Code, 0)

    return jsonify({'P_Analysis': P_Analysis, 'S_Analysis': S_Analysis}), 200

if __name__ == '__main__':
    app.run(debug=True)
