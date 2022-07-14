
import os

from flask import Flask, jsonify, request, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields

dotenv.load_dotenv()

db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')

DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'\
        .format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()


@app.route('/', methods = ['GET'])
def home():
    return render_template("index.html"), 200


@app.route('/api', methods = ['GET'])
def api_main():
    return send_file('api_doc.json'), 200


@app.route('/api/students', methods=['GET'])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200


@app.route('/api/students/get/<int:id>', methods = ['GET'])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200


@app.route('/api/students/add', methods = ['POST'])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name= json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201


@app.route('/api/students/modify/<int:id>', methods = ['PATCH'])
def modify_student(id):
    student = Student.get_by_id(id)
    student_json = request.get_json()
    if student_json.get('name'):
        student.name = student_json.get('name')
    if student_json.get('email'):
        student.email = student_json.get('email')
    if student_json.get('age'):
        student.age = student_json.get('age')
    if student_json.get('cellphone'):
        student.cellphone = student_json.get('cellphone')
    try:
        db.session.commit()
    except:
        return jsonify("Something went wrong!"), 500
    serializer = StudentSchema()
    data = serializer.dump(student)
    return jsonify(data), 200


@app.route('/api/students/change/<int:id>', methods = ['PUT'])
def change_student(id):
    student = Student.get_by_id(id)
    student_json = request.get_json()
    if not student_json:
        return {'message': 'Wrong data'}, 400
    student.name=student_json.get('name'),
    student.email=student_json.get('email'),
    student.age=student_json.get('age'),
    student.cellphone=student_json.get('cellphone')
    try:
        db.session.commit()
    except:
        return jsonify("Something went wrong!"), 500
    serializer = StudentSchema()
    data = serializer.dump(student)
    return data, 200


@app.route('/api/students/delete/<int:id>', methods = ['DELETE'])
def del_student(id):
    student = Student.get_by_id(id)
    if not student:
        return "", 404
    student.delete()
    return "", 204


@app.route('/api/health-check/ok', methods = ['GET'])
def health_check_ok():
    return {'message': 'Ok'}, 200


@app.route('/api/health-check/bad', methods = ['GET'])
def health_check_bad():
    return "", 500


if __name__ == '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(debug=True, host="0.0.0.0")
