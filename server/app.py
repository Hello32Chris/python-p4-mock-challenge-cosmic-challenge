#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

#  ALL SCIENTISTS

@app.route('/scientists', methods = ['GET', 'POST'])
def scientists():
    if request.method == 'GET':
        scientists = Scientist.query.all()
        scientist = [scientist.to_dict(rules = ('-missions', )) for scientist in scientists]
        resp = make_response(scientist, 200)
        return resp
    elif request.method == 'POST':
        form_data = request.get_json()
        try:
            new_scientist_obj = Scientist(
                name = form_data['name'],
                field_of_study = form_data['field_of_study']
            )
            db.session.add(new_scientist_obj)
            db.session.commit()
            resp = make_response(new_scientist_obj.to_dict(), 201)
        except ValueError:
            resp = make_response({"errors": ["validation errors"]}, 400)
            return resp
    return resp

#  SCIENTIST BY ID

@app.route('/scientists/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def scientist(id):
    scientist = Scientist.query.filter_by(id = id).first()
    if scientist:
        if request.method == 'GET':
            resp = make_response(scientist.to_dict(), 200)
        elif request.method == 'PATCH':
            form_data = request.get_json()
            try:
                for attr in form_data:
                    setattr(scientist, attr, form_data.get(attr))
                db.session.commit()
                resp = make_response(scientist.to_dict(), 202)
            except ValueError:
                resp = make_response({"errors": ["validation errors"]}, 400)
                return resp
        elif request.method == 'DELETE':
            db.session.delete(scientist)
            db.session.commit()
            resp = make_response({}, 204)
    else:
        resp = make_response({"error": "Scientist not found"}, 404)
        return resp
    return resp

#  ALL MISSIONS

@app.route('/missions', methods = ['POST'])
def missions():
    form_data = request.get_json()
    try:
        new_missions_obj = Mission(
            name = form_data['name'],
            scientist_id = form_data['scientist_id'],
            planet_id = form_data['planet_id']
        )
        db.session.add(new_missions_obj)
        db.session.commit()
        resp = make_response(new_missions_obj.to_dict(), 201)
        return resp
    except ValueError:
        resp = make_response({"errors": ["validation errors"]}, 400)
    return resp


#  ALL PLANETS

@app.route('/planets', methods = ['GET'])
def planets():
    planets = Planet.query.all()
    planet_dict = [planet.to_dict(rules = ('-missions', )) for planet in planets]
    resp = make_response(planet_dict, 200)
    return resp


if __name__ == '__main__':
    app.run(port=5555, debug=True)
