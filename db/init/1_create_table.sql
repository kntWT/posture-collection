SET CHARSET UTF8;

CREATE DATABASE IF NOT EXISTS posture_correction_db DEFAULT CHARACTER SET utf8 /*!80016 DEFAULT ENCRYPTION='N' */;

USE posture_correction_db;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    internal_posture_calibration_id INT,
    neck_to_nose_standard DOUBLE,
    neck_angle_offset DOUBLE NOT NULL DEFAULT 0,
    created_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
);

CREATE TABLE IF NOT EXISTS internal_postures (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL DEFAULT 1,
    file_name TEXT NOT NULL,
    orientation_alpha DOUBLE,
    orientation_beta DOUBLE, 
    orientation_gamma DOUBLE,
    pitch DOUBLE,
    yaw DOUBLE,
    roll DOUBLE,
    nose_x DOUBLE,
    nose_y DOUBLE,
    neck_x DOUBLE,
    neck_y DOUBLE,
    neck_to_nose DOUBLE,
    standard_dist DOUBLE,
    calibrate_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP(3) DEFAULT NULL,
    updated_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
);

CREATE TABLE IF NOT EXISTS external_postures (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL DEFAULT 1,
    neck_angle DOUBLE NOT NULL,
    torso_angle DOUBLE NOT NULL,
    created_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
);
