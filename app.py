"""NEU Syllabus Management System — Flask Application."""
import functools
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
import config
import models

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


# ============================================
# AUTH HELPERS
# ============================================

def login_required(view):
    """Decorator: redirect to login if not authenticated."""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped


def admin_required(view):
    """Decorator: redirect if not admin."""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped


# ============================================
# PUBLIC ROUTES
# ============================================

@app.route('/')
def index():
    syllabi = models.get_all_syllabi()
    return render_template('index.html', syllabi=syllabi)


@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('index'))
    results = models.search_syllabi(q)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([{
            'id': r['id'],
            'course_code': r['course_code'],
            'course_title_vi': r['course_title_vi'],
            'course_title_en': r['course_title_en'],
            'credits': r['credits'],
            'training_program': r['training_program'],
        } for r in results])
    return render_template('search_results.html', results=results, query=q)


@app.route('/syllabus/<course_code>')
def course_detail(course_code):
    syllabus = models.get_syllabus_by_code(course_code)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('index'))
    sid = syllabus['id']
    data = {
        'syllabus': syllabus,
        'instructors_vi': models.get_sub_items('syllabus_instructors', sid, 'VI'),
        'instructors_en': models.get_sub_items('syllabus_instructors', sid, 'EN'),
        'books_vi': models.get_sub_items('syllabus_books', sid, 'VI'),
        'books_en': models.get_sub_items('syllabus_books', sid, 'EN'),
        'software_vi': models.get_sub_items('syllabus_software', sid, 'VI'),
        'software_en': models.get_sub_items('syllabus_software', sid, 'EN'),
        'goals_vi': models.get_sub_items('course_goals', sid, 'VI', 'goal_code'),
        'goals_en': models.get_sub_items('course_goals', sid, 'EN', 'goal_code'),
        'outcomes_vi': models.get_sub_items('learning_outcomes', sid, 'VI', 'clo_code'),
        'outcomes_en': models.get_sub_items('learning_outcomes', sid, 'EN', 'clo_code'),
        'assessments_vi': models.get_sub_items('course_assessments', sid, 'VI', 'order_num'),
        'assessments_en': models.get_sub_items('course_assessments', sid, 'EN', 'order_num'),
        'plans_vi': models.get_sub_items('teaching_plans', sid, 'VI', 'week'),
        'plans_en': models.get_sub_items('teaching_plans', sid, 'EN', 'week'),
    }
    return render_template('course_detail.html', **data)


# ============================================
# AUTH ROUTES
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = models.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Đăng nhập thành công!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif len(username) < 3:
            flash('Tên đăng nhập phải có ít nhất 3 ký tự.', 'danger')
        elif len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'danger')
        elif password != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
        else:
            existing = models.get_user_by_username(username)
            if existing:
                flash('Tên đăng nhập đã tồn tại.', 'danger')
            else:
                pw_hash = generate_password_hash(password)
                user_id = models.create_user(username, pw_hash, 'user')
                if user_id:
                    session['user_id'] = user_id
                    session['username'] = username
                    session['role'] = 'user'
                    flash('Đăng ký thành công! Chào mừng bạn.', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Đã xảy ra lỗi. Vui lòng thử lại.', 'danger')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất.', 'info')
    return redirect(url_for('index'))


# ============================================
# ADMIN — DASHBOARD
# ============================================

@app.route('/admin/')
@admin_required
def admin_dashboard():
    q = request.args.get('q', '').strip()
    if q:
        syllabi = models.search_syllabi(q)
    else:
        syllabi = models.get_all_syllabi()
    return render_template('admin/dashboard.html', syllabi=syllabi, query=q)


# ============================================
# ADMIN — SYLLABUS CRUD
# ============================================

@app.route('/admin/syllabus/new', methods=['GET', 'POST'])
@admin_required
def admin_syllabus_new():
    if request.method == 'POST':
        data = _extract_syllabus_form(request.form)
        if not data['course_code']:
            flash('Mã học phần không được để trống.', 'danger')
            return render_template('admin/syllabus_form.html', syllabus=None, form_data=data)
        existing = models.get_syllabus_by_code(data['course_code'])
        if existing:
            flash('Mã học phần đã tồn tại.', 'danger')
            return render_template('admin/syllabus_form.html', syllabus=None, form_data=data)
        sid = models.create_syllabus(data)
        flash('Tạo đề cương thành công!', 'success')
        return redirect(url_for('admin_syllabus_edit', syllabus_id=sid))
    return render_template('admin/syllabus_form.html', syllabus=None, form_data=None)


@app.route('/admin/syllabus/<int:syllabus_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_syllabus_edit(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        data = _extract_syllabus_form(request.form)
        if not data['course_code']:
            flash('Mã học phần không được để trống.', 'danger')
            return render_template('admin/syllabus_form.html', syllabus=syllabus, form_data=data)
        dup = models.get_syllabus_by_code(data['course_code'])
        if dup and dup['id'] != syllabus_id:
            flash('Mã học phần đã tồn tại cho đề cương khác.', 'danger')
            return render_template('admin/syllabus_form.html', syllabus=syllabus, form_data=data)
        models.update_syllabus(syllabus_id, data)
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('admin_syllabus_edit', syllabus_id=syllabus_id))
    return render_template('admin/syllabus_form.html', syllabus=syllabus, form_data=None)


@app.route('/admin/syllabus/<int:syllabus_id>/delete', methods=['POST'])
@admin_required
def admin_syllabus_delete(syllabus_id):
    models.delete_syllabus(syllabus_id)
    flash('Đã xóa đề cương.', 'success')
    return redirect(url_for('admin_dashboard'))


def _extract_syllabus_form(form):
    """Extract syllabus fields from a form submission."""
    return {
        'course_code': form.get('course_code', '').strip(),
        'course_title_vi': form.get('course_title_vi', '').strip(),
        'course_title_en': form.get('course_title_en', '').strip(),
        'credits': int(form.get('credits', 0) or 0),
        'contact_hours': int(form.get('contact_hours', 0) or 0),
        'self_study_hours': int(form.get('self_study_hours', 0) or 0),
        'training_program': form.get('training_program', '').strip(),
        'decision_date': form.get('decision_date', '').strip(),
        'decision_number': form.get('decision_number', '').strip(),
        'prerequisite_courses_vi': form.get('prerequisite_courses_vi', '').strip(),
        'prerequisite_courses_en': form.get('prerequisite_courses_en', '').strip(),
        'num_prerequisite_courses': form.get('num_prerequisite_courses', 'None').strip(),
        'description_vi': form.get('description_vi', '').strip(),
        'description_en': form.get('description_en', '').strip(),
        'clo_assessment_vi': form.get('clo_assessment_vi', '').strip(),
        'clo_assessment_en': form.get('clo_assessment_en', '').strip(),
        'course_requirements_vi': form.get('course_requirements_vi', '').strip(),
        'course_requirements_en': form.get('course_requirements_en', '').strip(),
        'adjustment_time': form.get('adjustment_time', '').strip(),
    }


# ============================================
# ADMIN — SUB-TABLE GENERIC PATTERN
# Each sub-table route: GET shows list + form, POST adds/updates/deletes
# ============================================

