#!/usr/bin/python3
"""
Gaine Africa API Routes Module

Defines all RESTful endpoints for user management, agricultural record tracking,
and crop prediction features. Implements JWT authentication and CORS security.
"""
from flask_cors import CORS
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask import Blueprint, jsonify, request, session, current_app
from app.models import User, Record
from app import db
from .models.prediction import Prediction
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize password hashing utility
bcrypt = Bcrypt()

# Create main blueprint with versioned API prefix
main_routes = Blueprint("main_routes", __name__)

def authenticate_user(email, password):
    """
    Authenticate user credentials against database records.
    
    Args:
        email (str): User's email address
        password (str): Plaintext password to verify
        
    Returns:
        User: Authenticated user object or None
    """
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):  # Use the model's method
        return user
    return None

@main_routes.after_request
def after_request(response):
    """
    Apply security headers and CORS policies to all responses.
    
    Ensures:
    - Strict origin policy for frontend access
    - Credential support for authenticated requests
    - Approved headers and methods for cross-origin requests
    """
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

@main_routes.route('/api/users', methods=['GET'])
def get_users():
    """
    Retrieve basic information for all registered users.

    Returns:
        JSON: List of user objects with id and name
        Status:
            - 200: Successful retrieval
    """
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name} for user in users])

