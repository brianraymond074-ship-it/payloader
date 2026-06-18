from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin

db = SQLAlchemy()


class Admin(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    balance = db.Column(
        db.Float,
        default=400000.0
    )


class Employee(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    balance = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Transaction(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        nullable=True
    )

    tx_type = db.Column(
        db.String(50)
    )

    amount = db.Column(
        db.Float
    )

    status = db.Column(
        db.String(50)
    )

    description = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class WithdrawalRequest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employee_id = db.Column(
        db.Integer,
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="PENDING"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )