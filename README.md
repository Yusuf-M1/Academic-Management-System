# Academic Management System

A comprehensive web-based academic data management system built with Python, Flask, and MySQL. Designed as a college DBMS mini project demonstrating proper relational database design, CRUD operations, form handling, backend integration, and performance analytics.

---

## Table of Contents

1. [Project Description](#1-project-description)
2. [Tech Stack](#2-tech-stack)
3. [Folder Structure](#3-folder-structure)
4. [Installation & Setup](#4-installation--setup)
5. [Module Functionality](#5-module-functionality)
6. [Database Design](#6-database-design)
7. [Flask Route Structure](#7-flask-route-structure)
8. [Page Structure](#8-page-structure)
9. [User Flow](#9-user-flow)
10. [System Working Explanation](#10-system-working-explanation)
11. [Assumptions](#11-assumptions)
12. [Future Enhancements](#12-future-enhancements)
13. [Constraints & Limitations](#13-constraints--limitations)
14. [Why This Is a Good DBMS Mini Project](#14-why-this-is-a-good-dbms-mini-project)

---

## 1. Project Description

The **Academic Management System (AMS)** is a centralized web application that replaces manual registers and scattered spreadsheets with a database-driven system for managing academic records. It provides a clean browser-based interface for faculty and administrators to:

- Manage student profiles (CRUD)
- Track daily attendance with automatic percentage calculation
- Record and analyze internal marks across subjects and tests
- Manage class timetables
- Track assignment submissions and deadlines
- Monitor project submissions and approvals
- View comprehensive performance analytics with interactive charts

The system demonstrates core DBMS concepts including normalization (up to 3NF), referential integrity via foreign keys, cascading deletes, CRUD operations, aggregate queries, and generated columns.

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.x, Flask 3.0 |
| Database | MySQL 8.x |
| DB Connector | mysql-connector-python 8.2 |
| Frontend | HTML5, CSS3, JavaScript (ES6) |
| Charting | Chart.js 4.4 (CDN) |
| Icons | Bootstrap Icons (CDN) |
| Typography | Inter (Google Fonts CDN) |
| Password Hashing | Werkzeug 3.0 |

---

## 3. Folder Structure

```
Academic Management System/
├── app.py                    # Flask backend — all routes and logic
├── config.py                 # Database configuration
├── init_db.py                # Database initialization script
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation (this file)
├── database/
│   └── schema.sql            # Complete SQL schema with seed data
├── static/
│   ├── css/
│   │   └── style.css         # Premium custom stylesheet
│   └── js/
│       └── main.js           # Client-side JavaScript
└── templates/
    ├── base.html             # Master layout with sidebar navigation
    ├── login.html            # Authentication page
    ├── dashboard.html        # Analytics dashboard with charts
    ├── students.html         # Student CRUD with search/filter
    ├── edit_student.html     # Edit student form
    ├── attendance.html       # Attendance management
    ├── edit_attendance.html  # Edit attendance record
    ├── marks.html            # Internal marks management
    ├── edit_marks.html       # Edit marks entry
    ├── timetable.html        # Timetable management
    ├── assignments.html      # Assignment tracking
    ├── edit_assignment.html  # Edit assignment
    ├── projects.html         # Project submission tracking
    ├── edit_project.html     # Edit project submission
    └── analytics.html        # Performance analytics with charts
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Steps

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Update MySQL credentials in config.py
#    Edit MYSQL_USER and MYSQL_PASSWORD to match your MySQL setup

# 3. Initialize the database (creates tables and seeds data)
python init_db.py

# 4. Run the application
python app.py

# 5. Open in browser
#    Navigate to http://127.0.0.1:5000
#    Login with: admin / admin123
```

---

## 5. Module Functionality

### 5.1 Login / Authentication
- Admin login with hardcoded credentials (admin/admin123)
- Session-based authentication using Flask sessions
- `login_required` decorator protects all routes
- Logout clears session and redirects to login

### 5.2 Dashboard
- **Total Students**: Count from students table
- **Average Attendance**: Calculated as (Present count / Total count) × 100
- **Average Marks**: Mean of total_marks from internal_marks table
- **Pending Assignments**: Count where status = 'Pending'
- **Pending Projects**: Count where status = 'Pending'
- **Attendance Distribution**: Doughnut chart (Present/Absent/Late)
- **Recent Students**: Table of last 5 added students

### 5.3 Student Management
- **Add**: Form with 8 fields — roll number, name, department, semester, section, email, phone, DOB
- **View**: Table with all student records
- **Edit**: Pre-filled form for updating any field
- **Delete**: With JavaScript confirmation dialog
- **Search**: By name or roll number (real-time + server-side)
- **Filter**: By department and semester via dropdowns

### 5.4 Attendance Management
- **Mark**: Select student, enter subject, date, period, status (Present/Absent/Late)
- **View**: Table of all records with student name joined
- **Edit**: Update any attendance record
- **Delete**: Remove incorrect entries
- **Filter**: By subject and date
- **Statistics**: Auto-calculated percentage per student
- **Highlighting**: Students below 75% shown in red badge

### 5.5 Internal Marks Management
- **Add**: Student, subject, test name, assignment marks, quiz marks, internal exam marks
- **Auto-calculation**: Total marks computed by MySQL GENERATED column
- **View**: Table with student name, all component scores, and total
- **Edit/Delete**: Full CRUD support
- **Filter**: By subject

### 5.6 Timetable Management
- **Add**: Day, time slot, subject, faculty, classroom, section, semester
- **View**: Ordered by day (Mon→Sat) then time slot
- **Filter**: By day, section, and semester
- **Delete**: Remove entries

### 5.7 Assignment Tracking
- **Create**: Student, subject, title, due date, status, marks, feedback
- **Status Options**: Pending (yellow), Submitted (green), Late (red)
- **View**: Table with color-coded status badges
- **Edit**: Update status, award marks, add feedback
- **Filter**: By status
- **Delete**: Remove assignments

### 5.8 Project Submission Tracking
- **Add**: Student, project title, subject, submission date, guide name, status, remarks
- **Status Options**: Pending, Submitted, Approved, Rejected
- **View**: Table with status badges
- **Edit/Delete**: Full CRUD
- **Filter**: By status

### 5.9 Performance Analytics
- **Attendance % by Student**: Bar chart (red bars for <75%)
- **Average Marks by Subject**: Bar chart identifying strong/weak subjects
- **Assignment Completion**: Doughnut chart showing status distribution
- **Project Status**: Doughnut chart showing submission progress
- **Student Attendance Table**: Detailed list with Good/Low badges
- **Subject Strength Table**: Strong/Average/Weak classification

---

## 6. Database Design

### Entity-Relationship Summary

```
students (1) ──── (N) attendance
students (1) ──── (N) internal_marks
students (1) ──── (N) assignments
students (1) ──── (N) project_submissions
```

### Table Structures

#### `users` — Authentication
| Column | Type | Constraints |
|--------|------|------------|
| id | INT AUTO_INCREMENT | PRIMARY KEY |
| username | VARCHAR(50) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | ENUM('admin','faculty') | DEFAULT 'faculty' |

#### `students` — Student Records
| Column | Type | Constraints |
|--------|------|------------|
| student_id | INT AUTO_INCREMENT | PRIMARY KEY |
| roll_number | VARCHAR(20) | UNIQUE, NOT NULL |
| full_name | VARCHAR(100) | NOT NULL |
| department | VARCHAR(50) | NOT NULL |
| semester | INT | NOT NULL |
| section | VARCHAR(10) | NOT NULL |
| email | VARCHAR(100) | UNIQUE |
| phone_number | VARCHAR(15) | |
| dob | DATE | |

#### `attendance` — Attendance Records
| Column | Type | Constraints |
|--------|------|------------|
| attendance_id | INT AUTO_INCREMENT | PRIMARY KEY |
| student_id | INT | FK → students, ON DELETE CASCADE |
| subject | VARCHAR(100) | NOT NULL |
| attendance_date | DATE | NOT NULL |
| period | INT | NOT NULL |
| status | ENUM('Present','Absent','Late') | NOT NULL |

#### `internal_marks` — Marks Records
| Column | Type | Constraints |
|--------|------|------------|
| marks_id | INT AUTO_INCREMENT | PRIMARY KEY |
| student_id | INT | FK → students, ON DELETE CASCADE |
| subject | VARCHAR(100) | NOT NULL |
| test_name | VARCHAR(50) | NOT NULL |
| assignment_marks | DECIMAL(5,2) | DEFAULT 0 |
| quiz_marks | DECIMAL(5,2) | DEFAULT 0 |
| internal_exam_marks | DECIMAL(5,2) | DEFAULT 0 |
| total_marks | DECIMAL(5,2) | GENERATED (auto-sum) |

#### `timetable` — Class Schedule
| Column | Type | Constraints |
|--------|------|------------|
| timetable_id | INT AUTO_INCREMENT | PRIMARY KEY |
| day_name | ENUM(Mon-Sat) | NOT NULL |
| time_slot | VARCHAR(20) | NOT NULL |
| subject | VARCHAR(100) | NOT NULL |
| faculty_name | VARCHAR(100) | NOT NULL |
| classroom | VARCHAR(20) | NOT NULL |
| section | VARCHAR(10) | NOT NULL |
| semester | INT | NOT NULL |

#### `assignments` — Assignment Records
| Column | Type | Constraints |
|--------|------|------------|
| assignment_id | INT AUTO_INCREMENT | PRIMARY KEY |
| student_id | INT | FK → students, ON DELETE CASCADE |
| subject | VARCHAR(100) | NOT NULL |
| title | VARCHAR(200) | NOT NULL |
| due_date | DATE | NOT NULL |
| status | ENUM('Pending','Submitted','Late') | DEFAULT 'Pending' |
| marks_awarded | DECIMAL(5,2) | |
| feedback | TEXT | |

#### `project_submissions` — Project Records
| Column | Type | Constraints |
|--------|------|------------|
| project_id | INT AUTO_INCREMENT | PRIMARY KEY |
| student_id | INT | FK → students, ON DELETE CASCADE |
| project_title | VARCHAR(200) | NOT NULL |
| subject | VARCHAR(100) | NOT NULL |
| submission_date | DATE | |
| status | ENUM('Pending','Submitted','Approved','Rejected') | DEFAULT 'Pending' |
| guide_name | VARCHAR(100) | NOT NULL |
| remarks | TEXT | |

### Normalization
- **1NF**: All tables have atomic values, no repeating groups
- **2NF**: All non-key attributes fully depend on the primary key
- **3NF**: No transitive dependencies; total_marks is a generated column (derived from other columns in the same row)

### Referential Integrity
- All child tables reference `students(student_id)` via FOREIGN KEY
- `ON DELETE CASCADE` ensures deleting a student removes all related records

---

## 7. Flask Route Structure

| Route | Method | Function | Module |
|-------|--------|----------|--------|
| `/`, `/login` | GET, POST | `login()` | Auth |
| `/logout` | GET | `logout()` | Auth |
| `/dashboard` | GET | `dashboard()` | Dashboard |
| `/students` | GET, POST | `students()` | Students |
| `/edit_student/<id>` | GET, POST | `edit_student()` | Students |
| `/delete_student/<id>` | POST | `delete_student()` | Students |
| `/attendance` | GET, POST | `attendance()` | Attendance |
| `/attendance/edit/<id>` | GET, POST | `edit_attendance()` | Attendance |
| `/attendance/delete/<id>` | POST | `delete_attendance()` | Attendance |
| `/marks` | GET, POST | `marks()` | Marks |
| `/marks/edit/<id>` | GET, POST | `edit_marks()` | Marks |
| `/marks/delete/<id>` | POST | `delete_marks()` | Marks |
| `/timetable` | GET, POST | `timetable()` | Timetable |
| `/timetable/delete/<id>` | POST | `delete_timetable()` | Timetable |
| `/assignments` | GET, POST | `assignments()` | Assignments |
| `/assignments/edit/<id>` | GET, POST | `edit_assignment()` | Assignments |
| `/assignments/delete/<id>` | POST | `delete_assignment()` | Assignments |
| `/projects` | GET, POST | `projects()` | Projects |
| `/projects/edit/<id>` | GET, POST | `edit_project()` | Projects |
| `/projects/delete/<id>` | POST | `delete_project()` | Projects |
| `/analytics` | GET | `analytics()` | Analytics |

---

## 8. Page Structure

| Page | Purpose | Key Elements |
|------|---------|-------------|
| login.html | Authentication | Glassmorphism card, gradient background |
| dashboard.html | Overview | 5 stat cards, doughnut chart, recent students table |
| students.html | Student CRUD | Add form (8 fields), search bar, filter dropdowns, data table |
| attendance.html | Attendance CRUD | Mark form, filters, stats table, records table |
| marks.html | Marks CRUD | Add form (6 fields), filter, table with auto-totals |
| timetable.html | Schedule mgmt | Add form (7 fields), day/section/sem filters, ordered table |
| assignments.html | Assignment tracking | Create form, status filter, status badges, table |
| projects.html | Project tracking | Add form, status filter, status badges, table |
| analytics.html | Performance charts | 4 Chart.js charts, 2 detail tables |

---

## 9. User Flow

```
1. User opens browser → http://127.0.0.1:5000
2. Login page displayed → User enters admin/admin123
3. Flask validates credentials → Creates session
4. Redirected to Dashboard → Flask queries MySQL for stats
5. User navigates via sidebar → Each link loads a module page
6. User fills a form → Browser sends POST to Flask
7. Flask connects to MySQL → Executes INSERT/UPDATE/DELETE
8. Flask commits changes → Redirects with flash message
9. User views data tables → Flask SELECTs from MySQL, renders template
10. User visits Analytics → Flask runs aggregate queries, sends to Chart.js
11. User logs out → Session cleared, redirected to login
```

---

## 10. System Working Explanation

### Frontend → Backend → Database Flow

1. **HTML Templates** (Jinja2) render the user interface with forms, tables, and navigation
2. **CSS** provides premium styling with a dark sidebar, card-based layout, and responsive design
3. **JavaScript** handles client-side interactions: sidebar toggle, alert dismissal, delete confirmation, and Chart.js initialization
4. **Flask** receives HTTP requests, validates sessions, processes form data, and connects to MySQL
5. **MySQL** stores all data in normalized tables with foreign key relationships
6. **Flask** fetches results from MySQL and passes them to Jinja2 templates as context variables
7. **Templates** iterate over data to render dynamic tables, charts, and summary cards

### Key DBMS Concepts Demonstrated

| Concept | Where Used |
|---------|-----------|
| CREATE, INSERT, SELECT, UPDATE, DELETE | All CRUD routes |
| FOREIGN KEY | attendance, marks, assignments, projects → students |
| ON DELETE CASCADE | Deleting a student cascades to all related records |
| GENERATED COLUMN | total_marks auto-calculated in internal_marks |
| Aggregate Functions (COUNT, AVG, SUM, ROUND) | Dashboard and Analytics |
| GROUP BY | Analytics charts and attendance statistics |
| JOIN | All list views join with students table |
| ENUM | Status fields, day names |
| UNIQUE constraints | roll_number, email, username |
| Parameterized queries | All SQL uses %s placeholders (prevents SQL injection) |

---

## 11. Assumptions

1. Single admin user (admin/admin123) for simplicity
2. MySQL server is running locally on default port 3306
3. All users access from modern browsers (Chrome, Firefox, Edge)
4. Subject names are entered as text (not normalized FK references) for simplicity
5. One attendance record per student per subject per period per date
6. Marks are additive (assignment + quiz + internal exam = total)
7. The system is intended for single-institution use

---

## 12. Future Enhancements

1. **Multi-user authentication** with registration and role-based access (admin, faculty, student)
2. **Student portal** for view-only access to their own records
3. **PDF report generation** for attendance and marks sheets
4. **Email notifications** for low attendance and pending assignments
5. **Bulk attendance marking** for entire class at once
6. **File upload** for assignment submissions
7. **Export to Excel/CSV** for all data tables
8. **REST API** for mobile app integration
9. **Dark mode toggle** for user preference
10. **Audit logging** to track who made changes and when

---

## 13. Constraints & Limitations

1. No HTTPS — runs on Flask development server (not production-ready)
2. Single-user system — no concurrent access handling
3. No input sanitization beyond parameterized queries
4. No pagination — large datasets may slow down page rendering
5. No file/image uploads
6. Timetable does not handle time conflicts automatically
7. No email verification for student records
8. Charts require internet connection (CDN-loaded Chart.js)

---

## 14. Why This Is a Good DBMS Mini Project

| Criteria | How AMS Fulfills It |
|----------|-------------------|
| **Relational Design** | 9 tables with proper PK/FK, 1:N relationships, CASCADE rules |
| **Normalization** | Up to 3NF — no redundancy, atomic values, no transitive deps |
| **CRUD Operations** | Full Create, Read, Update, Delete on 6 entities |
| **Aggregate Queries** | COUNT, AVG, SUM, ROUND, GROUP BY for analytics |
| **JOINs** | Every list view joins child tables with students |
| **Generated Columns** | total_marks auto-computed by MySQL |
| **Data Integrity** | UNIQUE, NOT NULL, ENUM, FK constraints |
| **Web Integration** | Flask + MySQL + Jinja2 + JavaScript |
| **UI/UX Quality** | Professional design with charts, badges, animations |
| **Real-world Relevance** | Solves actual academic record management problems |
| **Scalable Scope** | 10 modules — enough complexity for a comprehensive project |

---

## Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |

---

*Built with Python, Flask, MySQL, HTML, CSS, and JavaScript.*
