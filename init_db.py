"""Initialize the database and seed sample data."""
import sqlite3
import os
from werkzeug.security import generate_password_hash
import config


def init_db():
    """Create all tables from schema.sql."""
    if os.path.exists(config.DATABASE):
        os.remove(config.DATABASE)

    conn = sqlite3.connect(config.DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")

    with open(os.path.join(config.BASE_DIR, 'schema.sql'), 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()
    print("[OK] Database created with all tables.")


def seed_admin():
    """Seed default admin account: admin / admin123"""
    conn = sqlite3.connect(config.DATABASE)
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        ('admin', generate_password_hash('admin123'), 'admin')
    )
    conn.commit()
    conn.close()
    print("[OK] Admin user seeded (admin / admin123).")


def seed_sample_data():
    """Seed 2 sample syllabi with full sub-table data in both VI and EN."""
    conn = sqlite3.connect(config.DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")

    # =============================================
    # Syllabus 1: Nhập môn CNTT
    # =============================================
    conn.execute("""
        INSERT INTO syllabi (
            course_code, course_title_vi, course_title_en,
            credits, contact_hours, self_study_hours,
            training_program, decision_date, decision_number,
            prerequisite_courses_vi, prerequisite_courses_en,
            num_prerequisite_courses,
            description_vi, description_en,
            clo_assessment_vi, clo_assessment_en,
            course_requirements_vi, course_requirements_en,
            adjustment_time
        ) VALUES (
            'EP17.CNTT1116',
            'Nhập môn Công nghệ thông tin',
            'Introduction To Information Technology',
            3, 25, 60,
            'EP17', '2024-01-15', 'QĐ-2024/001',
            'Không', 'None',
            'None',
            'Học phần cung cấp cho sinh viên những kiến thức cơ bản về công nghệ thông tin, bao gồm: kiến trúc máy tính, hệ điều hành, mạng máy tính, cơ sở dữ liệu, lập trình cơ bản và các ứng dụng CNTT trong kinh tế.',
            'This course provides students with fundamental knowledge of information technology, including: computer architecture, operating systems, computer networks, databases, basic programming and IT applications in economics.',
            'Đánh giá CLO dựa trên các bài kiểm tra, bài tập nhóm và thi cuối kỳ. Mỗi CLO được đánh giá thông qua ít nhất 2 phương pháp đánh giá khác nhau.',
            'CLO assessment is based on quizzes, group assignments, and final exam. Each CLO is assessed through at least 2 different assessment methods.',
            'Sinh viên cần tham dự ít nhất 80% số buổi học. Hoàn thành đầy đủ bài tập và bài kiểm tra theo lịch. Tuân thủ quy chế thi và kiểm tra của trường.',
            'Students must attend at least 80% of classes. Complete all assignments and tests on schedule. Comply with university examination regulations.',
            '2024-06-01'
        )
    """)
    s1_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Instructors
    for lang, name, email in [
        ('VI', 'Nguyễn Văn A', 'nguyenvana@neu.edu.vn'),
        ('VI', 'Trần Thị B', 'tranthib@neu.edu.vn'),
        ('EN', 'Nguyen Van A', 'nguyenvana@neu.edu.vn'),
        ('EN', 'Tran Thi B', 'tranthib@neu.edu.vn'),
    ]:
        conn.execute(
            "INSERT INTO syllabus_instructors (syllabus_id, language, full_name, email) VALUES (?,?,?,?)",
            (s1_id, lang, name, email)
        )

    # Books
    for lang, btype, title, author, year, publisher in [
        ('VI', 'textbook', 'Nhập môn Công nghệ thông tin', 'Nguyễn Văn A', '2023', 'NXB ĐHKTQD'),
        ('VI', 'reference', 'Tin học cơ sở', 'Trần Văn C', '2022', 'NXB Giáo dục'),
        ('EN', 'textbook', 'Introduction to Information Technology', 'John Smith', '2023', 'Pearson'),
        ('EN', 'reference', 'Computer Science: An Overview', 'Glenn Brookshear', '2022', 'Pearson'),
    ]:
        conn.execute(
            "INSERT INTO syllabus_books (syllabus_id, language, book_type, title, author, year, publisher) VALUES (?,?,?,?,?,?,?)",
            (s1_id, lang, btype, title, author, year, publisher)
        )

    # Software
    for lang, name, desc, ver in [
        ('VI', 'Microsoft Office', 'Bộ công cụ văn phòng', '2021'),
        ('VI', 'Python', 'Ngôn ngữ lập trình', '3.11'),
        ('EN', 'Microsoft Office', 'Office productivity suite', '2021'),
        ('EN', 'Python', 'Programming language', '3.11'),
    ]:
        conn.execute(
            "INSERT INTO syllabus_software (syllabus_id, language, software_name, description, version) VALUES (?,?,?,?,?)",
            (s1_id, lang, name, desc, ver)
        )

    # Course Goals
    for lang, code, desc, plo in [
        ('VI', 'G1', 'Hiểu các khái niệm cơ bản về CNTT và vai trò của CNTT trong kinh tế', 'PLO1'),
        ('VI', 'G2', 'Sử dụng thành thạo các công cụ CNTT cơ bản phục vụ học tập và công việc', 'PLO2'),
        ('VI', 'G3', 'Có khả năng tư duy logic và giải quyết vấn đề bằng lập trình cơ bản', 'PLO3'),
        ('EN', 'G1', 'Understand basic IT concepts and the role of IT in economics', 'PLO1'),
        ('EN', 'G2', 'Proficiently use basic IT tools for study and work', 'PLO2'),
        ('EN', 'G3', 'Ability to think logically and solve problems using basic programming', 'PLO3'),
    ]:
        conn.execute(
            "INSERT INTO course_goals (syllabus_id, language, goal_code, description, plo) VALUES (?,?,?,?,?)",
            (s1_id, lang, code, desc, plo)
        )

    # Learning Outcomes
    for lang, goal, clo, desc, level in [
        ('VI', 'G1', 'CLO1', 'Trình bày được các khái niệm cơ bản về CNTT', 'TU3'),
        ('VI', 'G1', 'CLO2', 'Phân tích được vai trò của CNTT trong các lĩnh vực kinh tế', 'ITU3'),
        ('VI', 'G2', 'CLO3', 'Sử dụng thành thạo Microsoft Office', 'TU3'),
        ('VI', 'G3', 'CLO4', 'Viết được chương trình Python đơn giản', 'ITU3'),
        ('EN', 'G1', 'CLO1', 'Describe basic concepts of information technology', 'TU3'),
        ('EN', 'G1', 'CLO2', 'Analyze the role of IT in economic fields', 'ITU3'),
        ('EN', 'G2', 'CLO3', 'Proficiently use Microsoft Office', 'TU3'),
        ('EN', 'G3', 'CLO4', 'Write simple Python programs', 'ITU3'),
    ]:
        conn.execute(
            "INSERT INTO learning_outcomes (syllabus_id, language, goal, clo_code, clo_description, level) VALUES (?,?,?,?,?,?)",
            (s1_id, lang, goal, clo, desc, level)
        )

    # Course Assessments
    for lang, order, method, desc, time_val, clo, weight in [
        ('VI', 1, 'Tham gia lớp học', 'Điểm danh, phát biểu', '15 buổi', 'CLO1, CLO2', '10%'),
        ('VI', 2, 'Bài tập', 'Bài tập cá nhân và nhóm', '4 tuần', 'CLO2, CLO3', '20%'),
        ('VI', 3, 'Kiểm tra giữa kỳ', 'Trắc nghiệm + tự luận', '60 phút', 'CLO1, CLO2, CLO3', '20%'),
        ('VI', 4, 'Thi cuối kỳ', 'Trắc nghiệm + thực hành', '90 phút', 'CLO1, CLO2, CLO3, CLO4', '50%'),
        ('EN', 1, 'Participation', 'Attendance, class discussion', '15 sessions', 'CLO1, CLO2', '10%'),
        ('EN', 2, 'Homework', 'Individual and group assignments', '4 weeks', 'CLO2, CLO3', '20%'),
        ('EN', 3, 'Midterm exam', 'Multiple choice + essay', '60 minutes', 'CLO1, CLO2, CLO3', '20%'),
        ('EN', 4, 'Final exam', 'Multiple choice + practical', '90 minutes', 'CLO1, CLO2, CLO3, CLO4', '50%'),
    ]:
        conn.execute(
            "INSERT INTO course_assessments (syllabus_id, language, order_num, method, description, time, clo, weight) VALUES (?,?,?,?,?,?,?,?)",
            (s1_id, lang, order, method, desc, time_val, clo, weight)
        )

    # Teaching Plans
    for lang, week, detail, ref, act, clo in [
        ('VI', 1, 'Giới thiệu về CNTT và vai trò trong kinh tế', 'Chương 1 - Giáo trình', 'Thảo luận nhóm', 'CLO1'),
        ('VI', 2, 'Kiến trúc máy tính và hệ điều hành', 'Chương 2 - Giáo trình', 'Bài tập thực hành', 'CLO1'),
        ('VI', 3, 'Mạng máy tính và Internet', 'Chương 3 - Giáo trình', 'Thuyết trình nhóm', 'CLO1, CLO2'),
        ('VI', 4, 'Cơ sở dữ liệu cơ bản', 'Chương 4 - Giáo trình', 'Bài tập SQL', 'CLO2'),
        ('VI', 5, 'Microsoft Word nâng cao', 'Tài liệu hướng dẫn Office', 'Thực hành trên máy', 'CLO3'),
        ('VI', 6, 'Microsoft Excel - Hàm và công thức', 'Tài liệu hướng dẫn Office', 'Bài tập Excel', 'CLO3'),
        ('VI', 7, 'Microsoft PowerPoint', 'Tài liệu hướng dẫn Office', 'Thuyết trình', 'CLO3'),
        ('VI', 8, 'Kiểm tra giữa kỳ', '', 'Kiểm tra', 'CLO1, CLO2, CLO3'),
        ('VI', 9, 'Giới thiệu lập trình Python', 'Chương 5 - Giáo trình', 'Viết code cơ bản', 'CLO4'),
        ('VI', 10, 'Biến, kiểu dữ liệu và toán tử', 'Chương 5 - Giáo trình', 'Bài tập lập trình', 'CLO4'),
        ('VI', 11, 'Cấu trúc điều khiển', 'Chương 6 - Giáo trình', 'Bài tập lập trình', 'CLO4'),
        ('VI', 12, 'Hàm và module', 'Chương 6 - Giáo trình', 'Project nhỏ', 'CLO4'),
        ('VI', 13, 'Ôn tập và tổng kết', '', 'Ôn tập', 'CLO1, CLO2, CLO3, CLO4'),
        ('EN', 1, 'Introduction to IT and its role in economics', 'Chapter 1 - Textbook', 'Group discussion', 'CLO1'),
        ('EN', 2, 'Computer architecture and operating systems', 'Chapter 2 - Textbook', 'Practice exercises', 'CLO1'),
        ('EN', 3, 'Computer networks and Internet', 'Chapter 3 - Textbook', 'Group presentation', 'CLO1, CLO2'),
        ('EN', 4, 'Database fundamentals', 'Chapter 4 - Textbook', 'SQL exercises', 'CLO2'),
        ('EN', 5, 'Advanced Microsoft Word', 'Office guide materials', 'Hands-on practice', 'CLO3'),
        ('EN', 6, 'Microsoft Excel - Functions and formulas', 'Office guide materials', 'Excel exercises', 'CLO3'),
        ('EN', 7, 'Microsoft PowerPoint', 'Office guide materials', 'Presentation', 'CLO3'),
        ('EN', 8, 'Midterm exam', '', 'Exam', 'CLO1, CLO2, CLO3'),
        ('EN', 9, 'Introduction to Python programming', 'Chapter 5 - Textbook', 'Basic coding', 'CLO4'),
        ('EN', 10, 'Variables, data types and operators', 'Chapter 5 - Textbook', 'Programming exercises', 'CLO4'),
        ('EN', 11, 'Control structures', 'Chapter 6 - Textbook', 'Programming exercises', 'CLO4'),
        ('EN', 12, 'Functions and modules', 'Chapter 6 - Textbook', 'Mini project', 'CLO4'),
        ('EN', 13, 'Review and summary', '', 'Review', 'CLO1, CLO2, CLO3, CLO4'),
    ]:
        conn.execute(
            "INSERT INTO teaching_plans (syllabus_id, language, week, detail, reference, activities_assessment, clo) VALUES (?,?,?,?,?,?,?)",
            (s1_id, lang, week, detail, ref, act, clo)
        )

    # =============================================
    # Syllabus 2: Lập trình Web
    # =============================================
    conn.execute("""
        INSERT INTO syllabi (
            course_code, course_title_vi, course_title_en,
            credits, contact_hours, self_study_hours,
            training_program, decision_date, decision_number,
            prerequisite_courses_vi, prerequisite_courses_en,
            num_prerequisite_courses,
            description_vi, description_en,
            clo_assessment_vi, clo_assessment_en,
            course_requirements_vi, course_requirements_en,
            adjustment_time
        ) VALUES (
            'EP17.CNTT1205',
            'Lập trình Web',
            'Web Programming',
            3, 30, 60,
            'EP17', '2024-02-01', 'QĐ-2024/015',
            'Nhập môn CNTT (EP17.CNTT1116)', 'Introduction to IT (EP17.CNTT1116)',
            '1',
            'Học phần trang bị cho sinh viên kiến thức và kỹ năng phát triển ứng dụng web, bao gồm HTML, CSS, JavaScript, lập trình phía server và cơ sở dữ liệu.',
            'This course equips students with knowledge and skills in web application development, including HTML, CSS, JavaScript, server-side programming and databases.',
            'Đánh giá CLO thông qua bài tập thực hành, project nhóm và thi cuối kỳ.',
            'CLO assessment through practical exercises, group projects and final exam.',
            'Tham dự ít nhất 80% buổi học. Nộp đầy đủ bài tập đúng hạn. Hoàn thành project nhóm.',
            'Attend at least 80% of sessions. Submit all assignments on time. Complete group project.',
            '2024-06-15'
        )
    """)
    s2_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    # Instructors for syllabus 2
    for lang, name, email in [
        ('VI', 'Lê Văn D', 'levand@neu.edu.vn'),
        ('EN', 'Le Van D', 'levand@neu.edu.vn'),
    ]:
        conn.execute(
            "INSERT INTO syllabus_instructors (syllabus_id, language, full_name, email) VALUES (?,?,?,?)",
            (s2_id, lang, name, email)
        )

    # Books for syllabus 2
    for lang, btype, title, author, year, publisher in [
        ('VI', 'textbook', 'Lập trình Web cơ bản', 'Lê Văn D', '2023', 'NXB ĐHKTQD'),
        ('EN', 'textbook', 'Web Development with Python and JavaScript', 'Mike Johnson', '2023', 'O\'Reilly'),
        ('EN', 'reference', 'HTML and CSS: Design and Build Websites', 'Jon Duckett', '2021', 'Wiley'),
    ]:
        conn.execute(
            "INSERT INTO syllabus_books (syllabus_id, language, book_type, title, author, year, publisher) VALUES (?,?,?,?,?,?,?)",
            (s2_id, lang, btype, title, author, year, publisher)
        )

    # Software for syllabus 2
    for lang, name, desc, ver in [
        ('VI', 'Visual Studio Code', 'Trình soạn thảo code', '1.85'),
        ('VI', 'Python + Flask', 'Framework lập trình web', '3.11 / 3.0'),
        ('EN', 'Visual Studio Code', 'Code editor', '1.85'),
        ('EN', 'Python + Flask', 'Web programming framework', '3.11 / 3.0'),
    ]:
        conn.execute(
            "INSERT INTO syllabus_software (syllabus_id, language, software_name, description, version) VALUES (?,?,?,?,?)",
            (s2_id, lang, name, desc, ver)
        )

    # Goals for syllabus 2
    for lang, code, desc, plo in [
        ('VI', 'G1', 'Nắm vững kiến thức nền tảng về phát triển web (HTML, CSS, JS)', 'PLO1'),
        ('VI', 'G2', 'Xây dựng được ứng dụng web hoàn chỉnh với Flask', 'PLO2, PLO3'),
        ('EN', 'G1', 'Master fundamental web development knowledge (HTML, CSS, JS)', 'PLO1'),
        ('EN', 'G2', 'Build complete web applications with Flask', 'PLO2, PLO3'),
    ]:
        conn.execute(
            "INSERT INTO course_goals (syllabus_id, language, goal_code, description, plo) VALUES (?,?,?,?,?)",
            (s2_id, lang, code, desc, plo)
        )

    # Learning Outcomes for syllabus 2
    for lang, goal, clo, desc, level in [
        ('VI', 'G1', 'CLO1', 'Thiết kế giao diện web responsive với HTML/CSS', 'TU3'),
        ('VI', 'G1', 'CLO2', 'Lập trình tương tác phía client với JavaScript', 'ITU3'),
        ('VI', 'G2', 'CLO3', 'Xây dựng ứng dụng web phía server với Flask', 'ITU3'),
        ('EN', 'G1', 'CLO1', 'Design responsive web interfaces with HTML/CSS', 'TU3'),
        ('EN', 'G1', 'CLO2', 'Program client-side interactions with JavaScript', 'ITU3'),
        ('EN', 'G2', 'CLO3', 'Build server-side web applications with Flask', 'ITU3'),
    ]:
        conn.execute(
            "INSERT INTO learning_outcomes (syllabus_id, language, goal, clo_code, clo_description, level) VALUES (?,?,?,?,?,?)",
            (s2_id, lang, goal, clo, desc, level)
        )

    # Assessments for syllabus 2
    for lang, order, method, desc, time_val, clo, weight in [
        ('VI', 1, 'Tham gia lớp học', 'Điểm danh, thực hành', '15 buổi', 'CLO1, CLO2', '10%'),
        ('VI', 2, 'Bài tập thực hành', 'Xây dựng trang web', '5 tuần', 'CLO1, CLO2, CLO3', '20%'),
        ('VI', 3, 'Project nhóm', 'Ứng dụng web hoàn chỉnh', '6 tuần', 'CLO1, CLO2, CLO3', '30%'),
        ('VI', 4, 'Thi cuối kỳ', 'Thực hành + vấn đáp', '120 phút', 'CLO1, CLO2, CLO3', '40%'),
        ('EN', 1, 'Participation', 'Attendance, practice', '15 sessions', 'CLO1, CLO2', '10%'),
        ('EN', 2, 'Practical assignments', 'Build web pages', '5 weeks', 'CLO1, CLO2, CLO3', '20%'),
        ('EN', 3, 'Group project', 'Complete web application', '6 weeks', 'CLO1, CLO2, CLO3', '30%'),
        ('EN', 4, 'Final exam', 'Practical + oral', '120 minutes', 'CLO1, CLO2, CLO3', '40%'),
    ]:
        conn.execute(
            "INSERT INTO course_assessments (syllabus_id, language, order_num, method, description, time, clo, weight) VALUES (?,?,?,?,?,?,?,?)",
            (s2_id, lang, order, method, desc, time_val, clo, weight)
        )

    # Teaching Plans for syllabus 2
    for lang, week, detail, ref, act, clo in [
        ('VI', 1, 'Tổng quan về Web và kiến trúc Client-Server', 'Chương 1', 'Thảo luận', 'CLO1'),
        ('VI', 2, 'HTML5 cơ bản', 'Chương 2', 'Thực hành HTML', 'CLO1'),
        ('VI', 3, 'CSS3 và Layout', 'Chương 3', 'Thực hành CSS', 'CLO1'),
        ('VI', 4, 'Responsive Design và Bootstrap', 'Chương 3', 'Xây dựng trang responsive', 'CLO1'),
        ('VI', 5, 'JavaScript cơ bản', 'Chương 4', 'Bài tập JS', 'CLO2'),
        ('VI', 6, 'DOM và sự kiện', 'Chương 4', 'Thực hành DOM', 'CLO2'),
        ('VI', 7, 'AJAX và Fetch API', 'Chương 5', 'Bài tập AJAX', 'CLO2'),
        ('VI', 8, 'Giới thiệu Flask', 'Chương 6', 'Setup Flask project', 'CLO3'),
        ('VI', 9, 'Flask Routes và Templates', 'Chương 6', 'Thực hành Jinja2', 'CLO3'),
        ('VI', 10, 'Flask Forms và Database', 'Chương 7', 'CRUD app', 'CLO3'),
        ('VI', 11, 'Authentication và Session', 'Chương 8', 'Login system', 'CLO3'),
        ('VI', 12, 'Hoàn thiện project nhóm', '', 'Review code', 'CLO1, CLO2, CLO3'),
        ('VI', 13, 'Trình bày project + Ôn tập', '', 'Thuyết trình', 'CLO1, CLO2, CLO3'),
        ('EN', 1, 'Web overview and Client-Server architecture', 'Chapter 1', 'Discussion', 'CLO1'),
        ('EN', 2, 'HTML5 fundamentals', 'Chapter 2', 'HTML practice', 'CLO1'),
        ('EN', 3, 'CSS3 and Layout', 'Chapter 3', 'CSS practice', 'CLO1'),
        ('EN', 4, 'Responsive Design and Bootstrap', 'Chapter 3', 'Build responsive page', 'CLO1'),
        ('EN', 5, 'JavaScript basics', 'Chapter 4', 'JS exercises', 'CLO2'),
        ('EN', 6, 'DOM and Events', 'Chapter 4', 'DOM practice', 'CLO2'),
        ('EN', 7, 'AJAX and Fetch API', 'Chapter 5', 'AJAX exercises', 'CLO2'),
        ('EN', 8, 'Introduction to Flask', 'Chapter 6', 'Setup Flask project', 'CLO3'),
        ('EN', 9, 'Flask Routes and Templates', 'Chapter 6', 'Jinja2 practice', 'CLO3'),
        ('EN', 10, 'Flask Forms and Database', 'Chapter 7', 'CRUD app', 'CLO3'),
        ('EN', 11, 'Authentication and Session', 'Chapter 8', 'Login system', 'CLO3'),
        ('EN', 12, 'Complete group project', '', 'Code review', 'CLO1, CLO2, CLO3'),
        ('EN', 13, 'Project presentation + Review', '', 'Presentation', 'CLO1, CLO2, CLO3'),
    ]:
        conn.execute(
            "INSERT INTO teaching_plans (syllabus_id, language, week, detail, reference, activities_assessment, clo) VALUES (?,?,?,?,?,?,?)",
            (s2_id, lang, week, detail, ref, act, clo)
        )

    conn.commit()
    conn.close()
    print("[OK] Sample data seeded (2 syllabi with full VI+EN data).")


if __name__ == '__main__':
    init_db()
    seed_admin()
    seed_sample_data()
    print("\nAll done! Run 'python app.py' to start the server.")
