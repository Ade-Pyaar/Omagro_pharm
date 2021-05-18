from datetime import datetime
from sales_project import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    add_product = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # sales = db.relationship('Sales', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.name}')"


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_of_item = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # seller = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.Column(db.String(30), nullable=False)
    date_sold = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"Sale('{self.name_of_item}', '{self.date_sold}', '{self.quantity}', '{self.price}')"


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    expiring_date = db.Column(db.String(12), nullable=False)
    quantity_to_alert = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"