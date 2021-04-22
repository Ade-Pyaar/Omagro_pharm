from flask import render_template, redirect, url_for, flash, request
from sales_project.forms import Regform, Loginform, Updateform, ResetPasswordForm, RequestResetForm
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
        page = request.args.get('page', 1, type=int)
        all_sales = Sales.query.order_by(Sales.date_sold.desc()).paginate(page=page, per_page=7)
        for sale in all_sales.items:
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

        user = User.query.filter_by(name=current_user.name).first()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        if current_user.name == form.name.data and current_user.password != hashed_password:
            User.query.filter_by(name=current_user.name).update({User.password: hashed_password})

        elif current_user.name != form.name.data and current_user.password != hashed_password:
            User.query.filter_by(name=current_user.name).update({User.name: form.name.data, User.password: hashed_password})

        elif current_user.name != form.name.data and current_user.password == hashed_password:
            User.query.filter_by(name=current_user.name).update({User.name: form.name.data}) 
        
        db.session.commit()

        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
        
    elif request.method == 'GET':
        form.name.data = current_user.name
    return render_template('account.html', title='Account', form=form)






@app.route('/account/delete')
def delete_account():

    user = User.query.filter_by(name=current_user.name).first()
    db.session.delete(user)
    db.session.commit()

    flash('Your account has been deleted', 'success')
    return redirect(url_for('login'))






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
    

    if request.method == "POST":
        length = int(len(request.form) / 4)

        for i in range(1, length+1):
            if len(request.form.get('name'+str(i))) != 0:
                item = Products(name=request.form.get('name'+str(i)),
                                quantity=request.form.get('quantity'+str(i)),
                                price=request.form.get('price'+str(i)),
                                expiring_date=request.form.get('expiring_date'+str(i)))
                db.session.add(item)

        db.session.commit()
        flash(f"{length} Product(s) Entered", 'success')
    return render_template('new_product.html', title='Add a new product')






@app.route('/all_product')
@login_required
def all_products():
    if current_user.name != 'Adekunle':
        flash('You are not allowed to access this page', 'danger')
        return redirect(url_for('sales'))

    page = request.args.get('page', 1, type=int)
    all_product = Products.query.order_by(Products.name).paginate(page=page, per_page=10)

    return render_template('all_product.html', title='Sales', all_product=all_product)






@app.route('/product/edit/<string:product_name>/', methods=['GET', 'POST'])
@login_required
def edit_product(product_name):
    if current_user.name != 'Adekunle':
        flash('You are not allowed to access this page', 'danger')
        return redirect(url_for('sales'))

    product = Products.query.filter_by(name=product_name).first()

    if request.method == "POST":
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        expiring_date = request.form.get('expiring_date')

        update_dict = {Products.quantity:quantity, Products.price:price, Products.expiring_date:expiring_date}

        Products.query.filter_by(name=name).update(update_dict)
        db.session.commit()

        flash('You have successfully updated the details', 'success')
        return redirect(url_for('all_products'))

    return render_template('edit_product.html', title='Edit Product', product=product)






@app.route("/product/delete/<string:product_name>/", methods=['POST', 'GET'])
@login_required
def delete_product(product_name):
    product = Products.query.filter_by(name=product_name).first()
    
    db.session.delete(product)
    db.session.commit()

    flash("The product have been deleted successfully", "success")
    return redirect(url_for("all_products"))






@app.route('/sales/previous', methods=['GET', 'POST'])
@login_required
def previous_sales():
    if current_user.name != 'Adekunle':
        flash("You are not allowed to access this page", "danger")
        return redirect(url_for('login'))
    else:
        date = datetime.now().strftime('%Y %m %d')
        page = request.args.get('page', 1, type=int)
        all_sales = Sales.query.order_by(Sales.date_sold.desc()).paginate(page=page, per_page=7)
    return render_template('previous_sales.html', title='Previous Sales', all_sales=all_sales, date=date)






@app.route('/sales/new', methods=["POST", "GET"])
@login_required
def new_sales():
    if current_user.name == 'Adekunle':
        flash("You are not allowed to access the new sales page", 'danger')
        return redirect(url_for('admin'))

    if request.method == "POST":
        length = int(len(request.form) / 3)

        for i in range(1, length+1):
            if len(request.form.get('name'+str(i))) != 0:
                sale = Sales(name_of_item=request.form.get('name'+str(i)),
                            quantity=request.form.get('quantity'+str(i)),
                            price=request.form.get('price'+str(i)),
                            author=current_user)
            db.session.add(sale)
        db.session.commit()
        flash("Sales Entered", 'success')
        
    all_products = Products.query.order_by(Products.name)
    product_dict = {}
    for item in all_products:
        product_dict[item.name] = item.price
    product_str = (product_dict)

    return render_template('new_sales.html', title='New Sales', product_str=product_str)






@app.route('/notifications')
@login_required
def notification():
    if current_user.name != 'Adekunle':
        flash('You are not allowed to access this page', 'danger')
        return redirect(url_for('sales'))

    today = datetime.today().strftime("%Y-%m-%d")
    
    page = request.args.get('page', 1, type=int)
    all_products = Products.query.order_by(Products.name).paginate(page=page, per_page=10)
    final_product = []
    for product in all_products.items:
        end_date = product.expiring_date[:10]
        start_date = datetime.strptime(today, "%Y-%m-%d")
        end_date = datetime.strptime(end_date.replace(' ', '-'), "%Y-%m-%d")

        if (end_date - start_date).days <= 30:
            final_product.append(product.name)

    return render_template('notifications.html', title='Sales', all_products=all_products, final_product=final_product)