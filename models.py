from datetime import datetime
from flask_login import UserMixin
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# ======================
# USER MODEL
# ======================
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="user", nullable=False)  # user, admin, engineer
    speciality = db.Column(db.String(120), nullable=True)

    # User's own requests
    service_requests = db.relationship(
        "ServiceRequest",
        foreign_keys="ServiceRequest.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Notifications
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        order_by="Notification.created_at.desc()",
        cascade="all, delete-orphan",
    )

    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ======================
# SERVICE REQUEST MODEL
# ======================
class ServiceRequest(db.Model):
    __tablename__ = "service_request"

    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120))
    model_no = db.Column(db.String(120))
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(50), default="pending", nullable=False)
    approval_status = db.Column(db.String(50), default="waiting", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Engineer's work description
    work_done = db.Column(db.Text, nullable=True)  # ✅ Added field

    # Request owner
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", foreign_keys=[user_id], back_populates="service_requests")

    # Alias for templates
    requester = db.relationship(
        "User",
        foreign_keys=[user_id],
        viewonly=True,
    )

    # Assigned engineer
    assigned_engineer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    assigned_engineer = db.relationship(
        "User",
        foreign_keys=[assigned_engineer_id],
        backref="assigned_requests"
    )

    # One-to-one receipt
    receipt = db.relationship(
        "Receipt",
        back_populates="service_request",
        uselist=False,
        cascade="all, delete-orphan"
    )


# ======================
# RECEIPT MODEL
# ======================
class Receipt(db.Model):
    __tablename__ = "receipt"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)

    service_request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.id"),
        unique=True,
        nullable=False
    )
    service_request = db.relationship("ServiceRequest", back_populates="receipt")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ======================
# NOTIFICATION MODEL
# ======================
class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(300), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="notifications")
