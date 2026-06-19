from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Admin(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    password_hash = db.Column(
        db.String(255)
    )

    phone = db.Column(
        db.String(20)
    )

    balance = db.Column(
        db.Float,
        default=400000
    )


class Employee(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(20)
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

    employee_name = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(20)
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

    reference = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )