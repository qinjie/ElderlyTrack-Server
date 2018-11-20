### Reference
# marshmallow: simplified object serialization  https://marshmallow.readthedocs.io/en/latest/
# https://marshmallow.readthedocs.io/en/latest/examples.html#quotes-api-flask-sqlalchemy
###
from datetime import datetime

from marshmallow import Schema, fields, ValidationError, pre_load, post_load

# Custom validator
from chalicelib.db.models import *


def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class TokenSchema(Schema):
    token = fields.Str()
    user = fields.Nested('UserSchema', only=('id', 'role', 'status', 'email', 'username', 'user_profile'))


class GpsSchema(Schema):
    id = fields.Int()
    latitude = fields.Decimal(required=True)
    longitude = fields.Decimal(required=True)
    address = fields.Str(required=True, validate=must_not_be_blank)
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make(self, data):
        return Gps(**data)


# gps_schema = GpsSchema()


class LocatorSchema(Schema):
    id = fields.Int()
    serial = fields.Str(required=True, validate=must_not_be_blank)
    label = fields.Str(required=True, validate=must_not_be_blank)
    remark = fields.Str()
    latitude = fields.Decimal()
    longitude = fields.Decimal()
    address = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_load
    def make(self, data):
        return Locator(**data)


# locator_schema = LocatorSchema()
# locators_schema = LocatorSchema(many=True)


class ResidentSchema(Schema):
    id = fields.Int()
    fullname = fields.Str(required=True, validate=must_not_be_blank)
    gender = fields.Int(missing=1)
    dob = fields.Date(required=True)
    nric = fields.Str()
    image_path = fields.Str()
    thumbnail_path = fields.Str()
    hide_photo = fields.Int(missing=0)
    status = fields.Int(missing=1)
    remark = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    beacons = fields.Nested('BeaconSchema', many=True, dump_only=True, exclude=('resident',))
    missings = fields.Nested('MissingSchema', many=True, dump_only=True, exclude=('resident',))
    missing_active = fields.Nested('MissingSchema', dump_only=True, exclude=('resident',))
    caregivers = fields.Nested('UserSchema', many=True, dump_only=True, only=('id', 'username', 'user_profile',))

    @post_load
    def make(self, data):
        return Resident(**data)


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()
    endpointID = fields.Str()
    pinpoint_status = fields.Int(missing=1)
    auth_key = fields.Str()
    password_hash = fields.Str()
    password_salt = fields.Str()
    access_token = fields.Str()
    password_reset_token = fields.Str()
    email_confirm_token = fields.Str()
    phone_number = fields.Str()
    role = fields.Int(missing=10)
    status = fields.Int(missing=10)
    allowance = fields.Int()
    timestamp = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    user_profile = fields.Nested('UserProfileSchema', dump_only=True, exclude=('user',))
    user_tokens = fields.Nested('UserTokenSchema', many=True, dump_only=True, exclude=('user',))

    @post_load
    def make(self, data):
        return User(**data)


# user_schema = UserSchema(exclude=('password_hash','access_token'))
# user_public_schema = UserSchema(only=('id', 'username', 'email', 'phone_number', 'role', 'status'))
# users_public_schema = UserSchema(many=True, only=('id', 'username', 'email', 'phone_number', 'role', 'status'))


class BeaconSchema(Schema):
    id = fields.Int()
    uuid = fields.Str(required=True, validate=must_not_be_blank)
    major = fields.Int(required=True)
    minor = fields.Int(required=True)
    label = fields.Str()
    status = fields.Int(missing=1)
    resident_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    resident = fields.Nested(ResidentSchema, exclude=('beacons',), dump_only=True)

    @post_load
    def make(self, data):
        return Beacon(**data)


# beacon_schema = BeaconSchema()
# beacons_schema = BeaconSchema(many=True, exclude=('resident',))


class UserProfileSchema(Schema):
    id = fields.Int()
    fullname = fields.Str(required=True, validate=must_not_be_blank)
    nric = fields.Str()
    phone = fields.Str()
    email = fields.Str()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    user = fields.Nested(UserSchema, dump_only=True)

    @post_load
    def make(self, data):
        return UserProfile(**data)


