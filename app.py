import os
import json
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from config import Config
from extensions import db
from models import User, ServiceRequest, Receipt, Notification
from forms import RegisterForm, LoginForm, ServiceRequestForm, AssignEngineerForm, ReceiptForm
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from datetime import datetime
from sqlalchemy import or_

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Login Manager
    login = LoginManager(app)
    login.login_view = 'login'

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---------------------- #
    # INDEX ROUTE
    # ---------------------- #
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'engineer':
                return redirect(url_for('engineer_dashboard'))
            else:
                return redirect(url_for('my_requests'))
        return render_template('index.html')
        # ---------------------- #
    # ABOUT COMPANY PAGE
    # ---------------------- #
    @app.route('/about')
    def about():
        company_info = {
            "name": "SmartFix Service Centre",
            "established": "2022",
            "services": [
                "TV Repair",
                "Refrigerator Repair",
                "Washing Machine Service",
                "Mobile & Laptop Repair",
                "Home Appliance Maintenance"
            ],
            "mission": "To provide fast, reliable and affordable home appliance repair services."
        }
        return render_template('about.html', company=company_info)

    # ---------------------- #
    # CONTACT US PAGE
    # ---------------------- #
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

            flash('Thank you for contacting us! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))

        return render_template('contact.html')

    # ---------------------- #
    # SERVICE CENTRE INFO
    # ---------------------- #
    @app.route('/service-centre')
    def service_centre():
        centre_details = {
            "centre_name": "SmartFix Authorized Service Centre",
            "address": "Mira Bhayandar, Mumbai, Maharashtra",
            "phone": "+91 9876543210",
            "email": "support@smartfix.com",
            "working_hours": "Mon-Sat (9:00 AM - 7:00 PM)"
        }
        return render_template('service_centre.html', centre=centre_details)


    # ---------------------- #
    # REGISTER
    # ---------------------- #
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'warning')
                return redirect(url_for('register'))
            u = User(name=form.name.data, email=form.email.data, role='user')
            u.set_password(form.password.data)
            db.session.add(u)
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    # ---------------------- #
    # LOGIN
    # ---------------------- #
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Invalid email or password', 'danger')
        return render_template('login.html', form=form)

    # ---------------------- #
    # LOGOUT
    # ---------------------- #
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out', 'info')
        return redirect(url_for('index'))

    # ---------------------- #
    # USER - CREATE REQUEST
    # ---------------------- #
    @app.route('/request/new', methods=['GET', 'POST'])
    @login_required
    def new_request():
        form = ServiceRequestForm()
        if form.validate_on_submit():
            sr = ServiceRequest(
                user_id=current_user.id,
                device_type=form.device_type.data,
                brand=form.brand.data,
                model_no=form.model_no.data,
                description=form.description.data
            )
            db.session.add(sr)
            db.session.flush()

            # Notify admins
            admins = User.query.filter_by(role='admin').all()
            for admin in admins:
                db.session.add(Notification(
                    user_id=admin.id,
                    message=f"New service request #{sr.id} by {current_user.name} awaiting approval",
                    link=url_for('admin_dashboard')
                ))

            # Notify user
            db.session.add(Notification(
                user_id=current_user.id,
                message=f"Your service request #{sr.id} has been created and is awaiting admin approval.",
                link=url_for('my_requests')
            ))

            db.session.commit()
            flash('Service request created. Awaiting admin approval.', 'success')
            return redirect(url_for('my_requests'))
        return render_template('new_request.html', form=form)
    @app.route('/admin/customer/<int:user_id>/history')
    @login_required
    def customer_history(user_id):

        if current_user.role != 'admin':
            abort(403)

        customer = User.query.get_or_404(user_id)
        requests = ServiceRequest.query.filter_by(user_id=user_id).all()

        return render_template('admin/customer_history.html',
                            customer=customer,
                            requests=requests)

    @app.route('/my-requests')
    @login_required
    def my_requests():
        reqs = ServiceRequest.query.filter_by(user_id=current_user.id).order_by(ServiceRequest.created_at.desc()).all()
        return render_template('my_requests.html', reqs=reqs)

    # ---------------------- #
    # ADMIN ONLY DECORATOR
    # ---------------------- #
    def admin_required(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != 'admin':
                abort(403)
            return f(*args, **kwargs)
        return decorated

    # ---------------------- #
    # ADMIN DASHBOARD
    # ---------------------- #
    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        pending_requests = ServiceRequest.query.filter_by(approval_status='waiting').order_by(ServiceRequest.created_at.desc()).all()
        approved_requests = ServiceRequest.query.filter_by(approval_status='approved').order_by(ServiceRequest.created_at.desc()).all()
        engineers = User.query.filter(User.role == 'engineer').all()
        return render_template(
            'admin_dashboard.html',
            pending_requests=pending_requests,
            approved_requests=approved_requests,
            engineers=engineers
        )

    # ---------------------- #
    # APPROVE / REJECT REQUEST
    # ---------------------- #
    @app.route('/admin/approve/<int:request_id>')
    @login_required
    @admin_required
    def approve_request(request_id):
        sr = ServiceRequest.query.get_or_404(request_id)
        sr.approval_status = 'approved'
        db.session.add(sr)
        db.session.add(Notification(
            user_id=sr.user_id,
            message=f"Your request #{sr.id} has been approved by admin.",
            link=url_for('my_requests')
        ))
        db.session.commit()
        flash(f'Request #{sr.id} approved.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/reject/<int:request_id>')
    @login_required
    @admin_required
    def reject_request(request_id):
        sr = ServiceRequest.query.get_or_404(request_id)
        sr.approval_status = 'rejected'
        db.session.add(Notification(
            user_id=sr.user_id,
            message=f"Your request #{sr.id} has been rejected by admin.",
            link=url_for('my_requests')
        ))
        db.session.commit()
        flash(f'Request #{sr.id} rejected.', 'warning')
        return redirect(url_for('admin_dashboard'))

    # ---------------------- #
    # ASSIGN ENGINEER
    # ---------------------- #
    @app.route('/admin/assign/<int:request_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def assign_engineer(request_id):
        sr = ServiceRequest.query.get_or_404(request_id)
        if sr.approval_status != 'approved':
            flash("Cannot assign engineer until request is approved.", "warning")
            return redirect(url_for('admin_dashboard'))

        engineers = User.query.filter(
            User.role == 'engineer',
            User.speciality.ilike(f"%{sr.device_type}%")
        ).all()

        if not engineers:
            engineers = User.query.filter(User.role == 'engineer').all()

        for e in engineers:
            if not e.speciality:
                e.speciality = "General Service"

        choices = [(e.id, f"{e.name} - {e.speciality}") for e in engineers]
        form = AssignEngineerForm()
        form.engineer_id.choices = choices
        engineer_details_json = json.dumps(choices)

        if form.validate_on_submit():
            sr.assigned_engineer_id = form.engineer_id.data
            sr.status = 'assigned'
            eng = User.query.get(sr.assigned_engineer_id)

            if eng:
                db.session.add(Notification(
                    user_id=eng.id,
                    message=f"You were assigned to request #{sr.id}.",
                    link=url_for('engineer_dashboard')
                ))
                db.session.add(Notification(
                    user_id=sr.user_id,
                    message=f"Your request #{sr.id} has been assigned to {eng.name} ({eng.speciality}).",
                    link=url_for('my_requests')
                ))

            db.session.commit()
            flash('Engineer assigned successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('assign_engineer.html', form=form, sr=sr, engineer_details_json=engineer_details_json)

    # ---------------------- #
    # RECEIPT ROUTES
    # ---------------------- #
    @app.route('/admin/receipt/<int:request_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def generate_receipt(request_id):
        sr = ServiceRequest.query.get_or_404(request_id)
        form = ReceiptForm()
        if form.validate_on_submit():
            r = Receipt(
                service_request_id=sr.id,
                amount=form.amount.data,
                payment_method=form.payment_method.data,
                details=form.details.data
            )
            db.session.add(r)
            db.session.flush()
            sr.status = 'completed'
            db.session.add(Notification(
                user_id=sr.user_id,
                message=f"Your request #{sr.id} has been completed. Receipt #{r.id} is available.",
                link=url_for('view_receipt', receipt_id=r.id)
            ))
            db.session.commit()
            flash('Receipt generated.', 'success')
            return redirect(url_for('view_receipt', receipt_id=r.id))
        return render_template('generate_receipt.html', form=form, sr=sr)

    @app.route('/receipt/<int:receipt_id>')
    @login_required
    def view_receipt(receipt_id):
        r = Receipt.query.get_or_404(receipt_id)
        return render_template('receipt.html', receipt=r)

    # ---------------------- #
    # ADMIN SEARCH
    # ---------------------- #
    @app.route('/admin/search')
    @login_required
    @admin_required
    def admin_search():
        q = request.args.get('q', '')
        results = []
        if q:
            results = ServiceRequest.query.filter(
                or_(
                    ServiceRequest.device_type.ilike(f'%{q}%'),
                    ServiceRequest.description.ilike(f'%{q}%'),
                )
            ).all()
        return render_template('admin_search.html', results=results, q=q)

    # ---------------------- #
    # NOTIFICATIONS
    # ---------------------- #
    @app.route("/notifications")
    @login_required
    def notifications():
        notes = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        return render_template("notifications.html", notifications=notes)

    @app.route("/notifications/read/<int:note_id>")
    @login_required
    def mark_read(note_id):
        n = Notification.query.get_or_404(note_id)
        if n.user_id != current_user.id:
            abort(403)
        n.is_read = True
        db.session.commit()
        return redirect(n.link or url_for("notifications"))

    # ---------------------- #
    # CLI COMMANDS
    # ---------------------- #
    @app.cli.command('create-admin')
    def create_admin():
        email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        name = os.environ.get('ADMIN_NAME', 'Admin')
        pwd = os.environ.get('ADMIN_PASS', 'password123')
        if User.query.filter_by(email=email).first():
            print('Admin already exists.')
            return
        admin = User(name=name, email=email, role='admin')
        admin.set_password(pwd)
        db.session.add(admin)

        engineers_data = [
            ('Engineer One', 'eng1@example.com', 'TV & Fridge Repair'),
            ('Engineer Two', 'eng2@example.com', 'Washing Machine Expert'),
            ('Engineer Three', 'eng3@example.com', 'Mobile & Laptop Specialist')
        ]
        for name, email, spec in engineers_data:
            if not User.query.filter_by(email=email).first():
                e = User(name=name, email=email, role='engineer', speciality=spec)
                e.set_password('engpass')
                db.session.add(e)

        db.session.commit()
        print('Admin and sample engineers created successfully.')

    # ---------------------- #
    # ENGINEER DECORATOR
    # ---------------------- #
    def engineer_required(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != 'engineer':
                abort(403)
            return f(*args, **kwargs)
        return decorated

    # ---------------------- #
    # ENGINEER DASHBOARD
    # ---------------------- #
    @app.route('/engineer')
    @login_required
    @engineer_required
    def engineer_dashboard():
        reqs = ServiceRequest.query.filter_by(assigned_engineer_id=current_user.id).order_by(ServiceRequest.created_at.desc()).all()
        return render_template('engineer_dashboard.html', reqs=reqs)

    # ---------------------- #
    # ENGINEER VIEW / UPDATE WORK
    # ---------------------- #
    @app.route('/engineer/request/<int:request_id>', methods=['GET', 'POST'])
    @login_required
    @engineer_required
    def engineer_request_detail(request_id):
        sr = ServiceRequest.query.get_or_404(request_id)
        if sr.assigned_engineer_id != current_user.id:
            abort(403)

        if request.method == 'POST':
            work_done = request.form.get('work_done', '').strip()
            status = request.form.get('status', '').strip()

            if work_done:
                sr.work_done = work_done

            if status == 'done':
                sr.status = 'done'
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    db.session.add(Notification(
                        user_id=admin.id,
                        message=f"Engineer {current_user.name} marked request #{sr.id} as done.",
                        link=url_for('generate_receipt', request_id=sr.id)
                    ))

            db.session.commit()
            flash('Work details updated successfully.', 'success')
            return redirect(url_for('engineer_dashboard'))

        return render_template('engineer_request_detail.html', sr=sr)

    # ---------------------- #
    # ERROR HANDLER
    # ---------------------- #
    @app.errorhandler(403)
    def forbidden(e):
        flash("You don't have permission to access that page.", "danger")
        return redirect(url_for('index'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
