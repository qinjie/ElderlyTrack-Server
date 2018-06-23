# coding: utf-8
from .base import Base
from sqlalchemy import Integer, Column, DECIMAL, Date, DateTime, ForeignKey, Index, SMALLINT, String, TIMESTAMP, text, \
    Table
from sqlalchemy.orm import relationship

caregiver_table = Table('caregiver', Base.metadata,
                        Column('user_id', Integer, ForeignKey('user.id')),
                        Column('resident_id', Integer, ForeignKey('resident.id'))
                        )


class Gps(Base):
    __tablename__ = 'gps'
    __table_args__ = (
        Index('latitude', 'latitude', 'longitude', unique=True),
    )

    id = Column(Integer, primary_key=True)
    latitude = Column(DECIMAL(11, 8), nullable=False)
    longitude = Column(DECIMAL(10, 8), nullable=False)
    address = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__, self.latitude, self.longitude, self.address)


class Locator(Base):
    __tablename__ = 'locator'

    id = Column(Integer, primary_key=True)
    serial = Column(String(50), nullable=False, unique=True)
    label = Column(String(100), nullable=False)
    remark = Column(String(500))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    address = Column(String(200))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class Resident(Base):
    __tablename__ = 'resident'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(200), nullable=False)
    gender = Column(SMALLINT, server_default=text("'1'"))
    dob = Column(Date, nullable=False)
    nric = Column(String(20))
    image_path = Column(String(200))
    thumbnail_path = Column(String(200))
    hide_photo = Column(SMALLINT, server_default=text("'0'"))
    status = Column(SMALLINT, server_default=text("'1'"))
    remark = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # # many user many resident
    caregivers = relationship("User", secondary=caregiver_table, back_populates="caretakers")
    beacons = relationship(u'Beacon', back_populates="resident")
    missings = relationship(u'Missing', back_populates="resident")
    missing_active = relationship(u'Missing', uselist=False,
                                   primaryjoin="and_(Resident.id==Missing.resident_id, Missing.status==1)",
                                   back_populates="resident")


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(255))
    endpointID = Column(String(40))
    pinpoint_status = Column(SMALLINT, server_default=text("'1'"))
    auth_key = Column(String(32), server_default=text("''"))
    password_hash = Column(String(255), server_default=text("''"))
    access_token = Column(String(32))
    password_reset_token = Column(String(255))
    email_confirm_token = Column(String(255))
    phone_number = Column(String(20))
    role = Column(Integer, server_default=text("'10'"))
    status = Column(SMALLINT, server_default=text("'10'"))
    allowance = Column(Integer)
    timestamp = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # many user many resident
    caretakers = relationship(u'Resident', secondary=caregiver_table, back_populates="caregivers")
    # one user one profile
    user_profile = relationship(u'UserProfile', uselist=False, back_populates="user")
    # one user many token
    user_token = relationship(u'UserToken', back_populates="user")

    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r, %r, %r)" % (
            self.__class__, self.id, self.username, self.email, self.phone_number, self.role, self.status)


class Beacon(Base):
    __tablename__ = 'beacon'
    __table_args__ = (
        Index('uuid', 'uuid', 'major', 'minor', unique=True),
    )

    id = Column(Integer, primary_key=True)
    uuid = Column(String(40), nullable=False)
    major = Column(Integer, nullable=False)
    minor = Column(Integer, nullable=False)
    status = Column(SMALLINT, server_default=text("'1'"))
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    resident = relationship(u'Resident', back_populates="beacons")


class Caregiver(Base):
    __tablename__ = 'caregiver'
    __table_args__ = (
        Index('relative_id', 'user_id', 'resident_id', unique=True),
        {'extend_existing': True}
    )
    extend_existing = True

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False,
                     index=True)
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False,
                         index=True)
    relation = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # resident = relationship(u'Resident')
    # user = relationship(u'User')


class Missing(Base):
    __tablename__ = 'missing'

    id = Column(Integer, primary_key=True)
    resident_id = Column(ForeignKey(u'resident.id', onupdate=u'CASCADE'), nullable=False, index=True)
    reported_by = Column(ForeignKey(u'user.id', onupdate=u'CASCADE'), nullable=True, index=True)
    reported_at = Column(DateTime, nullable=False, server_default=text("'1000-01-01 00:00:00'"))
    remark = Column(String(500))
    closed_by = Column(ForeignKey(u'user.id', onupdate=u'CASCADE'), nullable=True, index=True)
    closed_at = Column(Date, server_default=text("'1000-01-01'"))
    closure = Column(String(500))
    status = Column(SMALLINT, server_default=text("'1'"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    resident = relationship(u'Resident', back_populates="missings")

    # latest_location = relationship(u'Location', back_populates="missing")
    # location_history = relationship(u'LocationHistory', back_populates="missing")


class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    fullname = Column(String(200), nullable=False)
    nric = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100), unique=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'SET NULL', onupdate=u'CASCADE'), unique=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    user = relationship(u'User', uselist=False, back_populates="user_profile")


class UserToken(Base):
    __tablename__ = 'user_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    token = Column(String(32), nullable=False, unique=True, server_default=text("''"))
    label = Column(String(10))
    mac_address = Column(String(32))
    expire = Column(TIMESTAMP, server_default=text("'1000-01-01 00:00:00'"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship(u'User', uselist=False, back_populates="user_token")


class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    beacon_id = Column(ForeignKey(u'beacon.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, unique=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address = Column(String(200))
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    missing_id = Column(ForeignKey(u'missing.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    locator_id = Column(ForeignKey(u'locator.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # beacon = relationship(u'Beacon')
    # locator = relationship(u'Locator')
    # missing = relationship(u'Missing', back_populates='latest_location')
    # resident = relationship(u'Resident')
    # user = relationship(u'User')


class LocationHistory(Base):
    __tablename__ = 'location_history'

    id = Column(Integer, primary_key=True)
    beacon_id = Column(ForeignKey(u'beacon.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address = Column(String(200))
    resident_id = Column(ForeignKey(u'resident.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    missing_id = Column(ForeignKey(u'missing.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    locator_id = Column(ForeignKey(u'locator.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    user_id = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # beacon = relationship(u'Beacon')
    # locator = relationship(u'Locator')
    # missing = relationship(u'Missing', back_populates='location_history')
    # resident = relationship(u'Resident')
    # user = relationship(u'User')