# user_profile_schema = UserProfileSchema()
# user_profiles_schema = UserProfileSchema(exclude=('user',), many=True)


class CaregiverSchema(Schema):
    id = fields.Int()
    relative_id = fields.Int(required=True)
    resident_id = fields.Int(required=True)
    relation = fields.Str(required=True, validate=must_not_be_blank)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    relative = fields.Nested(UserProfileSchema, dump_only=True)
    resident = fields.Nested(ResidentSchema, dump_only=True)

    @post_load
    def make(self, data):
        return Caregiver(**data)


# caregiver_schema = CaregiverSchema()
# caregivers_schema = CaregiverSchema(many=True)


class MissingSchema(Schema):
    id = fields.Int()
    resident_id = fields.Int(required=True)
    reported_by = fields.Int(required=True)
    reported_at = fields.DateTime(missing="'1000-01-01 00:00:00'", required=True)
    remark = fields.Str(required=True)
    latitude = fields.Decimal()
    longitude = fields.Decimal()
    address = fields.Str()
    closed_by = fields.Int()
    closed_at = fields.Date()
    closure = fields.Str()
    status = fields.Int(missing=1)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    resident = fields.Nested(ResidentSchema, exclude=('missings', 'missing_active'), dump_only=True)
    locations = fields.Nested('LocationSchema', many=True, exclude=('missing', 'resident', 'user', 'locator'),
                              dump_only=True)

    @pre_load
    def pre(self, data):
        if not data.get('reported_at', None):
            data['reported_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return data

    @post_load
    def make(self, data):
        return Missing(**data)


# missing_schema = MissingSchema()
# missings_schema = MissingSchema(many=True)


class MissingClosingSchema(Schema):
    id = fields.Int()
    resident_id = fields.Int(required=True)
    reported_by = fields.Int()
    reported_at = fields.DateTime()
    remark = fields.Str()
    closed_by = fields.Int(required=True)
    closed_at = fields.Date()
    closure = fields.Str(required=True)
    status = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def pre(self, data):
        if not data.get('closed_at', None):
            data['closed_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return data

    @post_load
    def make(self, data):
        return Missing(**data)


class UserTokenSchema(Schema):
    id = fields.Int()
    user_id = fields.Int(required=True)
    token = fields.Str(required=True, validate=must_not_be_blank)
    label = fields.Str()
    mac_address = fields.Str()
    expire = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)

    user = fields.Nested(UserSchema, dump_only=True)

    @post_load
    def make(self, data):
        return UserToken(**data)


# userToken_schema = UserTokenSchema()
# userTokens_schema = UserTokenSchema(exclude=('user',), many=True)


class LocationSchema(Schema):
    id = fields.Int()
    beacon_id = fields.Int(required=True)
    latitude = fields.Decimal(required=True)
    longitude = fields.Decimal(required=True)
    address = fields.Str()
    resident_id = fields.Int()
    missing_id = fields.Int()
    locator_id = fields.Int()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)

    beacon = fields.Nested(BeaconSchema, exclude=('resident',), dump_only=True)
    missing = fields.Nested(MissingSchema, exclude=('resident',), dump_only=True)
    resident = fields.Nested(ResidentSchema, exclude=('beacons', 'missings', 'missing_active', 'caregivers'),
                             dump_only=True)
    locator = fields.Nested(LocatorSchema, dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)

    @post_load
    def postload(self, data):
        return Location(**data)


# location_schema = LocationSchema()
# locations_schema = LocationSchema(many=True)

class LocationBeaconSchema(Schema):
    id = fields.Int()
    beacon_id = fields.Int()
    uuid = fields.Str(required=True)
    minor = fields.Int(required=True)
    major = fields.Int(required=True)
    latitude = fields.Decimal(required=True)
    longitude = fields.Decimal(required=True)
    address = fields.Str()
    resident_id = fields.Int()
    missing_id = fields.Int()
    locator_id = fields.Int()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)


class SettingSchema(Schema):
    id = fields.Int()
    label = fields.Int(required=True)
    val = fields.Str(required=True)
    remark = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