@app.route('/admin/syllabus/<int:syllabus_id>/instructors', methods=['GET', 'POST'])
@admin_required
def admin_instructors(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_instructor(
                syllabus_id, lang,
                request.form.get('full_name', '').strip(),
                request.form.get('email', '').strip()
            )
            flash('Thêm giảng viên thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_instructor(
                item_id,
                request.form.get('full_name', '').strip(),
                request.form.get('email', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('syllabus_instructors', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_instructors', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('syllabus_instructors', syllabus_id, 'VI')
    items_en = models.get_sub_items('syllabus_instructors', syllabus_id, 'EN')
    return render_template('admin/instructors.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


@app.route('/admin/syllabus/<int:syllabus_id>/books', methods=['GET', 'POST'])
@admin_required
def admin_books(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_book(
                syllabus_id, lang,
                request.form.get('book_type', 'textbook'),
                request.form.get('title', '').strip(),
                request.form.get('author', '').strip(),
                request.form.get('year', '').strip(),
                request.form.get('publisher', '').strip()
            )
            flash('Thêm sách thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_book(
                item_id,
                request.form.get('book_type', 'textbook'),
                request.form.get('title', '').strip(),
                request.form.get('author', '').strip(),
                request.form.get('year', '').strip(),
                request.form.get('publisher', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('syllabus_books', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_books', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('syllabus_books', syllabus_id, 'VI')
    items_en = models.get_sub_items('syllabus_books', syllabus_id, 'EN')
    return render_template('admin/books.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


@app.route('/admin/syllabus/<int:syllabus_id>/software', methods=['GET', 'POST'])
@admin_required
def admin_software(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_software(
                syllabus_id, lang,
                request.form.get('software_name', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('version', '').strip()
            )
            flash('Thêm phần mềm thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_software(
                item_id,
                request.form.get('software_name', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('version', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('syllabus_software', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_software', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('syllabus_software', syllabus_id, 'VI')
    items_en = models.get_sub_items('syllabus_software', syllabus_id, 'EN')
    return render_template('admin/software.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


@app.route('/admin/syllabus/<int:syllabus_id>/goals', methods=['GET', 'POST'])
@admin_required
def admin_goals(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_goal(
                syllabus_id, lang,
                request.form.get('goal_code', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('plo', '').strip()
            )
            flash('Thêm mục tiêu thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_goal(
                item_id,
                request.form.get('goal_code', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('plo', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('course_goals', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_goals', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('course_goals', syllabus_id, 'VI', 'goal_code')
    items_en = models.get_sub_items('course_goals', syllabus_id, 'EN', 'goal_code')
    return render_template('admin/goals.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


@app.route('/admin/syllabus/<int:syllabus_id>/outcomes', methods=['GET', 'POST'])
@admin_required
def admin_outcomes(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_outcome(
                syllabus_id, lang,
                request.form.get('goal', '').strip(),
                request.form.get('clo_code', '').strip(),
                request.form.get('clo_description', '').strip(),
                request.form.get('level', '').strip()
            )
            flash('Thêm chuẩn đầu ra thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_outcome(
                item_id,
                request.form.get('goal', '').strip(),
                request.form.get('clo_code', '').strip(),
                request.form.get('clo_description', '').strip(),
                request.form.get('level', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('learning_outcomes', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_outcomes', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('learning_outcomes', syllabus_id, 'VI', 'clo_code')
    items_en = models.get_sub_items('learning_outcomes', syllabus_id, 'EN', 'clo_code')
    return render_template('admin/outcomes.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


@app.route('/admin/syllabus/<int:syllabus_id>/assessments', methods=['GET', 'POST'])
@admin_required
def admin_assessments(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_assessment(
                syllabus_id, lang,
                int(request.form.get('order_num', 0) or 0),
                request.form.get('method', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('time', '').strip(),
                request.form.get('clo', '').strip(),
                request.form.get('weight', '').strip()
            )
            flash('Thêm phương pháp đánh giá thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_assessment(
                item_id,
                int(request.form.get('order_num', 0) or 0),
                request.form.get('method', '').strip(),
                request.form.get('description', '').strip(),
                request.form.get('time', '').strip(),
                request.form.get('clo', '').strip(),
                request.form.get('weight', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('course_assessments', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_assessments', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('course_assessments', syllabus_id, 'VI', 'order_num')
    items_en = models.get_sub_items('course_assessments', syllabus_id, 'EN', 'order_num')
    return render_template('admin/assessments.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


@app.route('/admin/syllabus/<int:syllabus_id>/teaching-plan', methods=['GET', 'POST'])
@admin_required
def admin_teaching_plan(syllabus_id):
    syllabus = models.get_syllabus_by_id(syllabus_id)
    if not syllabus:
        flash('Không tìm thấy đề cương.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        lang = request.form.get('language', 'VI')
        if action == 'add':
            models.create_teaching_plan(
                syllabus_id, lang,
                int(request.form.get('week', 0) or 0),
                request.form.get('detail', '').strip(),
                request.form.get('reference', '').strip(),
                request.form.get('activities_assessment', '').strip(),
                request.form.get('clo', '').strip()
            )
            flash('Thêm kế hoạch giảng dạy thành công!', 'success')
        elif action == 'edit':
            item_id = int(request.form.get('item_id', 0))
            models.update_teaching_plan(
                item_id,
                int(request.form.get('week', 0) or 0),
                request.form.get('detail', '').strip(),
                request.form.get('reference', '').strip(),
                request.form.get('activities_assessment', '').strip(),
                request.form.get('clo', '').strip()
            )
            flash('Cập nhật thành công!', 'success')
        elif action == 'delete':
            item_id = int(request.form.get('item_id', 0))
            models.delete_sub_item('teaching_plans', item_id)
            flash('Đã xóa.', 'success')
        return redirect(url_for('admin_teaching_plan', syllabus_id=syllabus_id))

    items_vi = models.get_sub_items('teaching_plans', syllabus_id, 'VI', 'week')
    items_en = models.get_sub_items('teaching_plans', syllabus_id, 'EN', 'week')
    return render_template('admin/teaching_plan.html',
                           syllabus=syllabus, items_vi=items_vi, items_en=items_en)


# ============================================
# RUN
# ============================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
