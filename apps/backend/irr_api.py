import uuid
from http.client import BAD_REQUEST

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_database, Session, Simulation,\
    get_all_simulations, get_simulation, create_simulation
from irr_simulations import find_best_schedule
from aquacrop.entities.crops.crop_params import crop_params
from sys import platform

app = Flask(__name__)
CORS(app)


@app.route("/get-simulations")
def get_simulations():
    with Session() as session:
        sims = get_all_simulations(session, request.remote_addr)
        return jsonify([s.to_dict() for s in sims])


@app.route("/get-simulation/<uid>")
def get_simulation_by_id(uid):
    with Session() as session:
        sim = get_simulation(session, uid)
        return jsonify(sim.to_dict())


@app.route("/get-crop-harvest/<crop>")
def get_crop_harvest(crop):
    return jsonify(int(crop_params[crop]['MaturityCD']))


@app.route("/create-simulation", methods=['POST'])
def create_update_simulation():
    try:
        ip = request.remote_addr
        start_date = request.json['start_date']
        end_date = request.json['end_date']
        crop_type = request.json['crop_type']
        crop_stage = request.json['crop_stage']
        field_size = request.json['field_size']
        max_water = request.json['max_water']
    except Exception as e:
        return BAD_REQUEST

    opt_schedule, harvest_date = find_best_schedule(start=start_date, end=end_date, crop=crop_type,
                                                    field_size=int(field_size), max_irr_liters=int(max_water))
    sim = Simulation(id=str(uuid.uuid4()), mac_address=ip, schedule=opt_schedule.Liters.to_dict(),
                     harvest_date=str(harvest_date), **request.json)

    with Session() as session:
        return jsonify(create_simulation(session, sim))


if platform != 'win32' or __name__ == "__main__":
    init_database()
    app.run(host='0.0.0.0', port=5555)
