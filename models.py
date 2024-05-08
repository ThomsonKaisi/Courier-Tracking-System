from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    bio = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    address = relationship("Address", back_populates="user", uselist=False)
    parcels_sent = relationship("Parcel", foreign_keys="Parcel.sender_id", back_populates="sender")
    parcels_received = relationship("Parcel", foreign_keys="Parcel.receiver_id", back_populates="receiver")

class Address(Base):
    __tablename__ = "Address"
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(50), index=True)
    box_number = Column(Integer, index=True)
    area = Column(String(100), index=True)
    description = Column(String(100), index=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship("User", back_populates="address")

class Parcel(Base):
    __tablename__ = "Parcel"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(100), index=True)
    sender_id = Column(Integer, ForeignKey('User.id'))
    receiver_id = Column(Integer, ForeignKey('User.id'))
    source_id = Column(Integer, ForeignKey('Station.id'))
    destination_id = Column(Integer, ForeignKey('Station.id'))

    sender = relationship("User", foreign_keys=[sender_id], back_populates="parcels_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="parcels_received")
    source = relationship("Station", foreign_keys=[source_id], back_populates="parcels_departed")
    destination = relationship("Station", foreign_keys=[destination_id], back_populates="parcels_arrived")

class Admin(User):
    __tablename__ = "Admin"
    
    id = Column(Integer, ForeignKey('User.id'), primary_key=True)
    position = Column(String(30), index=True)
    station_id = Column(Integer, ForeignKey('Station.id'))
    station = relationship("Station", back_populates="admins")

class Station(Base):
    __tablename__ = "Station"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    parcels_departed = relationship("Parcel", foreign_keys="Parcel.source_id", back_populates="source")
    parcels_arrived = relationship("Parcel", foreign_keys="Parcel.destination_id", back_populates="destination")
    admins = relationship("Admin", back_populates="station")
