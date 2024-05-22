from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask import jsonify
import random
'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        #Method 1. 
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        
        #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all")
def all_record():
    records = Cafe.query.all()
    record=[data.to_dict() for data in records]
    return jsonify(data={'Records':record})

@app.route("/random")
def random_record():
    # id=request.args.get('id')
    # print(id)
    records = Cafe.query.all()
    r_record=random.choice(records)
    return jsonify({'Random':r_record.to_dict()})
# HTTP POST - Create Record
@app.route("/add",methods=['POST','GET'])
def add_record():
    if request.method=='POST':
        name=request.form.get("name")
        map=request.form.get("mapurl")
        img=request.form.get("imageurl")
        location=request.form.get("location")
        seats=request.form.get("seats")
        toilets=bool(request.form.get("toilets"))
        wifi=bool(request.form.get("wifi"))
        sockets=bool(request.form.get("sockets"))
        takecalls=bool(request.form.get("takecalls"))
        price=request.form.get("price")
    
        d=Cafe(name=name,map_url=map,img_url=img,location=location,seats=seats,has_toilet=toilets,has_wifi=wifi,has_sockets=sockets,can_take_calls=takecalls,coffee_price=price)
        db.session.add(d)
        db.session.commit()
        return jsonify(msg={'Message':'Data Inserted'})
    return render_template("add.html")

# HTTP GET - Read Record
@app.route("/search")
def read_record():
    query_location = request.args.get("loc")
    result = (db.session.execute(db.select(Cafe).where(Cafe.location == query_location))).scalars().all()
    # Note, this may get more than one cafe per location

    if result:
        return jsonify({'Read_Record':[r.to_dict() for r in result]})
    else:
        return jsonify({'Read_Record':f'No Record Found for {query_location}'})


# HTTP PUT/PATCH - Update Record
@app.route("/update/<int:id>",methods=['POST','GET'])
def update_record(id):
    # id=request.args.get('id')
    record=(db.session.execute(db.select(Cafe).where(Cafe.id==id))).scalar()
    if request.method=='POST':
        record.name=request.form.get("name")
        record.map_url=request.form.get("mapurl")
        record.img_url=request.form.get("imageurl")
        record.location=request.form.get("location")
        record.seats=request.form.get("seats")
        record.has_toilets=bool(request.form.get("toilets"))
        record.has_wifi=bool(request.form.get("wifi"))
        record.has_sockets=bool(request.form.get("sockets"))
        record.can_take_calls=bool(request.form.get("takecalls"))
        record.coffee_price=request.form.get("price")
        
        db.session.commit()
        return jsonify({'Message':'Data Updated Successfully'})
    return render_template("update.html",data=record,id=id)
# HTTP DELETE - Delete Record
@app.route('/delete/<int:id>')
def erase(id):
    apiKey=request.args.get('api-key')
    data = Cafe.query.get(id)
    if data:
        if apiKey=='DeleteKrDo':
            db.session.delete(data)
            db.session.commit()
            return jsonify({'Success':f'Record with id {id} Deleted.'})
        else:
    
         return jsonify({'Not Allows':'Secret Key is Incorrect You are not allowed to Delete Record '})
    else:
        return jsonify({'Failed':f'Record with id {id} does not exist'})
    
        
   

if __name__ == '__main__':
    app.run(debug=True)
