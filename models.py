import sqlite3
import config


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================
# SYLLABI (main table)
# ============================================

def get_all_syllabi():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM syllabi ORDER BY updated_at DESC"
    ).fetchall()
    db.close()
    return rows


def get_syllabus_by_id(syllabus_id):
    db = get_db()
    row = db.execute("SELECT * FROM syllabi WHERE id = ?", (syllabus_id,)).fetchone()
    db.close()
    return row


def get_syllabus_by_code(course_code):
    db = get_db()
    row = db.execute("SELECT * FROM syllabi WHERE course_code = ?", (course_code,)).fetchone()
    db.close()
    return row


def search_syllabi(query):
    db = get_db()
    q = f"%{query}%"
    rows = db.execute(
        """SELECT * FROM syllabi
           WHERE course_code LIKE ?
              OR course_title_vi LIKE ?
              OR course_title_en LIKE ?
              OR training_program LIKE ?
              OR description_vi LIKE ?
              OR description_en LIKE ?
           ORDER BY updated_at DESC""",
        (q, q, q, q, q, q)
    ).fetchall()
    db.close()
    return rows


def create_syllabus(data):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO syllabi (
            course_code, course_title_vi, course_title_en,
            credits, contact_hours, self_study_hours,
            training_program, decision_date, decision_number,
            prerequisite_courses_vi, prerequisite_courses_en,
            num_prerequisite_courses,
            description_vi, description_en,
            clo_assessment_vi, clo_assessment_en,
            course_requirements_vi, course_requirements_en,
            adjustment_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data['course_code'], data.get('course_title_vi', ''), data.get('course_title_en', ''),
            data.get('credits', 0), data.get('contact_hours', 0), data.get('self_study_hours', 0),
            data.get('training_program', ''), data.get('decision_date', ''), data.get('decision_number', ''),
            data.get('prerequisite_courses_vi', ''), data.get('prerequisite_courses_en', ''),
            data.get('num_prerequisite_courses', 'None'),
            data.get('description_vi', ''), data.get('description_en', ''),
            data.get('clo_assessment_vi', ''), data.get('clo_assessment_en', ''),
            data.get('course_requirements_vi', ''), data.get('course_requirements_en', ''),
            data.get('adjustment_time', '')
        )
    )
    db.commit()
    syllabus_id = cursor.lastrowid
    db.close()
    return syllabus_id


def update_syllabus(syllabus_id, data):
    db = get_db()
    db.execute(
        """UPDATE syllabi SET
            course_code = ?, course_title_vi = ?, course_title_en = ?,
            credits = ?, contact_hours = ?, self_study_hours = ?,
            training_program = ?, decision_date = ?, decision_number = ?,
            prerequisite_courses_vi = ?, prerequisite_courses_en = ?,
            num_prerequisite_courses = ?,
            description_vi = ?, description_en = ?,
            clo_assessment_vi = ?, clo_assessment_en = ?,
            course_requirements_vi = ?, course_requirements_en = ?,
            adjustment_time = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?""",
        (
            data['course_code'], data.get('course_title_vi', ''), data.get('course_title_en', ''),
            data.get('credits', 0), data.get('contact_hours', 0), data.get('self_study_hours', 0),
            data.get('training_program', ''), data.get('decision_date', ''), data.get('decision_number', ''),
            data.get('prerequisite_courses_vi', ''), data.get('prerequisite_courses_en', ''),
            data.get('num_prerequisite_courses', 'None'),
            data.get('description_vi', ''), data.get('description_en', ''),
            data.get('clo_assessment_vi', ''), data.get('clo_assessment_en', ''),
            data.get('course_requirements_vi', ''), data.get('course_requirements_en', ''),
            data.get('adjustment_time', ''),
            syllabus_id
        )
    )
    db.commit()
    db.close()


def delete_syllabus(syllabus_id):
    db = get_db()
    db.execute("DELETE FROM syllabi WHERE id = ?", (syllabus_id,))
    db.commit()
    db.close()


# ============================================
# USERS
# ============================================

def get_user_by_username(username):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return row


# ============================================
# GENERIC SUB-TABLE CRUD
# ============================================

def get_sub_items(table, syllabus_id, language=None, order_by=None):
    """Get items from a sub-table, optionally filtered by language."""
    db = get_db()
    allowed_tables = {
        'syllabus_instructors', 'syllabus_books', 'syllabus_software',
        'course_goals', 'learning_outcomes', 'course_assessments', 'teaching_plans'
    }
    if table not in allowed_tables:
        db.close()
        return []

    sql = f"SELECT * FROM {table} WHERE syllabus_id = ?"
    params = [syllabus_id]

    if language:
        sql += " AND language = ?"
        params.append(language)

    if order_by:
        allowed_order = {'week', 'order_num', 'goal_code', 'clo_code', 'id'}
        if order_by in allowed_order:
            sql += f" ORDER BY {order_by}"
    else:
        sql += " ORDER BY id"

    rows = db.execute(sql, params).fetchall()
    db.close()
    return rows


def get_sub_item_by_id(table, item_id):
    """Get a single item from a sub-table by its ID."""
    db = get_db()
    allowed_tables = {
        'syllabus_instructors', 'syllabus_books', 'syllabus_software',
        'course_goals', 'learning_outcomes', 'course_assessments', 'teaching_plans'
    }
    if table not in allowed_tables:
        db.close()
        return None
    row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    db.close()
    return row


