from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date

app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------------------------------------------------------
# DATABASE HELPER
# ---------------------------------------------------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()['total']

    cursor.execute("""
        SELECT ROUND(SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)*100.0 / NULLIF(COUNT(*),0), 1) AS avg_att
        FROM attendance
    """)
    row = cursor.fetchone()
    avg_attendance = row['avg_att'] if row['avg_att'] else 0

    cursor.execute("SELECT ROUND(AVG(total_marks),1) AS avg_marks FROM internal_marks")
    row = cursor.fetchone()
    avg_marks = row['avg_marks'] if row['avg_marks'] else 0

    cursor.execute("SELECT COUNT(*) AS cnt FROM assignments WHERE status='Pending'")
    pending_assignments = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM project_submissions WHERE status='Pending'")
    pending_projects = cursor.fetchone()['cnt']

    # Attendance distribution for chart
    cursor.execute("""
        SELECT status, COUNT(*) AS cnt FROM attendance GROUP BY status
    """)
    att_dist = cursor.fetchall()

    # Top 5 recent students
    cursor.execute("SELECT * FROM students ORDER BY student_id DESC LIMIT 5")
    recent_students = cursor.fetchall()

    conn.close()
    return render_template('dashboard.html',
        total_students=total_students, avg_attendance=avg_attendance,
        avg_marks=avg_marks, pending_assignments=pending_assignments,
        pending_projects=pending_projects, att_dist=att_dist,
        recent_students=recent_students)

