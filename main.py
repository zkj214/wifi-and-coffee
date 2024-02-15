from flask import Flask,render_template,redirect,url_for,request,jsonify
from flask_bootstrap import Bootstrap5  #pip install bootstrap-flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL
import os

app=Flask(__name__)
app.config["SECRET_KEY"]=os.environ.get("FLASK_KEY")

bootstrap=Bootstrap5(app)

app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DB_URI","sqlite:///cafes.db")
db=SQLAlchemy()
db.init_app(app)


class Cafe(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)
    map_url=db.Column(db.String(200),nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False,default=True)
    has_toilet = db.Column(db.Boolean, nullable=False, default=True)
    has_wifi = db.Column(db.Boolean, nullable=False, default=True)
    can_take_calls = db.Column(db.Boolean, nullable=False, default=True)
    seats=db.Column(db.String(20),nullable=False)
    coffee_price=db.Column(db.String(16),nullable=False)


with app.app_context():
    db.create_all()


class AddCafeForm(FlaskForm):
    name=StringField("Cafe Name:",validators=[DataRequired()])
    map_url = StringField("Location Map:", validators=[DataRequired(),URL()])
    img_url = StringField("Image Link:", validators=[DataRequired(),URL()])
    location = StringField("Location:", validators=[DataRequired()])
    has_sockets = BooleanField("Does it have sockets?",default=False)
    has_toilet = BooleanField("Does it have a toilet?", default=False)
    has_wifi = BooleanField("Does it have Wifi?", default=False)
    can_take_calls = BooleanField("Can it take calls?", default=False)
    seats=SelectField("Seat Capacity:",validators=[DataRequired()],choices=["0-10","10-20","20-30","30-40","40-50","50+"])
    coffee_price=StringField("Standard Coffee Price:",validators=[DataRequired()])
    submit=SubmitField("Add")


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/show_all_cafes")
def display_cafes():
    result=db.session.execute(db.select(Cafe))
    all_cafes=list(result.scalars())
    return render_template("cafes.html",cafes=all_cafes)


@app.route("/add-cafe",methods=["GET","POST"])
def add_cafe():
    add_form=AddCafeForm()

    if add_form.validate_on_submit():
        new_cafe=Cafe(name=add_form.name.data,map_url=add_form.map_url.data,img_url=add_form.img_url.data,location=add_form.location.data,
                      has_sockets=bool(add_form.has_sockets.data),has_toilet=bool(add_form.has_toilet.data),has_wifi=bool(add_form.has_wifi.data),can_take_calls=bool(add_form.can_take_calls.data),
             seats=add_form.seats.data,coffee_price=add_form.coffee_price.data)
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('display_cafes'))

    return render_template("add.html",form=add_form)


@app.route("/closed-cafe/<int:cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key=request.args.get("api-key")
    cafe=db.session.execute(db.select(Cafe).where(Cafe.id==cafe_id)).scalar()

    if api_key==os.environ.get("API_KEY"):
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success":"The cafe is successfully deleted from the database."}),200
        else:
            return jsonify(response={"error":"Sorry, the id is not found in the database."}),404
    else:
        return jsonify(response={"Not allowed":"The key that you typed is incorrect. Pls try again."}),403


@app.route("/update-cafe/<int:cafe_id>",methods=["PATCH"])
def update_cafe(cafe_id):
    updated_price=request.args.get("new_price")
    cafe=db.session.execute(db.select(Cafe).where(Cafe.id==cafe_id)).scalar()

    if cafe:
        cafe.coffee_price=updated_price
        db.session.commit()
        return jsonify(response={"success":"The coffee price has been successfully updated."}),200
    else:
        return jsonify(response={"error":"Sorry, the id that you entered is not found in the database."}),404


if __name__=="__main__":
    app.run(debug=True)