def delete_sub_item(table, item_id):
    """Delete a single item from a sub-table."""
    db = get_db()
    allowed_tables = {
        'syllabus_instructors', 'syllabus_books', 'syllabus_software',
        'course_goals', 'learning_outcomes', 'course_assessments', 'teaching_plans'
    }
    if table not in allowed_tables:
        db.close()
        return
    db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
    db.commit()
    db.close()


# ============================================
# INSTRUCTORS
# ============================================

def create_instructor(syllabus_id, language, full_name, email):
    db = get_db()
    db.execute(
        "INSERT INTO syllabus_instructors (syllabus_id, language, full_name, email) VALUES (?, ?, ?, ?)",
        (syllabus_id, language, full_name, email)
    )
    db.commit()
    db.close()


def update_instructor(item_id, full_name, email):
    db = get_db()
    db.execute(
        "UPDATE syllabus_instructors SET full_name = ?, email = ? WHERE id = ?",
        (full_name, email, item_id)
    )
    db.commit()
    db.close()


# ============================================
# BOOKS
# ============================================

def create_book(syllabus_id, language, book_type, title, author, year, publisher):
    db = get_db()
    db.execute(
        """INSERT INTO syllabus_books
           (syllabus_id, language, book_type, title, author, year, publisher)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (syllabus_id, language, book_type, title, author, year, publisher)
    )
    db.commit()
    db.close()


def update_book(item_id, book_type, title, author, year, publisher):
    db = get_db()
    db.execute(
        """UPDATE syllabus_books
           SET book_type = ?, title = ?, author = ?, year = ?, publisher = ?
           WHERE id = ?""",
        (book_type, title, author, year, publisher, item_id)
    )
    db.commit()
    db.close()


# ============================================
# SOFTWARE
# ============================================

def create_software(syllabus_id, language, software_name, description, version):
    db = get_db()
    db.execute(
        """INSERT INTO syllabus_software
           (syllabus_id, language, software_name, description, version)
           VALUES (?, ?, ?, ?, ?)""",
        (syllabus_id, language, software_name, description, version)
    )
    db.commit()
    db.close()


def update_software(item_id, software_name, description, version):
    db = get_db()
    db.execute(
        """UPDATE syllabus_software
           SET software_name = ?, description = ?, version = ?
           WHERE id = ?""",
        (software_name, description, version, item_id)
    )
    db.commit()
    db.close()


# ============================================
# COURSE GOALS
# ============================================

def create_goal(syllabus_id, language, goal_code, description, plo):
    db = get_db()
    db.execute(
        """INSERT INTO course_goals
           (syllabus_id, language, goal_code, description, plo)
           VALUES (?, ?, ?, ?, ?)""",
        (syllabus_id, language, goal_code, description, plo)
    )
    db.commit()
    db.close()


def update_goal(item_id, goal_code, description, plo):
    db = get_db()
    db.execute(
        """UPDATE course_goals
           SET goal_code = ?, description = ?, plo = ?
           WHERE id = ?""",
        (goal_code, description, plo, item_id)
    )
    db.commit()
    db.close()


# ============================================
# LEARNING OUTCOMES
# ============================================

def create_outcome(syllabus_id, language, goal, clo_code, clo_description, level):
    db = get_db()
    db.execute(
        """INSERT INTO learning_outcomes
           (syllabus_id, language, goal, clo_code, clo_description, level)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (syllabus_id, language, goal, clo_code, clo_description, level)
    )
    db.commit()
    db.close()


def update_outcome(item_id, goal, clo_code, clo_description, level):
    db = get_db()
    db.execute(
        """UPDATE learning_outcomes
           SET goal = ?, clo_code = ?, clo_description = ?, level = ?
           WHERE id = ?""",
        (goal, clo_code, clo_description, level, item_id)
    )
    db.commit()
    db.close()


# ============================================
# COURSE ASSESSMENTS
# ============================================

def create_assessment(syllabus_id, language, order_num, method, description, time, clo, weight):
    db = get_db()
    db.execute(
        """INSERT INTO course_assessments
           (syllabus_id, language, order_num, method, description, time, clo, weight)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (syllabus_id, language, order_num, method, description, time, clo, weight)
    )
    db.commit()
    db.close()


def update_assessment(item_id, order_num, method, description, time, clo, weight):
    db = get_db()
    db.execute(
        """UPDATE course_assessments
           SET order_num = ?, method = ?, description = ?, time = ?, clo = ?, weight = ?
           WHERE id = ?""",
        (order_num, method, description, time, clo, weight, item_id)
    )
    db.commit()
    db.close()


# ============================================
# TEACHING PLANS
# ============================================

def create_teaching_plan(syllabus_id, language, week, detail, reference, activities_assessment, clo):
    db = get_db()
    db.execute(
        """INSERT INTO teaching_plans
           (syllabus_id, language, week, detail, reference, activities_assessment, clo)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (syllabus_id, language, week, detail, reference, activities_assessment, clo)
    )
    db.commit()
    db.close()


def update_teaching_plan(item_id, week, detail, reference, activities_assessment, clo):
    db = get_db()
    db.execute(
        """UPDATE teaching_plans
           SET week = ?, detail = ?, reference = ?, activities_assessment = ?, clo = ?
           WHERE id = ?""",
        (week, detail, reference, activities_assessment, clo, item_id)
    )
    db.commit()
    db.close()
