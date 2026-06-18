import os
from flask import Flask, render_template, request, redirect, flash

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
    Transaction,
    WithdrawalRequest
)

from routes.ussd import ussd_bp

from services.mobile_money import (
    send_money
)

# Initialize Flask and force absolute path for templates folder to prevent Windows errors
base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(ussd_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect("/dashboard")

        flash("Invalid Login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/dashboard")
@login_required
def dashboard():
    admin = Admin.query.first()
    employees = Employee.query.all()
    
    # Matches the exact filtering logic your loop expects
    requests = WithdrawalRequest.query.filter_by(status="PENDING").all()

    return render_template(
        "dashboard.html",
        admin=admin,
        employees=employees,
        requests=requests
    )


@app.route("/add-employee", methods=["POST"])
@login_required
def add_employee():
    name = request.form.get("name")
    phone = request.form.get("phone")

    # Creates employee with a base balance of 0
    employee = Employee(name=name, phone=phone, balance=0.0)

    db.session.add(employee)
    db.session.commit()

    flash("Employee Added")
    return redirect("/dashboard")


@app.route("/refill", methods=["POST"])
@login_required
def refill():
    amount = float(request.form.get("amount"))

    admin = Admin.query.first()
    admin.balance += amount

    tx = Transaction(
        tx_type="REFILL",
        amount=amount,
        status="SUCCESS",
        description="Admin Refill"
    )

    db.session.add(tx)
    db.session.commit()

    flash("Balance Refilled")
    return redirect("/dashboard")


@app.route("/pay-salary", methods=["POST"])
@login_required
def pay_salary():
    employee_id = int(request.form.get("employee_id"))
    amount = float(request.form.get("amount"))

    admin = Admin.query.first()
    employee = Employee.query.get(employee_id)

    if amount > admin.balance:
        flash("Insufficient System Balance")
        return redirect("/dashboard")

    admin.balance -= amount
    employee.balance += amount

    tx = Transaction(
        employee_id=employee.id,
        tx_type="SALARY",
        amount=amount,
        status="SUCCESS",
        description="Salary Payment"
    )

    db.session.add(tx)
    db.session.commit()

    flash("Salary Paid")
    return redirect("/dashboard")


@app.route("/approve/<int:req_id>")
@login_required
def approve(req_id):
    withdrawal = WithdrawalRequest.query.get(req_id)

    if not withdrawal:
        flash("Request Not Found")
        return redirect("/dashboard")

    employee = Employee.query.get(withdrawal.employee_id)
    admin = Admin.query.first()

    if withdrawal.amount > employee.balance:
        flash("Employee Balance Too Low")
        return redirect("/dashboard")

    if withdrawal.amount > admin.balance:
        flash("System Balance Too Low")
        return redirect("/dashboard")

    # Send the real money using Africa's Talking
    success, response = send_money(employee.phone, withdrawal.amount)

    if success:
        employee.balance -= withdrawal.amount
        admin.balance -= withdrawal.amount
        withdrawal.status = "APPROVED"

        tx = Transaction(
            employee_id=employee.id,
            tx_type="WITHDRAWAL",
            amount=withdrawal.amount,
            status="SUCCESS",
            description="USSD Withdrawal"
        )

        db.session.add(tx)
        db.session.commit()
        flash("Withdrawal Approved")
    else:
        flash(str(response))

    return redirect("/dashboard")


@app.route("/reject/<int:req_id>")
@login_required
def reject(req_id):
    withdrawal = WithdrawalRequest.query.get(req_id)

    if withdrawal:
        withdrawal.status = "REJECTED"
        db.session.commit()

    flash("Request Rejected")
    return redirect("/dashboard")


# Create database schemas and seed initial admin credentials on boot
with app.app_context():
    db.create_all()

    admin = Admin.query.filter_by(username="admin").first()
    if not admin:
        admin = Admin(
            username="admin",
            password_hash=generate_password_hash("admin123"),
            balance=400000.0
        )
        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)