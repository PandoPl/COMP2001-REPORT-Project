from flask import Flask, request
from flask_restx import Resource, Api, fields
import requests

from models import db, Trail, TrailSchema, AppUser, TrailPoint, TrailFeatureMapping
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from functools import wraps

# Initialise Flask app
app = Flask(__name__)

# Set up database connection
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://PPandov:EwwC859*@dist-6-505.uopnet.plymouth.ac.uk:1433/COMP2001_PPandov'
    '?driver=ODBC+Driver+17+for+SQL+Server'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up JWT configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Use a strong secret key
jwt = JWTManager(app)

authorizations = {
    "BearerAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer <token>'"
    }
}

# Initialise database and marshmallow with the app
db.init_app(app)

# Initialise API
api = Api(app, version='1.0', title='TrailService API',
          description='A microservice for managing trails (JWT Authenticated)',
          security='BearerAuth',authorizations=authorizations)

# Initialise Trail Schema
trail_schema = TrailSchema()
trails_schema = TrailSchema(many=True)

# Define API namespace
trail_ns = api.namespace('trails', description='Trail management operations')
user_ns = api.namespace('users', description='Admin CRUD operations for managing users')

# URL of the external Authenticator API
AUTH_API_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

# Trail model for API documentation
trail_model = trail_ns.model('Trail', {
    'trail_name': fields.String(required=True, description='Trail name'),
    'trail_summary': fields.String(required=True, description='Summary of the trail'),
    'trail_description': fields.String(description='Detailed description of the trail'),
    'difficulty': fields.String(description='Trail difficulty level'),
    'location': fields.String(description='Trail location'),
    'length': fields.Float(description='Trail length in kilometers'),
    'elevation_gain': fields.Float(description='Elevation gain of the trail in meters'),
    'route_type': fields.String(description='Trail route type (e.g., Loop, Out-and-back)'),
    'user_id': fields.Integer(description='User ID of the trail owner', required=True),
})

# Decorator to check for admin role
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()  # Get all custom claims from the token
        if not claims or claims.get('role') != 'admin':
            return {'message': 'Admin privileges required'}, 403
        return fn(*args, **kwargs)
    return wrapper



##############################################
# Helper function to fetch users from the API
##############################################
def fetch_users_from_auth_api():
    try:
        # Send GET request to the AUTH API
        response = requests.get(AUTH_API_URL)
        response.raise_for_status()  # Raise an error if the status code is not 200
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users from API: {e}")
        return []


