-- Schema for NEU Syllabus Management System
-- 9 tables: users + syllabi (main) + 7 sub-tables

PRAGMA foreign_keys = ON;

-- ============================================
-- 1. Users (Admin accounts)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
);

-- ============================================
-- 2. Syllabi (Main syllabus info)
--    Each text field has _vi and _en variants
-- ============================================
CREATE TABLE IF NOT EXISTS syllabi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE NOT NULL,
    course_title_vi TEXT,
    course_title_en TEXT,
    credits INTEGER DEFAULT 0,
    contact_hours INTEGER DEFAULT 0,
    self_study_hours INTEGER DEFAULT 0,
    training_program TEXT,
    decision_date TEXT,
    decision_number TEXT,
    prerequisite_courses_vi TEXT,
    prerequisite_courses_en TEXT,
    num_prerequisite_courses TEXT DEFAULT 'None',
    description_vi TEXT,
    description_en TEXT,
    clo_assessment_vi TEXT,
    clo_assessment_en TEXT,
    course_requirements_vi TEXT,
    course_requirements_en TEXT,
    adjustment_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. Syllabus Instructors
-- ============================================
CREATE TABLE IF NOT EXISTS syllabus_instructors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    full_name TEXT NOT NULL,
    email TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);

-- ============================================
-- 4. Syllabus Books (textbook / reference)
-- ============================================
CREATE TABLE IF NOT EXISTS syllabus_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    book_type TEXT NOT NULL DEFAULT 'textbook',
    title TEXT NOT NULL,
    author TEXT,
    year TEXT,
    publisher TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);

-- ============================================
-- 5. Syllabus Software
-- ============================================
CREATE TABLE IF NOT EXISTS syllabus_software (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    software_name TEXT NOT NULL,
    description TEXT,
    version TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);

-- ============================================
-- 6. Course Goals (Section 5)
-- ============================================
CREATE TABLE IF NOT EXISTS course_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    goal_code TEXT NOT NULL,
    description TEXT,
    plo TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);

-- ============================================
-- 7. Learning Outcomes (Section 6)
-- ============================================
CREATE TABLE IF NOT EXISTS learning_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    goal TEXT,
    clo_code TEXT NOT NULL,
    clo_description TEXT,
    level TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);

-- ============================================
-- 8. Course Assessments (Section 7)
-- ============================================
CREATE TABLE IF NOT EXISTS course_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    order_num INTEGER DEFAULT 0,
    method TEXT,
    description TEXT,
    time TEXT,
    clo TEXT,
    weight TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);

-- ============================================
-- 9. Teaching Plans (Section 8) - sorted by week
-- ============================================
CREATE TABLE IF NOT EXISTS teaching_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    syllabus_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'VI',
    week INTEGER NOT NULL,
    detail TEXT,
    reference TEXT,
    activities_assessment TEXT,
    clo TEXT,
    FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
);
