import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_database, Session, Simulation,\
    get_all_simulations, get_simulation, create_simulation

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


@app.route("/create-simulation", methods=['POST'])
def create_update_simulation():
    sim = Simulation(id=str(uuid.uuid4()), mac_address=request.remote_addr, **request.json)

    # ip = request.remote_addr
    # crop_type = request.form.get('crop_type')
    # crop_stage = request.form.get('crop_stage')
    # start_date = request.form.get('start_date')
    # end_date = request.form.get('end_date')
    # max_water = request.form.get('max_water')
    # field_size = request.form.get('field_size')

    with Session() as session:
        return jsonify(create_simulation(session, sim))


if __name__ == '__main__':
    init_database()
    app.run(port=5555)
