from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from main.base_model import Base


class Event(Base):
    """Represents an event in the database."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    attendees = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id", name="fk_event_location"), nullable=False)
    location = relationship("Location", back_populates="events")
    support_representative_id = Column(Integer, ForeignKey("collaborators.id", name="fk_event_support_representative"), nullable=True)
    support_representative = relationship("Collaborator", back_populates="events")
    contract_id = Column(Integer, ForeignKey("contracts.id", name="fk_event_contract"), unique=True, nullable=False)
    contract = relationship("Contract", back_populates="event")

class Location(Base):
    """Represents a location associated to an event in the database."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    street_number = Column(String(10), nullable=False)
    street_name = Column(String(100), nullable=False)
    zip_code = Column(String(10), nullable=False)
    city = Column(String(50), nullable=False)
    events = relationship("Event", back_populates="location")