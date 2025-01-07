-- Create Schema
CREATE SCHEMA CW2;
GO

-- Create AppUser Table
CREATE TABLE CW2.AppUser (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) NOT NULL UNIQUE,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password NVARCHAR(200) NOT NULL,
    role NVARCHAR(10) NOT NULL  -- Either 'admin' or 'user'
);
GO

-- Create Trail Table
CREATE TABLE CW2.Trail (
    trail_id INT IDENTITY(1,1) PRIMARY KEY,
    trail_name NVARCHAR(100) NOT NULL,
    trail_summary NVARCHAR(200) NOT NULL,
    trail_description NVARCHAR(500),
    difficulty NVARCHAR(50),
    location NVARCHAR(200),
    length FLOAT,
    elevation_gain FLOAT,
    route_type NVARCHAR(50),
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES CW2.AppUser(user_id) ON DELETE CASCADE
);
GO

-- Create TrailPoint Table
CREATE TABLE CW2.TrailPoint (
    point_id INT IDENTITY(1,1) PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    trail_id INT NOT NULL,
    FOREIGN KEY (trail_id) REFERENCES CW2.Trail(trail_id) ON DELETE CASCADE
);
GO

-- Create TrailFeature Table
CREATE TABLE CW2.TrailFeature (
    feature_id INT IDENTITY(1,1) PRIMARY KEY,
    feature_name NVARCHAR(100) NOT NULL,
    feature_description NVARCHAR(200)
);
GO

-- Create TrailFeatureMapping Table
CREATE TABLE CW2.TrailFeatureMapping (
    _TrailID INT NOT NULL,
    _TrailFeatureID INT NOT NULL,
    PRIMARY KEY (_TrailID, _TrailFeatureID),
    FOREIGN KEY (_TrailID) REFERENCES CW2.Trail(trail_id) ON DELETE CASCADE,
    FOREIGN KEY (_TrailFeatureID) REFERENCES CW2.TrailFeature(feature_id) ON DELETE CASCADE
);
GO