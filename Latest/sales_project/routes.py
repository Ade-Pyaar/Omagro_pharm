from flask import render_template, redirect, url_for, flash, request
from sales_project.forms import Regform, Loginform, Updateform, ResetPasswordForm, RequestResetForm, EditProductForm, NewProductForm
from sales_project.models import User, Sales, Products
from sales_project import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route('/admin_login', methods=['POST', 'GET'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = Loginform()
    if form.validate_on_submit():
        if form.name.data == 'Adekunle':
            user = User.query.filter_by(name=form.name.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f"Welcome Admin: {form.name.data}!", 'success')
                return redirect(url_for('admin'))
            else:
                flash('Login unsuccessful, please check the name and password', 'danger')
        else:
            flash('You are not allowed to login here, go to the login page', 'danger')
    return render_template('admin_login.html', title='Admin Login', form=form)


@app.route('/admin')
@login_required
def admin():
    if current_user.name != 'Adekunle':
        flash("You are not allowed to access this page", "danger")
        return redirect(url_for('login'))
    else:
        date = datetime.now().strftime('%Y %m %d')
        total_money, number = 0, 0
        all_sales = Sales.query.all()
        for sale in all_sales:
            if sale.date_sold.strftime('%Y %m %d') == date:
                number += 1
                total_money += sale.price
    return render_template('admin.html', title='Admin Page', number=number, all_sales=all_sales, total_money=total_money, date=date)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('sales'))
    form = Regform()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.name.data}, you can now login ", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('sales'))
    form = Loginform()
    if form.validate_on_submit():
        if form.name.data == 'Adekunle':
            flash("You can't login there, login here", 'danger')
            return redirect(url_for('admin_login'))
        else:
            user = User.query.filter_by(name=form.name.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f"Welcome {form.name.data}!", 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('sales'))
            else:
                flash('Login unsuccessful, please check the name and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/account', methods=['POST', 'GET'])
def account():
    form = Updateform()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
    return render_template('account.html', title='Account', form=form)


@app.route('/sales')
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    all_sales = Sales.query.order_by(Sales.date_sold.desc()).paginate(page=page, per_page=7)
    return render_template('sales.html', title='Sales', all_sales=all_sales)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        return redirect(url_for('reset_token', token=user.name))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.query.filter_by(name=token).first()
    if user is None:
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated! You can now login', 'Success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if current_user.name != 'Adekunle':
        flash('You are not allowed to access this page', 'danger')
        return redirect(url_for('sales'))
    else:
        form = NewProductForm()
        if form.validate_on_submit():
            item = Products(name_of_product=form.name.data, price=form.price.data)
            db.session.add(item)
            db.session.commit()
            flash("A new product have been added", 'success')
            return redirect(url_for('new_product'))
    return render_template('new_product.html', title='Add a new product', form=form)


@app.route('/product/edit', methods=['GET', 'POST'])
@login_required
def edit_product():
    if current_user.name != 'Adekunle':
        flash('You are not allowed to access this page', 'danger')
        return redirect(url_for('sales'))
    return render_template('edit_product.html', title='Edit Product')


@app.route('/sales/previous', methods=['GET', 'POST'])
@login_required
def previous_sales():
    if current_user.name != 'Adekunle':
        flash('You are not allowed to access this page', 'danger')
        return redirect(url_for('sales'))
    return render_template('edit_product.html', title='Edit Product')


@app.route('/sales/new')
@login_required
def new_sales():
    if current_user.name == 'Adekunle':
        flash("You are not allowed to access the new sales page", 'danger')
        return redirect(url_for('admin'))
    else:
        if request.args.get('name1') is not None:
            for i in range(1, int(request.args.get('field'))+1):
                sale = Sales(name_of_item=request.args.get('name'+str(i)), quantity=request.args.get('quantity'+str(i)), price=request.args.get('price'+str(i)),
                             author=current_user)
                db.session.add(sale)
                db.session.commit()
            flash("Your sale has been entered", 'success')
            return redirect(url_for('sales'))
    products = Products.query.all()
    return render_template('name.html', title='New Sales', products=products)