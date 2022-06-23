import os
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME', 'local')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'local')

Base = declarative_base()

engine = create_engine(f"postgresql://{POSTGRES_USERNAME}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}/irr-db")

Session = sessionmaker(bind=engine)


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

    @property
    def serialize(self):
        return {
            'id': self.id,
            'mac_address': self.mac_address,
            'crop_type': self.crop_type,
            'crop_stage': self.crop_stage,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'max_water': self.max_water,
            'field_size': self.field_size
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

        session.add(existing_sim)
        session.commit()
        return "Featured result updated."
    else:
        session.add(sim)
        session.commit()
        return "Added featured result."


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
