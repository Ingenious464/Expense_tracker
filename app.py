from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    category = db.relationship('Category', backref='expenses')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        new_expense = Expense(amount=amount, category=category)
        db.session.add(new_expense)
        db.session.commit()
      #  expenses.append({'amount': amount, 'category': category})

    expenses = Expense.query.all()
    return render_template('index.html', expenses=expenses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    category_name = request.form.get('category_name')
    new_category = Category(name=category_name)
    db.session.add(new_category)
    db.session.commit()
    flash(f'Category "{category_name}" added successfully.', 'success')
    return redirect(url_for('categories'))
# ... (other routes remain unchanged)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Implement user login logic here
    if request.method == 'POST':
        # Handle form submission and user login
        flash('Login successful.', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    # Implement expense editing logic here
    expense = Expense.query.get_or_404(expense_id)
    if current_user != expense.user:
        abort(403)  # User is not authorized to edit this expense

    if request.method == 'POST':
        # Handle form submission and update expense
        flash('Expense updated successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('edit_expense.html', expense=expense)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    # Implement expense deletion logic here
    expense = Expense.query.get_or_404(expense_id)
    if current_user != expense.user:
        abort(403)  # User is not authorized to delete this expense

    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    # Implement user profile logic here

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
