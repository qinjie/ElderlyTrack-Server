### Reference
# marshmallow: simplified object serialization  https://marshmallow.readthedocs.io/en/latest/
# https://marshmallow.readthedocs.io/en/latest/examples.html#quotes-api-flask-sqlalchemy
###

from marshmallow import Schema, fields, ValidationError, pre_load


# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class GpsSchema(Schema):
    id = fields.Int(dump_only=True)
    latitude = fields.Decimal(required=True)
    longitude = fields.Decimal(required=True)
    address = fields.Str(required=True, validate=must_not_be_blank)
    created_at = fields.DateTime(dump_only=True)


gps_schema = GpsSchema()


class LocatorSchema(Schema):
    id = fields.Int(dump_only=True)
    serial = fields.Str(required=True, validate=must_not_be_blank)
    label = fields.Str(required=True, validate=must_not_be_blank)
    remark = fields.Str()
    latitude = fields.Decimal()
    longitude = fields.Decimal()
    address = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


locator_schema = LocatorSchema()
locators_schema = LocatorSchema(many=True)


class ResidentSchema(Schema):
    id = fields.Int(dump_only=True)
    fullname = fields.Str(required=True, validate=must_not_be_blank)
    dob = fields.Date(required=True)
    nric = fields.Str()
    image_path = fields.Str()
    thumbnail_path = fields.Str()
    hide_photo = fields.Int(missing=0)
    status = fields.Int(missing=1)
    remark = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


resident_schema = ResidentSchema()
residents_schema = ResidentSchema(many=True, only=('id', 'content'))


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Str()
    endpointID = fields.Str()
    pinpoint_status = fields.Int(missing=1)
    auth_key = fields.Str(missing='')
    password_hash = fields.Str(missing='')
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


user_schema = UserSchema()
user_public_schema = UserSchema(only=('id', 'username', 'email', 'phone_number'))


class BeaconSchema(Schema):
    id = fields.Int(dump_only=True)
    uuid = fields.Str(required=True, validate=must_not_be_blank)
    major = fields.Int(required=True)
    minor = fields.Int(required=True)
    status = fields.Int(missing=1)
    resident_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    resident = fields.Nested(ResidentSchema, dump_only=True)


beacon_schema = BeaconSchema()
beacons_schema = BeaconSchema(many=True)


class RelativeSchema(Schema):
    id = fields.Int(dump_only=True)
    fullname = fields.Str(required=True, validate=must_not_be_blank)
    nric = fields.Str()
    phone = fields.Str()
    email = fields.Str()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)


relative_schema = RelativeSchema()
relatives_schema = RelativeSchema(many=True)


class CaregiverSchema(Schema):
    id = fields.Int(dump_only=True)
    relative_id = fields.Int(required=True)
    resident_id = fields.Int(required=True)
    relation = fields.Str(required=True, validate=must_not_be_blank)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    relative = fields.Nested(RelativeSchema, dump_only=True)
    resident = fields.Nested(ResidentSchema, dump_only=True)


caregiver_schema = CaregiverSchema()
caregivers_schema = CaregiverSchema(many=True)


class MissingSchema(Schema):
    id = fields.Int(dump_only=True)
    resident_id = fields.Int(required=True)
    reported_at = fields.DateTime(missing="'0000-00-00 00:00:00'", required=True)
    remark = fields.Str()
    closed_at = fields.Date(missing="'0000-00-00'")
    closure = fields.Str()
    status = fields.Int(missing=1)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    resident = fields.Nested(ResidentSchema, dump_only=True)


missing_schema = MissingSchema()
missings_schema = MissingSchema(many=True)


class UserTokenSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    token = fields.Str(required=True, validate=must_not_be_blank)
    label = fields.Str()
    mac_address = fields.Str()
    expire = fields.DateTime(missing="'0000-00-00 00:00:00'")
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)


userToken_schema = UserTokenSchema()
userTokens_schema = UserTokenSchema(many=True)


class LocationSchema(Schema):
    id = fields.Int(dump_only=True)
    beacon_id = fields.Int(required=True)
    latitude = fields.Decimal(required=True)
    longitude = fields.Decimal(required=True)
    address = fields.Str()
    resident_id = fields.Int()
    missing_id = fields.Int()
    locator_id = fields.Int()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)

    beacon = fields.Nested(BeaconSchema, dump_only=True)
    locator = fields.Nested(LocatorSchema, dump_only=True)
    missing = fields.Nested(MissingSchema, dump_only=True)
    resident = fields.Nested(ResidentSchema, dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)


class LocationHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    beacon_id = fields.Int(required=True)
    latitude = fields.Decimal(required=True)
    longitude = fields.Decimal(required=True)
    address = fields.Str()
    resident_id = fields.Int()
    missing_id = fields.Int()
    locator_id = fields.Int()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)

    beacon = fields.Nested(BeaconSchema, dump_only=True)
    locator = fields.Nested(LocatorSchema, dump_only=True)
    missing = fields.Nested(MissingSchema, dump_only=True)
    resident = fields.Nested(ResidentSchema, dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)


locationHistory_schema = LocationHistorySchema()
locationHistories_schema = LocationHistorySchema(many=True)
