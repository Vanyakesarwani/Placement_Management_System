CREATE DATABASE IF NOT EXISTS placement_db;

USE placement_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') NOT NULL
);

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    branch VARCHAR(100),
    cgpa DECIMAL(3,2),
    backlogs INT DEFAULT 0,
    skills TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(150)
);

CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    role VARCHAR(150) NOT NULL,
    package DECIMAL(10,2),
    min_cgpa DECIMAL(3,2),
    max_backlogs INT DEFAULT 0,
    deadline DATE,
    description TEXT,

    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    status ENUM(
        'Applied',
        'Shortlisted',
        'Interview',
        'Selected',
        'Rejected'
    ) DEFAULT 'Applied',
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),

    UNIQUE (student_id, job_id)
);

