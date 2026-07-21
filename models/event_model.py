from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from models.base_model import Base

class Event(Base):
    """Représente un événement dans la base de données."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    attendees = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", back_populates="events")
    support_representative_id = Column(Integer, ForeignKey("collaborators.id"), nullable=True)
    support_representative = relationship("Collaborator", back_populates="events")
    contract_id = Column(Integer, ForeignKey("contracts.id"), unique=True, nullable=False)
    contract = relationship("Contract", back_populates="event")

class Location(Base):
    """Représente un lieu associé à un événement dans la base de données."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    street_number = Column(String(10), nullable=False)
    street_name = Column(String(100), nullable=False)
    zip_code = Column(String(10), nullable=False)
    city = Column(String(50), nullable=False)
    events = relationship("Event", back_populates="location")