############################################
# Route to Import Users into the Database
############################################
@user_ns.route('/import_users')
class ImportUsersResource(Resource):
    def get(self):
        """
        Fetch users from the external Authenticator API and save them to the database.
        """
        users = fetch_users_from_auth_api()  # Fetch users from the API
        if not users:
            return {"message": "Failed to fetch users from Authenticator API"}, 500

        created_users = []
        for user_data in users:
            # Check if the user already exists
            existing_user = AppUser.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                # Create a new user and save to the database
                new_user = AppUser(
                    username=user_data['name'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role="user"
                )
                db.session.add(new_user)
                created_users.append(user_data['email'])
            else:
                print(f"User with email {user_data['email']} already exists, skipping.")

        db.session.commit()  # Commit all database changes
        return {"message": "Users imported successfully", "imported_users": created_users}, 201


######################
# LOGIN ENDPOINT
######################

@user_ns.route('/login', methods=['POST'])
class LoginResource(Resource):
    @user_ns.expect(api.model('Login', {
        'email': fields.String(required=True, description='Email address'),
        'password': fields.String(required=True, description='Password'),
    }))
    def post(self):
        """Authenticate user and return a JWT token."""
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if email and password fields are provided
        if not email or not password:
            return {"message": "Email and password are required"}, 400

        # Query database to authenticate user
        user = AppUser.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Generate a JWT token
            access_token = create_access_token(
                identity=str(user.user_id),
                additional_claims={
                    "email": user.email,
                    "role": user.role
                }
            )

            return {"access_token": access_token}, 200
        else:
            return {"message": "Invalid email or password"}, 401



######################
# USER CRUD ENDPOINTS
######################

# Get all users (Admin only)
@user_ns.route('/all')
class GetAllUsersResource(Resource):
    @api.doc(security='BearerAuth')
    @jwt_required()
    @admin_required
    def get(self):
        """Get all users (Admin only)."""
        users = AppUser.query.all()
        return [{'id': user.user_id, 'username': user.username, 'email': user.email, "password": user.password,'role': user.role} for user in
                users], 200

# Create a new user (Admin only)
@user_ns.route('/create')
class CreateUserResource(Resource):
    @user_ns.expect(api.model('User', {
        'username': fields.String(required=True, description='Username'),
        'email': fields.String(required=True, description='Email'),
        'password': fields.String(required=True, description='Password'),
        'role': fields.String(required=True, description='User role', enum=['admin', 'user']),
    }))
    @api.doc(security='BearerAuth')
    @jwt_required()
    @admin_required
    def post(self):
        """Create a new user (Admin only)."""
        data = request.get_json()
        new_user = AppUser(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return {'id': new_user.user_id, 'username': new_user.username, 'email': new_user.email,
                'role': new_user.role}, 201


# Fetch or delete a specific user by ID (Admin functionality)
@user_ns.route('/<int:user_id>')
class UserResource(Resource):
    @api.doc(security='BearerAuth')
    @jwt_required()
    @admin_required
    def get(self, user_id):
        """Get a user by ID (Admin only)."""
        user = AppUser.query.get_or_404(user_id)
        return {'id': user.user_id, 'username': user.username, 'email': user.email, 'role': user.role}, 200

    @jwt_required()
    @admin_required
    def delete(self, user_id):
        """Delete a user by ID (Admin only)."""
        user = AppUser.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200


######################
# TRAIL CRUD ENDPOINTS
######################
@trail_ns.route('/')
class TrailsResource(Resource):
    @jwt_required()
    def get(self):
        """Get all trails (limited information if not an admin)."""
        trails = Trail.query.all()

        # Get the user's role from JWT claims
        claims = get_jwt()

        user_role = claims.get('role')

        if user_role == 'admin':
            #Admins get the full information
            return trails_schema.dump(trails), 200
        else:
            # Limited view for non-admin users
            limited_data = [
                {
                    "trail_id": trail.trail_id,
                    "trail_name": trail.trail_name,
                    "trail_summary": trail.trail_summary,
                    "difficulty": trail.difficulty,
                    "location": trail.location,
                    "length": trail.length,
                    "elevation_gain": trail.elevation_gain,
                    "route_type": trail.route_type,
                }
                for trail in trails
            ]
            return limited_data, 200

    @api.doc(security='BearerAuth')
    @trail_ns.expect(trail_model)
    @jwt_required()
    @admin_required
    def post(self):
        """Create a new trail (Admin only)."""
        data = request.get_json()
        new_trail = Trail(
            trail_name=data['trail_name'],
            trail_summary=data['trail_summary'],
            trail_description=data.get('trail_description'),
            difficulty=data.get('difficulty'),
            location=data.get('location'),
            length=data.get('length'),
            elevation_gain=data.get('elevation_gain'),
            route_type=data.get('route_type'),
            user_id=data['user_id'],
        )
        db.session.add(new_trail)
        db.session.commit()
        return trail_schema.dump(new_trail), 201


@trail_ns.route('/<int:id>')
class TrailResource(Resource):
    @jwt_required()
    def get(self, id):
        """Get trail by ID (any user can view, Admin gets complete information)."""
        trail = Trail.query.get_or_404(id)

        claims = get_jwt()

        # Limited view for non-admin users
        limited_data = {
            "trail_id": trail.trail_id,
            "trail_name": trail.trail_name,
            "trail_summary": trail.trail_summary,
            "difficulty": trail.difficulty,
            "location": trail.location,
            "length": trail.length,
            "elevation_gain": trail.elevation_gain,
            "route_type": trail.route_type,
        }

        # Check if user is an admin, if they are then show them the rest of the info
        if claims.get('role') == 'admin':
            limited_data["trail_description"] = trail.trail_description
            limited_data["user_id"] = trail.user_id

        return limited_data, 200

    @api.doc(security='BearerAuth')
    @trail_ns.expect(trail_model)
    @jwt_required()
    @admin_required
    def put(self, id):
        """Update an existing trail (Admin only)."""
        trail = Trail.query.get_or_404(id)
        data = request.get_json()
        trail.trail_name = data.get('trail_name', trail.trail_name)
        trail.trail_summary = data.get('trail_summary', trail.trail_summary)
        trail.trail_description = data.get('trail_description', trail.trail_description)
        trail.difficulty = data.get('difficulty', trail.difficulty)
        trail.location = data.get('location', trail.location)
        trail.length = data.get('length', trail.length)
        trail.elevation_gain = data.get('elevation_gain', trail.elevation_gain)
        trail.route_type = data.get('route_type', trail.route_type)
        db.session.commit()
        return trail_schema.dump(trail), 200

    @api.doc(security='BearerAuth')
    @jwt_required()
    @admin_required
    def delete(self, id):
        """Delete an existing trail (Admin only)."""
        trail = Trail.query.get_or_404(id)
        db.session.delete(trail)
        db.session.commit()
        return {'message': 'Trail deleted successfully'}, 200


if __name__ == '__main__':
    # Start the Flask app
    app.run(host="0.0.0.0", port=8000, debug=True)