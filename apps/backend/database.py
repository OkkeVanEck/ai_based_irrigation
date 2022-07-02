import json
import os
import zlib

from sqlalchemy import create_engine, Column, String, DateTime, Integer, TypeDecorator, LargeBinary
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME', 'local')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'local')

Base = declarative_base()

print(f"postgresql://{POSTGRES_USERNAME}:{quote_plus(POSTGRES_PASSWORD)}@"
                       f"{POSTGRES_HOST}/lucas-test?sslmode=require")
engine = create_engine(f"postgresql://{POSTGRES_USERNAME}:{quote_plus(POSTGRES_PASSWORD)}@"
                       f"{POSTGRES_HOST}/lucas-test?sslmode=require")

Session = sessionmaker(bind=engine)


class CustomLargeBinary(TypeDecorator):
    """We need this class to decode and encode the dictionaries to bytes"""
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        return zlib.compress(json.dumps(value).encode('utf-8'))

    def process_result_value(self, value, dialect):
        return json.loads(zlib.decompress(value).decode('utf-8'))

    def coerce_compared_value(self, op, value):
        return self.impl.coerce_compared_value(op, value)


class Simulation(Base):
    """ORM class for the featured results"""
    __tablename__ = 'simulations'

    id = Column(String, autoincrement=False, primary_key=True)
    mac_address = Column(String, nullable=False)
    crop_type = Column(String, nullable=False)
    crop_stage = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    max_water = Column(Integer, nullable=False)
    field_size = Column(Integer, nullable=False)
    schedule = Column(MutableDict.as_mutable(CustomLargeBinary), nullable=True)
    harvest_date = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'mac_address': self.mac_address,
            'crop_type': self.crop_type,
            'crop_stage': self.crop_stage,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'max_water': self.max_water,
            'field_size': self.field_size,
            'schedule': self.schedule,
            'harvest_date': self.harvest_date
        }


def init_database():
    """ Initialize the database """
    Base.metadata.create_all(engine)


def create_simulation(session, sim: Simulation):
    existing_sim = session.query(Simulation). \
        filter(Simulation.id == sim.id).one_or_none()

    if existing_sim:
        # If the data is the same as present in the database
        setattr(existing_sim, 'id', sim.id)
        setattr(existing_sim, 'mac_address', sim.mac_address)
        setattr(existing_sim, 'crop_type', sim.crop_type)
        setattr(existing_sim, 'crop_stage', sim.crop_stage)
        setattr(existing_sim, 'start_date', sim.start_date)
        setattr(existing_sim, 'end_date', sim.end_date)
        setattr(existing_sim, 'max_water', sim.max_water)
        setattr(existing_sim, 'field_size', sim.field_size)
        setattr(existing_sim, 'schedule', sim.schedule)
        setattr(existing_sim, 'harvest_date', sim.harvest_date)

        session.add(existing_sim)
        session.commit()
        return sim.id
    else:
        session.add(sim)
        session.commit()
        return sim.id


def get_all_simulations(session, mac_address):
    return session.query(Simulation). \
        filter(Simulation.mac_address == mac_address).all()


def get_simulation(session, id_):
    return session.query(Simulation). \
        filter(Simulation.id == id_).one_or_none()


def delete_featured_results(session, id_):
    sim = get_simulation(session, id_)

    if sim:
        session.delete(id_)
        session.commit()
        return "Deleted featured result"
    else:
        return "Document not found"
