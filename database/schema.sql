-- ============================================================
-- Academic Management System — Database Schema
-- ============================================================
-- This script creates all tables for the Academic Management
-- System with proper normalization, primary keys, foreign keys,
-- and one-to-many relationships.
-- ============================================================

CREATE DATABASE IF NOT EXISTS academic_management;
USE academic_management;

-- ============================================================
-- 1. USERS TABLE (Authentication Module)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'faculty') NOT NULL DEFAULT 'faculty',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. FACULTY TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. SUBJECTS TABLE (Normalization)
-- ============================================================
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    credits INT DEFAULT 3
);

-- ============================================================
-- 4. STUDENTS TABLE (Student Management Module)
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    section VARCHAR(10) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(15),
    dob DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. ATTENDANCE TABLE (Attendance Management Module)
-- One student → Many attendance records
-- ============================================================
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    attendance_date DATE NOT NULL,
    period INT NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ============================================================
-- 6. INTERNAL MARKS TABLE (Internal Marks Module)
-- One student → Many marks records
-- Uses GENERATED column for auto total calculation
-- ============================================================
CREATE TABLE IF NOT EXISTS internal_marks (
    marks_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    test_name VARCHAR(50) NOT NULL,
    assignment_marks DECIMAL(5,2) DEFAULT 0,
    quiz_marks DECIMAL(5,2) DEFAULT 0,
    internal_exam_marks DECIMAL(5,2) DEFAULT 0,
    total_marks DECIMAL(5,2) GENERATED ALWAYS AS (assignment_marks + quiz_marks + internal_exam_marks) STORED,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ============================================================
-- 7. TIMETABLE TABLE (Timetable Management Module)
-- ============================================================
CREATE TABLE IF NOT EXISTS timetable (
    timetable_id INT AUTO_INCREMENT PRIMARY KEY,
    day_name ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL,
    time_slot VARCHAR(20) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    faculty_name VARCHAR(100) NOT NULL,
    classroom VARCHAR(20) NOT NULL,
    section VARCHAR(10) NOT NULL,
    semester INT NOT NULL
);

-- ============================================================
-- 8. ASSIGNMENTS TABLE (Assignment Tracking Module)
-- One student → Many assignments
-- ============================================================
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('Pending', 'Submitted', 'Late') DEFAULT 'Pending',
    marks_awarded DECIMAL(5,2),
    feedback TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ============================================================
-- 9. PROJECT SUBMISSIONS TABLE (Project Submission Module)
-- One student → Many project submissions
-- ============================================================
CREATE TABLE IF NOT EXISTS project_submissions (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    project_title VARCHAR(200) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    submission_date DATE,
    status ENUM('Pending', 'Submitted', 'Approved', 'Rejected') DEFAULT 'Pending',
    guide_name VARCHAR(100) NOT NULL,
    remarks TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Default admin user (password: admin123)
-- The hash below is generated by Werkzeug's generate_password_hash('admin123')
-- We use a placeholder; init_db.py generates the real hash at runtime.

-- Sample Subjects
INSERT IGNORE INTO subjects (subject_name, subject_code, department, semester, credits) VALUES
('Data Structures', 'CS201', 'CSE', 3, 4),
('Database Management Systems', 'CS301', 'CSE', 5, 4),
('Operating Systems', 'CS302', 'CSE', 5, 3),
('Computer Networks', 'CS401', 'CSE', 7, 3),
('Web Technologies', 'CS303', 'CSE', 5, 3),
('Mathematics I', 'MA101', 'CSE', 1, 4),
('Digital Electronics', 'EC201', 'ECE', 3, 3),
('Signal Processing', 'EC301', 'ECE', 5, 4);

-- Sample Faculty
INSERT IGNORE INTO faculty (faculty_name, department, email) VALUES
('Dr. Sharma', 'CSE', 'sharma@college.edu'),
('Prof. Gupta', 'CSE', 'gupta@college.edu'),
('Dr. Patel', 'ECE', 'patel@college.edu'),
('Prof. Reddy', 'CSE', 'reddy@college.edu');