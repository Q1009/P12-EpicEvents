from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from main.base_model import Base


class Event(Base):
    """Represents an event in the EpicEvents CRM database.

    Stores comprehensive information about events including scheduling details,
    attendance, location, associated contract, and assigned support representative.

    :cvar id: Unique identifier for the event, auto-incremented.
    :vartype id: int
    :cvar name: Name or title of the event, maximum 100 characters.
    :vartype name: str
    :cvar start_date: Date and time when the event begins (UTC).
    :vartype start_date: datetime
    :cvar end_date: Date and time when the event ends (UTC).
    :vartype end_date: datetime
    :cvar attendees: Number of attendees expected at the event.
    :vartype attendees: int
    :cvar description: Detailed description or notes about the event.
    :vartype description: str | None
    :cvar location_id: Foreign key reference to the associated location.
    :vartype location_id: int
    :cvar location: One-to-many relationship with Location model.
        An event has exactly one location.
    :vartype location: Location
    :cvar support_representative_id: Foreign key reference to the assigned
        support representative. Can be null if no representative is assigned.
    :vartype support_representative_id: int | None
    :cvar support_representative: Many-to-one relationship with Collaborator model.
        Represents the collaborator assigned as support for this event.
    :vartype support_representative: Collaborator | None
    :cvar contract_id: Foreign key reference to the associated contract.
        Must be unique as each contract can have only one event.
    :vartype contract_id: int
    :cvar contract: One-to-one relationship with Contract model.
        Each event is associated with exactly one contract.
    :vartype contract: Contract

    .. note::
        The contract_id has a unique constraint, enforcing a one-to-one
        relationship between contracts and events.
    """

    __tablename__ = "events"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(100), nullable=False)
    start_date: DateTime = Column(DateTime, nullable=False)
    end_date: DateTime = Column(DateTime, nullable=False)
    attendees: int = Column(Integer, nullable=False)
    description: str | None = Column(Text, nullable=True)
    location_id: int = Column(
        Integer,
        ForeignKey("locations.id", name="fk_event_location"),
        nullable=False,
    )
    location = relationship("Location", back_populates="events")
    support_representative_id: int | None = Column(
        Integer,
        ForeignKey(
            "collaborators.id", name="fk_event_support_representative"
        ),
        nullable=True,
    )
    support_representative = relationship(
        "Collaborator", back_populates="events"
    )
    contract_id: int = Column(
        Integer,
        ForeignKey("contracts.id", name="fk_event_contract"),
        unique=True,
        nullable=False,
    )
    contract = relationship("Contract", back_populates="event")


class Location(Base):
    """Represents a physical location in the EpicEvents CRM database.

    Stores address information for locations where events can take place.
    A location can be associated with multiple events.

    :cvar id: Unique identifier for the location, auto-incremented.
    :vartype id: int
    :cvar name: Descriptive name for the location, maximum 100 characters.
        Can be null.
    :vartype name: str | None
    :cvar street_number: Street number portion of the address.
    :vartype street_number: str
    :cvar street_name: Name of the street.
    :vartype street_name: str
    :cvar zip_code: Postal code for the location.
    :vartype zip_code: str
    :cvar city: City where the location is situated.
    :vartype city: str
    :cvar events: One-to-many relationship with Event model.
        A location can be associated with multiple events.
    :vartype events: list[Event]

    .. note::
        The street_number, street_name, zip_code, and city fields are all
        required (non-nullable) to ensure complete address information.
    """

    __tablename__ = "locations"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str | None = Column(String(100), nullable=True)
    street_number: str = Column(String(10), nullable=False)
    street_name: str = Column(String(100), nullable=False)
    zip_code: str = Column(String(10), nullable=False)
    city: str = Column(String(50), nullable=False)
    events = relationship("Event", back_populates="location")
