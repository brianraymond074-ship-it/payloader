from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config import Config

from models import (
    db,
    Admin,
    Employee,
    Transaction
)

from services.mobile_money import (
    send_money
)

import os


app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):

    return Admin.query.get(
        int(user_id)
    )


@app.route("/")
def home():

    return redirect("/login")


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password_hash,
            password
        ):

            login_user(admin)

            return redirect(
                "/dashboard"
            )

        flash(
            "Invalid Login"
        )

    return render_template(
        "login.html"
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        "/login"
    )


@app.route("/dashboard")
@login_required
def dashboard():

    admin = Admin.query.first()

    employees = Employee.query.all()

    return render_template(
        "dashboard.html",
        admin=admin,
        employees=employees
    )


@app.route(
    "/add-employee",
    methods=["POST"]
)
@login_required
def add_employee():

    name = request.form.get(
        "name"
    )

    phone = request.form.get(
        "phone"
    )

    employee = Employee(
        name=name,
        phone=phone
    )

    db.session.add(
        employee
    )

    db.session.commit()

    flash(
        "Employee Added Successfully"
    )

    return redirect(
        "/dashboard"
    )


@app.route(
    "/pay-salary",
    methods=["POST"]
)
@login_required
def pay_salary():

    employee_id = int(
        request.form.get(
            "employee_id"
        )
    )

    amount = float(
        request.form.get(
            "amount"
        )
    )

    admin = Admin.query.first()

    employee = Employee.query.get(
        employee_id
    )

    if not employee:

        flash(
            "Employee Not Found"
        )

        return redirect(
            "/dashboard"
        )

    if amount > admin.balance:

        flash(
            "Insufficient Balance"
        )

        return redirect(
            "/dashboard"
        )

    success, response = send_money(
        employee.phone,
        amount
    )

    if success:

        admin.balance -= amount

        tx = Transaction(
            employee_name=employee.name,
            phone=employee.phone,
            tx_type="SALARY",
            amount=amount,
            status="SUCCESS",
            reference=str(response),
            description="Salary Payment"
        )

        db.session.add(
            tx
        )

        db.session.commit()

        flash(
            "Salary Sent Successfully"
        )

    else:

        tx = Transaction(
            employee_name=employee.name,
            phone=employee.phone,
            tx_type="SALARY",
            amount=amount,
            status="FAILED",
            reference="FAILED",
            description=str(response)
        )

        db.session.add(
            tx
        )

        db.session.commit()

        flash(
            f"Payment Failed: {response}"
        )

    return redirect(
        "/dashboard"
    )


@app.route(
    "/admin-withdraw",
    methods=["POST"]
)
@login_required
def admin_withdraw():

    amount = float(
        request.form.get(
            "amount"
        )
    )

    admin = Admin.query.first()

    if amount > admin.balance:

        flash(
            "Insufficient Balance"
        )

        return redirect(
            "/dashboard"
        )

    admin_phone = os.getenv(
        "ADMIN_PHONE"
    )

    success, response = send_money(
        admin_phone,
        amount
    )

    if success:

        admin.balance -= amount

        tx = Transaction(
            employee_name="ADMIN",
            phone=admin_phone,
            tx_type="ADMIN_WITHDRAWAL",
            amount=amount,
            status="SUCCESS",
            reference=str(response),
            description="Admin Withdrawal"
        )

        db.session.add(
            tx
        )

        db.session.commit()

        flash(
            "Withdrawal Sent Successfully"
        )

    else:

        flash(
            f"Withdrawal Failed: {response}"
        )

    return redirect(
        "/dashboard"
    )


@app.route("/history")
@login_required
def history():

    transactions = Transaction.query.order_by(
        Transaction.id.desc()
    ).all()

    return render_template(
        "history.html",
        transactions=transactions
    )


@app.route(
    "/payment-callback",
    methods=["POST"]
)
def payment_callback():

    data = request.json

    print(
        "PAYMENT CALLBACK:",
        data
    )

    return "OK", 200


@app.route("/health")
def health():

    return {
        "status": "running"
    }


with app.app_context():

    db.create_all()

    admin = Admin.query.filter_by(
        username="admin"
    ).first()

    if not admin:

        admin = Admin(
            username="admin",
            password_hash=generate_password_hash(
                "admin123"
            ),
            phone=os.getenv(
                "ADMIN_PHONE"
            ),
            balance=400000
        )

        db.session.add(
            admin
        )

        db.session.commit()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )