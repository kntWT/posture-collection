SET CHARSET UTF8;

CREATE DATABASE IF NOT EXISTS posture_correction_db DEFAULT CHARACTER SET utf8 /*!80016 DEFAULT ENCRYPTION='N' */;

USE posture_correction_db;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    neck_to_nose_standard DOUBLE,
    neck_angle_offset DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS internal_postures (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL DEFAULT 1,
    image_path TEXT NOT NULL,
    orientation_alpha DOUBLE NOT NULL,
    orientation_beta DOUBLE NOT NULL, 
    orientation_gamma DOUBLE NOT NULL,
    pitch DOUBLE,
    yaw DOUBLE,
    roll DOUBLE,
    nose_x DOUBLE,
    nose_y DOUBLE,
    neck_to_nose DOUBLE,
    standard_dist DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS external_postures (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL DEFAULT 1,
    internal_posture_id INT,
    neck_angle DOUBLE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
