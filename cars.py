import os
import csv
from peewee import *
from flask import Flask, render_template, request, url_for, redirect, flash

app = Flask(__name__)
app.secret_key = '301298'

global appType 
appType = 'Monolith'

database = SqliteDatabase('carsweb.db')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class BaseModel(Model):
     class Meta:
        database = database

class TBCars(BaseModel):
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()

def create_tables():
    with database:
        database.create_tables([TBCars])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def indeks():
    return render_template('index.html', appType=appType)

@app.route('/createcar')
def createcar():
    return render_template('createcar.html', appType=appType)

@app.route('/createcarsave',methods=['GET','POST'])
def createcarsave():
    fName = request.form['carName']
    fBrand = request.form['carBrand']
    fModel = request.form['carModel']
    fPrice = request.form['carPrice']

    viewData = {
        "name" : fName,
        "brand" : fBrand,
        "model" : fModel,
        "price" : fPrice 
    }

    #simpan di DB
    car_simpan = TBCars.create(
        carname = fName,
        carbrand = fBrand,
        carmodel = fModel,
        carprice = fPrice
        )
    return redirect(url_for('readcar'))

@app.route('/readcar')
def readcar():
    rows = TBCars.select()
    return render_template('readcar.html', rows=rows, appType=appType)

@app.route('/updatecar', methods=['GET', 'POST'])
def updatecar():
    if request.method == 'GET':
        cars = TBCars.select()
        return render_template('updatecar.html', cars=cars, appType=appType)
    
@app.route('/updatecarsave', methods=['POST'])
def updatecarsave():
    car_id = request.form['carID']
    fName = request.form['carName']
    fBrand = request.form['carBrand']
    fModel = request.form['carModel']
    fPrice = request.form['carPrice']
    
    car_to_update = TBCars.get(TBCars.id == car_id)
    car_to_update.carname = fName
    car_to_update.carbrand = fBrand
    car_to_update.carmodel = fModel
    car_to_update.carprice = fPrice
    car_to_update.save()
    
    return redirect(url_for('readcar'))

@app.route('/deletecar')
def deletecar():
    return render_template('deletecar.html', appType=appType)

@app.route('/deletecarsave', methods=['GET','POST'])
def deletecarsave():
    fName = request.form['carName']
    car_delete = TBCars.delete().where(TBCars.carname==fName)
    car_delete.execute()
    return redirect(url_for('readcar'))

@app.route('/searchcar', methods=['GET', 'POST'])
def searchcar():
    return render_template('searchcar.html', appType=appType)

@app.route('/searchcarresults', methods=['POST'])
def searchcarresults():
    search_query = request.form['searchQuery']
    
    results = TBCars.select().where(
        (TBCars.id.contains(search_query)) |
        (TBCars.carname.contains(search_query)) |
        (TBCars.carbrand.contains(search_query)) |
        (TBCars.carmodel.contains(search_query)) |
        (TBCars.carprice.contains(search_query))
    )
    
    return render_template('searchcar.html', results=results, searchQuery=search_query, appType=appType)

@app.route('/help')
def help():
    return "ini halaman Helps"

@app.route('/importcsv')
def importcsv():
    return render_template('importcsv.html', appType=appType)

@app.route('/importcsvsave', methods=['POST'])
def importcsvsave():
    if 'csvFile' not in request.files:
        flash('No file part found.')
        return redirect(url_for('importcsv'))

    file = request.files['csvFile']

    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('importcsv'))

    if file.filename.endswith('.csv'):
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Import CSV data to database
            with open(filepath, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print(f"Importing row: {row}")  # Debug log
                    TBCars.create(
                        carname=row['carname'],
                        carbrand=row['carbrand'],
                        carmodel=row['carmodel'],
                        carprice=row['carprice']
                    )

            flash('CSV file imported successfully.')
        except Exception as e:
            flash(f'An error occurred: {e}')
    else:
        flash('Invalid file type. Please upload a CSV file.')
    return redirect(url_for('readcar'))

if __name__ == '__main__':
    create_tables()
    app.run(
        port =5010,
        host='0.0.0.0',
        debug = True
        )