# ---------------------------------------------------------------------------
# STUDENT MANAGEMENT
# ---------------------------------------------------------------------------
@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO students (roll_number, full_name, department, semester, section, email, phone_number, dob)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (request.form['roll_number'], request.form['full_name'],
                  request.form['department'], request.form['semester'],
                  request.form['section'], request.form.get('email',''),
                  request.form.get('phone_number',''), request.form.get('dob') or None))
            conn.commit()
            flash('Student added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('students'))

    # Search / filter
    search = request.args.get('search', '')
    dept_filter = request.args.get('department', '')
    sem_filter = request.args.get('semester', '')

    query = "SELECT * FROM students WHERE 1=1"
    params = []
    if search:
        query += " AND (roll_number LIKE %s OR full_name LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    if dept_filter:
        query += " AND department = %s"
        params.append(dept_filter)
    if sem_filter:
        query += " AND semester = %s"
        params.append(sem_filter)
    query += " ORDER BY student_id DESC"

    cursor.execute(query, params)
    all_students = cursor.fetchall()

    cursor.execute("SELECT DISTINCT department FROM students ORDER BY department")
    departments = [r['department'] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT semester FROM students ORDER BY semester")
    semesters = [r['semester'] for r in cursor.fetchall()]

    conn.close()
    return render_template('students.html', students=all_students,
        departments=departments, semesters=semesters,
        search=search, dept_filter=dept_filter, sem_filter=sem_filter)

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE students SET roll_number=%s, full_name=%s, department=%s,
                semester=%s, section=%s, email=%s, phone_number=%s, dob=%s
                WHERE student_id=%s
            """, (request.form['roll_number'], request.form['full_name'],
                  request.form['department'], request.form['semester'],
                  request.form['section'], request.form.get('email',''),
                  request.form.get('phone_number',''), request.form.get('dob') or None, id))
            conn.commit()
            flash('Student updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        conn.close()
        return redirect(url_for('students'))

    cursor.execute("SELECT * FROM students WHERE student_id=%s", (id,))
    student = cursor.fetchone()
    conn.close()
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('students'))
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id=%s", (id,))
    conn.commit()
    conn.close()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('students'))

# ---------------------------------------------------------------------------
# ATTENDANCE MANAGEMENT
# ---------------------------------------------------------------------------
@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO attendance (student_id, subject, attendance_date, period, status)
                VALUES (%s,%s,%s,%s,%s)
            """, (request.form['student_id'], request.form['subject'],
                  request.form['attendance_date'], request.form['period'],
                  request.form['status']))
            conn.commit()
            flash('Attendance recorded!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('attendance'))

    # Filters
    subj_filter = request.args.get('subject', '')
    date_filter = request.args.get('date', '')
    query = """SELECT a.*, s.full_name, s.roll_number FROM attendance a
               JOIN students s ON a.student_id = s.student_id WHERE 1=1"""
    params = []
    if subj_filter:
        query += " AND a.subject = %s"; params.append(subj_filter)
    if date_filter:
        query += " AND a.attendance_date = %s"; params.append(date_filter)
    query += " ORDER BY a.attendance_date DESC, a.period"

    cursor.execute(query, params)
    records = cursor.fetchall()

    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()

    # Attendance percentages per student
    cursor.execute("""
        SELECT s.student_id, s.full_name, s.roll_number,
            COUNT(*) AS total, SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present,
            ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) AS percentage
        FROM attendance a JOIN students s ON a.student_id=s.student_id
        GROUP BY s.student_id, s.full_name, s.roll_number ORDER BY percentage
    """)
    att_stats = cursor.fetchall()

    conn.close()
    return render_template('attendance.html', records=records, students=all_students,
        att_stats=att_stats, subj_filter=subj_filter, date_filter=date_filter)

@app.route('/attendance/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_attendance(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE attendance SET student_id=%s, subject=%s, attendance_date=%s, period=%s, status=%s
                WHERE attendance_id=%s
            """, (request.form['student_id'], request.form['subject'],
                  request.form['attendance_date'], request.form['period'],
                  request.form['status'], id))
            conn.commit()
            flash('Attendance updated!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        conn.close()
        return redirect(url_for('attendance'))

    cursor.execute("SELECT * FROM attendance WHERE attendance_id=%s", (id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('edit_attendance.html', record=record, students=all_students)

@app.route('/attendance/delete/<int:id>', methods=['POST'])
@login_required
def delete_attendance(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE attendance_id=%s", (id,))
    conn.commit(); conn.close()
    flash('Attendance record deleted', 'success')
    return redirect(url_for('attendance'))

# ---------------------------------------------------------------------------
# INTERNAL MARKS MANAGEMENT
# ---------------------------------------------------------------------------
@app.route('/marks', methods=['GET', 'POST'])
@login_required
def marks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO internal_marks (student_id, subject, test_name, assignment_marks, quiz_marks, internal_exam_marks)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (request.form['student_id'], request.form['subject'],
                  request.form['test_name'], request.form['assignment_marks'],
                  request.form['quiz_marks'], request.form['internal_exam_marks']))
            conn.commit()
            flash('Marks added!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('marks'))

    subj_filter = request.args.get('subject', '')
    query = """SELECT m.*, s.full_name, s.roll_number FROM internal_marks m
               JOIN students s ON m.student_id=s.student_id WHERE 1=1"""
    params = []
    if subj_filter:
        query += " AND m.subject=%s"; params.append(subj_filter)
    query += " ORDER BY m.marks_id DESC"

    cursor.execute(query, params)
    records = cursor.fetchall()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('marks.html', records=records, students=all_students, subj_filter=subj_filter)

@app.route('/marks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_marks(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE internal_marks SET student_id=%s, subject=%s, test_name=%s,
                assignment_marks=%s, quiz_marks=%s, internal_exam_marks=%s WHERE marks_id=%s
            """, (request.form['student_id'], request.form['subject'],
                  request.form['test_name'], request.form['assignment_marks'],
                  request.form['quiz_marks'], request.form['internal_exam_marks'], id))
            conn.commit()
            flash('Marks updated!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        conn.close()
        return redirect(url_for('marks'))
    cursor.execute("SELECT * FROM internal_marks WHERE marks_id=%s", (id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('edit_marks.html', record=record, students=all_students)

@app.route('/marks/delete/<int:id>', methods=['POST'])
@login_required
def delete_marks(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM internal_marks WHERE marks_id=%s", (id,))
    conn.commit(); conn.close()
    flash('Marks record deleted', 'success')
    return redirect(url_for('marks'))

# ---------------------------------------------------------------------------
# TIMETABLE MANAGEMENT
# ---------------------------------------------------------------------------
@app.route('/timetable', methods=['GET', 'POST'])
@login_required
def timetable():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO timetable (day_name, time_slot, subject, faculty_name, classroom, section, semester)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (request.form['day_name'], request.form['time_slot'],
                  request.form['subject'], request.form['faculty_name'],
                  request.form['classroom'], request.form['section'],
                  request.form['semester']))
            conn.commit()
            flash('Timetable entry added!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('timetable'))

    day_filter = request.args.get('day', '')
    sec_filter = request.args.get('section', '')
    sem_filter = request.args.get('semester', '')

    query = "SELECT * FROM timetable WHERE 1=1"
    params = []
    if day_filter: query += " AND day_name=%s"; params.append(day_filter)
    if sec_filter: query += " AND section=%s"; params.append(sec_filter)
    if sem_filter: query += " AND semester=%s"; params.append(sem_filter)
    query += " ORDER BY FIELD(day_name,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'), time_slot"

    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()
    return render_template('timetable.html', records=records,
        day_filter=day_filter, sec_filter=sec_filter, sem_filter=sem_filter)

@app.route('/timetable/delete/<int:id>', methods=['POST'])
@login_required
def delete_timetable(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timetable WHERE timetable_id=%s", (id,))
    conn.commit(); conn.close()
    flash('Timetable entry deleted', 'success')
    return redirect(url_for('timetable'))

# ---------------------------------------------------------------------------
# ASSIGNMENT TRACKING
# ---------------------------------------------------------------------------
@app.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO assignments (student_id, subject, title, due_date, status, marks_awarded, feedback)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (request.form['student_id'], request.form['subject'],
                  request.form['title'], request.form['due_date'],
                  request.form.get('status', 'Pending'),
                  request.form.get('marks_awarded') or None,
                  request.form.get('feedback', '')))
            conn.commit()
            flash('Assignment added!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('assignments'))

    status_filter = request.args.get('status', '')
    query = """SELECT a.*, s.full_name, s.roll_number FROM assignments a
               JOIN students s ON a.student_id=s.student_id WHERE 1=1"""
    params = []
    if status_filter: query += " AND a.status=%s"; params.append(status_filter)
    query += " ORDER BY a.due_date DESC"

    cursor.execute(query, params)
    records = cursor.fetchall()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('assignments.html', records=records, students=all_students, status_filter=status_filter)

@app.route('/assignments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_assignment(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE assignments SET student_id=%s, subject=%s, title=%s, due_date=%s,
                status=%s, marks_awarded=%s, feedback=%s WHERE assignment_id=%s
            """, (request.form['student_id'], request.form['subject'],
                  request.form['title'], request.form['due_date'],
                  request.form['status'], request.form.get('marks_awarded') or None,
                  request.form.get('feedback',''), id))
            conn.commit()
            flash('Assignment updated!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        conn.close()
        return redirect(url_for('assignments'))
    cursor.execute("SELECT * FROM assignments WHERE assignment_id=%s", (id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('edit_assignment.html', record=record, students=all_students)

@app.route('/assignments/delete/<int:id>', methods=['POST'])
@login_required
def delete_assignment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignments WHERE assignment_id=%s", (id,))
    conn.commit(); conn.close()
    flash('Assignment deleted', 'success')
    return redirect(url_for('assignments'))

# ---------------------------------------------------------------------------
# PROJECT SUBMISSIONS
# ---------------------------------------------------------------------------
@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO project_submissions (student_id, project_title, subject, submission_date, status, guide_name, remarks)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (request.form['student_id'], request.form['project_title'],
                  request.form['subject'], request.form.get('submission_date') or None,
                  request.form.get('status', 'Pending'), request.form['guide_name'],
                  request.form.get('remarks', '')))
            conn.commit()
            flash('Project submission added!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('projects'))

    status_filter = request.args.get('status', '')
    query = """SELECT p.*, s.full_name, s.roll_number FROM project_submissions p
               JOIN students s ON p.student_id=s.student_id WHERE 1=1"""
    params = []
    if status_filter: query += " AND p.status=%s"; params.append(status_filter)
    query += " ORDER BY p.project_id DESC"

    cursor.execute(query, params)
    records = cursor.fetchall()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('projects.html', records=records, students=all_students, status_filter=status_filter)

@app.route('/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE project_submissions SET student_id=%s, project_title=%s, subject=%s,
                submission_date=%s, status=%s, guide_name=%s, remarks=%s WHERE project_id=%s
            """, (request.form['student_id'], request.form['project_title'],
                  request.form['subject'], request.form.get('submission_date') or None,
                  request.form['status'], request.form['guide_name'],
                  request.form.get('remarks',''), id))
            conn.commit()
            flash('Project updated!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        conn.close()
        return redirect(url_for('projects'))
    cursor.execute("SELECT * FROM project_submissions WHERE project_id=%s", (id,))
    record = cursor.fetchone()
    cursor.execute("SELECT * FROM students ORDER BY full_name")
    all_students = cursor.fetchall()
    conn.close()
    return render_template('edit_project.html', record=record, students=all_students)

@app.route('/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM project_submissions WHERE project_id=%s", (id,))
    conn.commit(); conn.close()
    flash('Project submission deleted', 'success')
    return redirect(url_for('projects'))

# ---------------------------------------------------------------------------
# PERFORMANCE ANALYTICS
# ---------------------------------------------------------------------------
@app.route('/analytics')
@login_required
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Per-student attendance %
    cursor.execute("""
        SELECT s.full_name,
            ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/NULLIF(COUNT(*),0),1) AS pct
        FROM attendance a JOIN students s ON a.student_id=s.student_id
        GROUP BY s.student_id, s.full_name ORDER BY pct DESC
    """)
    att_by_student = cursor.fetchall()

    # Subject-wise average marks
    cursor.execute("""
        SELECT subject, ROUND(AVG(total_marks),1) AS avg_total FROM internal_marks
        GROUP BY subject ORDER BY avg_total DESC
    """)
    marks_by_subject = cursor.fetchall()

    # Assignment completion
    cursor.execute("""
        SELECT status, COUNT(*) AS cnt FROM assignments GROUP BY status
    """)
    assign_stats = cursor.fetchall()

    # Project status
    cursor.execute("""
        SELECT status, COUNT(*) AS cnt FROM project_submissions GROUP BY status
    """)
    project_stats = cursor.fetchall()

    conn.close()
    return render_template('analytics.html', att_by_student=att_by_student,
        marks_by_subject=marks_by_subject, assign_stats=assign_stats,
        project_stats=project_stats)

# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)