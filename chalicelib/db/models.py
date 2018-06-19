# coding: utf-8
from .base import Base
from sqlalchemy import Column, DECIMAL, Date, DateTime, ForeignKey, INTEGER, Index, SMALLINT, String, TIMESTAMP, text
from sqlalchemy.orm import relationship

class Gps(Base):
    __tablename__ = 'gps'
    __table_args__ = (
        Index('latitude', 'latitude', 'longitude', unique=True),
    )

    id = Column(INTEGER(10), primary_key=True)
    latitude = Column(DECIMAL(11, 8), nullable=False)
    longitude = Column(DECIMAL(10, 8), nullable=False)
    address = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    def __init__(self, latitude, longitude, address):
        self.latitude = latitude
        self.longitude = longitude
        self.address = address


class Locator(Base):
    __tablename__ = 'locator'

    id = Column(INTEGER(10), primary_key=True)
    serial = Column(String(50), nullable=False, unique=True)
    label = Column(String(100), nullable=False)
    remark = Column(String(500))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    address = Column(String(200))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    def __init__(self, serial, label):
        self.serial = serial
        self.label = label


class Resident(Base):
    __tablename__ = 'resident'

    id = Column(INTEGER(10), primary_key=True)
    fullname = Column(String(200), nullable=False)
    dob = Column(Date, nullable=False)
    nric = Column(String(20))
    image_path = Column(String(200))
    thumbnail_path = Column(String(200))
    hide_photo = Column(SMALLINT(2), server_default=text("'0'"))
    status = Column(SMALLINT(4), server_default=text("'1'"))
    remark = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    def __init__(self, fullname, dob):
        self.fullname = fullname
        self.dob = dob


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(10), primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(255))
    endpointID = Column(String(40))
    pinpoint_status = Column(SMALLINT(4), server_default=text("'1'"))
    auth_key = Column(String(32), server_default=text("''"))
    password_hash = Column(String(255), server_default=text("''"))
    access_token = Column(String(32))
    password_reset_token = Column(String(255))
    email_confirm_token = Column(String(255))
    phone_number = Column(String(20))
    role = Column(INTEGER(10), server_default=text("'10'"))
    status = Column(SMALLINT(6), server_default=text("'10'"))
    allowance = Column(INTEGER(10))
    timestamp = Column(INTEGER(10))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    def __init__(self, username, email):
        self.username = username
        self.email = email


class Beacon(Base):
    __tablename__ = 'beacon'
    __table_args__ = (
        Index('uuid', 'uuid', 'major', 'minor', unique=True),
    )

    id = Column(INTEGER(10), primary_key=True)
    uuid = Column(String(40), nullable=False)
    major = Column(INTEGER(10), nullable=False)
    minor = Column(INTEGER(10), nullable=False)
    status = Column(SMALLINT(2), server_default=text("'1'"))
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    resident = relationship(u'Resident')

    def __init__(self, uuid, major, minor):
        self.uuid = uuid
        self.major = major
        self.minor = minor


class Caregiver(Base):
    __tablename__ = 'caregiver'
    __table_args__ = (
        Index('relative_id', 'relative_id', 'resident_id', unique=True),
    )

    id = Column(INTEGER(10), primary_key=True)
    relative_id = Column(INTEGER(10), nullable=False)
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False,
                         index=True)
    relation = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    resident = relationship(u'Resident')

    def __init__(self, relative_id, resident_id, relation):
        self.relative_id = relative_id
        self.resident_id = resident_id
        self.relation = relation


class Missing(Base):
    __tablename__ = 'missing'

    id = Column(INTEGER(10), primary_key=True)
    resident_id = Column(ForeignKey(u'resident.id', onupdate=u'CASCADE'), nullable=False, index=True)
    reported_at = Column(DateTime, nullable=False, server_default=text("'0000-00-00 00:00:00'"))
    remark = Column(String(500))
    closed_at = Column(Date, server_default=text("'0000-00-00'"))
    closure = Column(String(500))
    status = Column(INTEGER(2), server_default=text("'1'"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    resident = relationship(u'Resident')

    def __init__(self, resident_id, reported_at):
        self.resident_id = resident_id
        self.reported_at = reported_at


class Relative(Base):
    __tablename__ = 'relative'

    id = Column(INTEGER(10), primary_key=True)
    fullname = Column(String(200), nullable=False)
    nric = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100), unique=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'SET NULL', onupdate=u'CASCADE'), unique=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    user = relationship(u'User')

    def __init__(self, fullname):
        self.fullname = fullname


class UserToken(Base):
    __tablename__ = 'user_token'

    id = Column(INTEGER(10), primary_key=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    token = Column(String(32), nullable=False, unique=True, server_default=text("''"))
    label = Column(String(10))
    mac_address = Column(String(32))
    expire = Column(TIMESTAMP, server_default=text("'0000-00-00 00:00:00'"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship(u'User')

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token


class Location(Base):
    __tablename__ = 'location'

    id = Column(INTEGER(10), primary_key=True)
    beacon_id = Column(ForeignKey(u'beacon.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, unique=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address = Column(String(200))
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    missing_id = Column(ForeignKey(u'missing.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    locator_id = Column(ForeignKey(u'locator.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    beacon = relationship(u'Beacon')
    locator = relationship(u'Locator')
    missing = relationship(u'Missing')
    resident = relationship(u'Resident')
    user = relationship(u'User')

    def __init__(self, beacon_id, latitude, longitude):
        self.beacon_id = beacon_id
        self.latitude = latitude
        self.longitude = longitude


class LocationHistory(Base):
    __tablename__ = 'location_history'

    id = Column(INTEGER(10), primary_key=True)
    beacon_id = Column(ForeignKey(u'beacon.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address = Column(String(200))
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    missing_id = Column(ForeignKey(u'missing.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    locator_id = Column(ForeignKey(u'locator.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    beacon = relationship(u'Beacon')
    locator = relationship(u'Locator')
    missing = relationship(u'Missing')
    resident = relationship(u'Resident')
    user = relationship(u'User')

    def __init__(self, beacon_id, latitude, longitude):
        self.beacon_id = beacon_id
        self.latitude = latitude
        self.longitude = longitude