@main_routes.route('/api/users', methods=['POST'])
def create_user():
    """
Register new user with email uniqueness validation.
    
    Expected JSON Payload:
        - name: User's full name
        - email: Unique email address
        - password: Login credential
        
    Returns:
        JSON: Success/error message
        Status:
            - 201: User created successfully
            - 400: Missing required fields
            - 409: Email already registered
    """
    data = request.get_json()

    # Validate required fields
    if not all(key in data for key in ['name', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check for existing email
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'Email already in use'}), 409
    
    # Create and persist new user
    new_user = User(name=data['name'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@main_routes.route('/api/login', methods=['POST'])
def login():
    """
    Authenticate user and generate JWT access token.
    
    Expected JSON Payload:
        - email: Registered email address
        - password: Account password
        
    Returns:
        JSON: Access token and user details
        Status:
            - 200: Successful login
            - 400: Missing credentials
            - 401: Invalid credentials
    """
    data = request.get_json()

    # Validate input presence
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = authenticate_user(data['email'], data['password'])

    if user:
        # Generate JWT token with user identity
        access_token = create_access_token(identity=user.id)  # Create JWT token
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@main_routes.route('/api/logout', methods=['POST'])
def logout():
    """
    Logs out a user by clearing the session data.

    Returns:
        JSON: Success message
        Status:
            - 200: Logout successful
    """
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

@main_routes.route('/api/users/<int:user_id>/records', methods=['GET'])
@jwt_required()
def get_records(user_id):
    """
    Retrieve agricultural records for authenticated user.
    
    Args:
        user_id (int): Target user ID from URL path
        
    Returns:
        JSON: List of farming records with calculated profits
        Status:
            - 200: Successful retrieval (empty array if no records)
            - 401: Missing/invalid JWT
    """
    records = Record.query.filter_by(user_id=user_id).all()

    if not records:
        
        # Return empty list instead of 404
        return jsonify([]), 200

    return jsonify([
        {
            'id': record.id,
            'crop': record.crop,
            'planting': record.planting,
            'weeding': record.weeding,
            'harvesting': record.harvesting,
            'storage': record.storage,
            'sales': record.sales,
            'profit_or_loss': record.calculate_profit_or_loss()  # Auto-computed
        }
        for record in records
    ]), 200

@main_routes.route('/api/users/<int:user_id>/records', methods=['POST'])
@cross_origin(origin='http://localhost:5173', supports_credentials=True)
@jwt_required()
def create_record(user_id):
    """
    Create new agricultural record for authenticated user.
    
    Expected JSON Payload:
        - crop: Crop type
        - planting: Planting cost
        - weeding: Weeding cost
        - harvesting: Harvesting cost
        - storage: Storage cost
        - sales: Sales revenue
        
    Args:
        user_id (int): Authenticated user ID from JWT
        
    Returns:
        JSON: Success/error message
        Status:
            - 201: Record created
            - 400: Invalid/missing data
            - 401: Unauthorized access
    """
    data = request.get_json()
    user_id = get_jwt_identity()

    # Validate required fields
    required_fields = ["crop", "planting", "weeding", "harvesting", "storage", "sales"]
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Convert financial values to floats
        planting = float(data["planting"])
        weeding = float(data["weeding"])
        harvesting = float(data["harvesting"])
        storage = float(data["storage"])
        sales = float(data["sales"])
    except ValueError:
        return jsonify({'error': 'Invalid number format'}), 400
    
    # Create and persist new record
    new_record = Record(
        user_id=user_id,
        crop=data["crop"],
        planting=planting,
        weeding=weeding,
        harvesting=harvesting,
        storage=storage,
        sales=sales
    )

    new_record.save()

    return jsonify({'message': 'Record created successfully'}), 201

@main_routes.route('/api/users/<int:user_id>/records/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_record(user_id, record_id):
    """
    Update specific agricultural record with partial/full data.
    
    Args:
        user_id (int): User ID from URL path
        record_id (int): Target record ID from URL path
        
    Expected JSON Payload (any combination):
        - crop: Updated crop type
        - planting: Revised planting cost
        - weeding: Revised weeding cost
        - harvesting: Revised harvesting cost
        - storage: Revised storage cost
        - sales: Revised sales revenue
        
    Returns:
        JSON: Success/error message
        Status:
            - 200: Update successful
            - 403: Unauthorized modification attempt
            - 404: Record not found
    """
    data = request.get_json()
    user_id_from_token = get_jwt_identity()

    # Authorization check
    if user_id_from_token != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    record = Record.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'error': 'Record not found'}), 404

    # Partial update implementation
    if "crop" in data:
        record.crop = data["crop"]
    if "planting" in data:
        record.planting = float(data["planting"])
    if "weeding" in data:
        record.weeding = float(data["weeding"])
    if "harvesting" in data:
        record.harvesting = float(data["harvesting"])
    if "storage" in data:
        record.storage = float(data["storage"])
    if "sales" in data:
        record.sales = float(data["sales"])

    record.save()  # Auto-updates profit/loss

    return jsonify({'message': 'Record updated successfully'}), 200

@main_routes.route('/api/users/<int:user_id>/records/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_record(user_id, record_id):
    """
    Permanently remove an agricultural record.
    
    Args:
        user_id (int): User ID from URL path
        record_id (int): Target record ID from URL path
        
    Returns:
        JSON: Success/error message
        Status:
            - 200: Deletion successful
            - 403: Unauthorized deletion attempt
            - 404: Record not found
    """
    user_id_from_token = get_jwt_identity()

    if user_id_from_token != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    record = Record.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        return jsonify({'error': 'Record not found'}), 404

    db.session.delete(record)
    db.session.commit()

    return jsonify({'message': 'Record deleted successfully'}), 200

@main_routes.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Retrieve a single user by ID.
    
    Args:
        user_id (int): The ID of the user.

    Returns:
        JSON response containing the user details or an error message.
        Status:
            - 200: User found
            - 404: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@main_routes.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update a user's details.

    Args:
        user_id (int): The ID of the user.

    Expected JSON Payload:
        - name: Updated full name
        - email: Updated email address
        
    Returns:
        JSON: Success/error message
        Status:
            - 200: Update successful
            - 404: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@main_routes.route('/api/register', methods=['POST'])
def register():
    """Register a new user with additional fields."""
    data = request.get_json()
    
    # Check if required fields are provided
    required_fields = ["name", "email", "password", "phone", "age", "location", "land_size", "crop"]
    if not data or not all(key in data for key in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if user already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User already exists"}), 400

    # Convert land_size safely (avoid float conversion errors)
    try:
        land_size = float(data["land_size"])
    except ValueError:
        return jsonify({"error": "Invalid land size format"}), 400

    # Create a new user instance with additional fields
    new_user = User(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        age=int(data["age"]),
        location=data["location"],
        land_size=land_size,
        crop=data["crop"]
    )
    new_user.set_password(data["password"])  # ✅ Secure password storage

    # Save user to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@main_routes.route('/api/predictions', methods=['GET'])
def get_predictions():
    """
    Retrieve all stored crop yield predictions.
    
    Returns:
        JSON: List of prediction objects
        Status:
            - 200: Always successful (empty array if no predictions)
    """
    predictions = Prediction.query.all()
    return jsonify([prediction.to_dict() for prediction in predictions])

@main_routes.route('/api/predictions', methods=['POST'])
def add_prediction():
    """
    Store new AI-generated crop prediction.
    
    Expected JSON Payload:
        - user_id: Associated farmer ID
        - crop: Predicted crop type
        - yield_estimate: Projected yield in kilograms
        - market_price: Anticipated price per unit
        
    Returns:
        JSON: Success/error message
        Status:
            - 201: Prediction stored
            - 400: Missing required fields
    
    """
    data = request.get_json()

    if not all(key in data for key in ['user_id', 'crop', 'yield_estimate', 'market_price']):
        return jsonify({'error': 'Missing required fields'}), 400

    new_prediction = Prediction(
        user_id=data['user_id'],
        crop=data['crop'],
        yield_estimate=data['yield_estimate'],
        market_price=data['market_price']
    )

    db.session.add(new_prediction)
    db.session.commit()

    return jsonify({'message': 'Prediction added successfully'}), 201