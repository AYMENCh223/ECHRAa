from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import requests

auth_bp = Blueprint('auth', __name__)

SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY')

SUPABASE_AUTH_URL = f"{SUPABASE_URL}/auth/v1" if SUPABASE_URL else None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if SUPABASE_AUTH_URL and SUPABASE_ANON_KEY:
            headers = {
                'apikey': SUPABASE_ANON_KEY,
                'Content-Type': 'application/json'
            }
            data = {
                'email': email,
                'password': password
            }
            response = requests.post(f"{SUPABASE_AUTH_URL}/token?grant_type=password", json=data, headers=headers)
            if response.status_code == 200:
                session['user'] = response.json().get('access_token')
                flash('تم تسجيل الدخول بنجاح.', 'success')
                return redirect(url_for('index'))
            else:
                flash('فشل تسجيل الدخول. يرجى التحقق من بياناتك.', 'error')
        else:
            # Mock login: accept any email/password for development
            session['user'] = email
            flash('تم تسجيل الدخول التجريبي بنجاح.', 'success')
            return redirect(url_for('index'))
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if SUPABASE_AUTH_URL and SUPABASE_ANON_KEY:
            headers = {
                'apikey': SUPABASE_ANON_KEY,
                'Content-Type': 'application/json'
            }
            data = {
                'email': email,
                'password': password
            }
            response = requests.post(f"{SUPABASE_AUTH_URL}/signup", json=data, headers=headers)
            if response.status_code == 200:
                flash('تم إنشاء الحساب بنجاح. يرجى تسجيل الدخول.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('فشل إنشاء الحساب. يرجى المحاولة مرة أخرى.', 'error')
        else:
            # Mock signup: accept any email/password for development
            flash('تم إنشاء الحساب التجريبي بنجاح. يرجى تسجيل الدخول.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if SUPABASE_AUTH_URL and SUPABASE_ANON_KEY:
            headers = {
                'apikey': SUPABASE_ANON_KEY,
                'Content-Type': 'application/json'
            }
            data = {'email': email}
            response = requests.post(f"{SUPABASE_AUTH_URL}/recover", json=data, headers=headers)
            if response.status_code == 200:
                flash('تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.', 'success')
            else:
                flash('حدث خطأ. يرجى المحاولة مرة أخرى.', 'error')
        else:
            # Mock forgot password for development
            flash('تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني (وضع التطوير).', 'success')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('auth.login'))
