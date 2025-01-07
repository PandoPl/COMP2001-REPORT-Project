from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

# Initialise database
db = SQLAlchemy()


# AppUser Model
class AppUser(db.Model):
    __tablename__ = 'AppUser'
    __table_args__ = {'schema': 'CW2'}

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # Admin or User

    trails = db.relationship('Trail', backref='owner', lazy=True)

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def check_password(self, password):
        return self.password == password



# Trail Model
class Trail(db.Model):
    __tablename__ = 'Trail'
    __table_args__ = {'schema': 'CW2'}

    trail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trail_name = db.Column(db.String(100), nullable=False)
    trail_summary = db.Column(db.String(200), nullable=False)
    trail_description = db.Column(db.String(500))
    difficulty = db.Column(db.String(50))
    location = db.Column(db.String(200))
    length = db.Column(db.Float)
    elevation_gain = db.Column(db.Float)
    route_type = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('CW2.AppUser.user_id'), nullable=False)

    trail_points = db.relationship('TrailPoint', backref='trail', lazy=True, cascade="all, delete-orphan")
    feature_mappings = db.relationship('TrailFeatureMapping', backref='trail', lazy=True, cascade="all, delete-orphan")

    def __init__(self, trail_name, trail_summary, trail_description, difficulty, location, length, elevation_gain,
                 route_type, user_id):
        self.trail_name = trail_name
        self.trail_summary = trail_summary
        self.trail_description = trail_description
        self.difficulty = difficulty
        self.location = location
        self.length = length
        self.elevation_gain = elevation_gain
        self.route_type = route_type
        self.user_id = user_id


# Trail Point Model
class TrailPoint(db.Model):
    __tablename__ = 'TrailPoint'
    __table_args__ = {'schema': 'CW2'}

    point_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    trail_id = db.Column(db.Integer, db.ForeignKey('CW2.Trail.trail_id'), nullable=False)

    def __init__(self, latitude, longitude, trail_id):
        self.latitude = latitude
        self.longitude = longitude
        self.trail_id = trail_id


# Trail Feature Model
class TrailFeature(db.Model):
    __tablename__ = 'TrailFeature'
    __table_args__ = {'schema': 'CW2'}

    feature_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    feature_name = db.Column(db.String(100), nullable=False)
    feature_description = db.Column(db.String(200))

    feature_mappings = db.relationship('TrailFeatureMapping', backref='feature', lazy=True,
                                       cascade="all, delete-orphan")

    def __init__(self, feature_name, feature_description):
        self.feature_name = feature_name
        self.feature_description = feature_description


# Trail Feature Mapping Model
class TrailFeatureMapping(db.Model):
    __tablename__ = 'TrailFeatureMapping'
    __table_args__ = {'schema': 'CW2'}

    _TrailID = db.Column(db.Integer, db.ForeignKey('CW2.Trail.trail_id'), primary_key=True)
    _TrailFeatureID = db.Column(db.Integer, db.ForeignKey('CW2.TrailFeature.feature_id'), primary_key=True)

    def __init__(self, _TrailID, _TrailFeatureID):
        self._TrailID = _TrailID
        self._TrailFeatureID = _TrailFeatureID


# Schema for AppUser
class AppUserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AppUser


# Schema for Trail
class TrailSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Trail
        include_relationships = True
        include_fk = True


# Schema for TrailPoint
class TrailPointSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TrailPoint
        include_relationships = True
        include_fk = True


# Schema for TrailFeature
class TrailFeatureSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TrailFeature
        include_relationships = True
        include_fk = True


# Schema for TrailFeatureMapping
class TrailFeatureMappingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TrailFeatureMapping
        include_relationships = True
        include_fk = True
