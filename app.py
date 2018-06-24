import json
from datetime import datetime, timedelta
import os

import pymysql
import boto3
from chalice import Chalice, NotFoundError, ChaliceViewError, CognitoUserPoolAuthorizer, ConflictError, Rate, \
    UnauthorizedError, AuthResponse
from chalice import IAMAuthorizer
from chalice import BadRequestError
from sqlalchemy import exc

from chalicelib import constants
from chalicelib.auth import encode_password, verify_password, get_jwt_token, decode_jwt_token, gen_jwt_token, \
    get_authorized_user
from chalicelib.db.base import session_factory
from chalicelib.db.models import *
from chalicelib.db.schemas import *
import contextlib

from chalicelib.helper import notify_expired_missing, notify_found_missing, notify_new_missing
from chalicelib.utils import SetEncoder, DatetimeEncoder
from chalicelib.constants import JWT_SECRET

db_host = "iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com"
db_name = "elderly_track"
db_username = "root"
db_password = "Soe7014Ece"

pinpoint_client = boto3.client(
    'pinpoint',
    aws_access_key_id='AKIAIVUZMXV4RPNA6TXQ',
    aws_secret_access_key='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',
    region_name='us-east-1'
)

app = Chalice(app_name="elderly_track")


# JWT Token Authorizer
@app.authorizer()
def authorizer(auth_request):
    token = auth_request.token
    decoded = decode_jwt_token(token, JWT_SECRET)
    # Here login_info = email + "|" + role
    return AuthResponse(routes=['*'], principal_id=decoded['sub'])


# Debug mode
app.debug = True


# authorizer = None  # Set to None to disable authorization


@app.route('/v1/user/register_with_email', methods=['POST'], authorizer=None)
def register():
    json_body = app.current_request.json_body
    email = json_body['email']
    password = json_body['password']
    if not (email or password):
        raise BadRequestError("Email and password must be supplied.")

    result = encode_password(password)
    hashed_password = result['hashed']
    salt_used = result['salt']
    json_body.pop('password', None)
    schema = UserSchema()
    user, errors = schema.load(json_body)
    user.password_hash = hashed_password
    user.password_salt = salt_used

    with contextlib.closing(session_factory()) as session:
        try:
            session.add(user)
            session.commit()
            user_schema = UserSchema(exclude=('password_hash', 'salt', 'access_token'))
            result = user_schema.dump(user)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/user/login_with_email', methods=['POST'], authorizer=None)
def login():
    json_body = app.current_request.json_body
    email = json_body['email']
    password = json_body['password']
    if not (email or password):
        raise BadRequestError("Email and password must be supplied.")

    with contextlib.closing(session_factory()) as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise NotFoundError("User not found")

        # Add to token ==> email + "|" + role
        jwt_token = get_jwt_token(user.email + "," + str(user.role), password, user.password_salt, user.password_hash,
                                  JWT_SECRET)
        return json.dumps({"token": jwt_token}, cls=DatetimeEncoder)


@app.route('/v1/user/login_anonymous', methods=['GET'], authorizer=None)
def login_anonymous():
    data = ',' + str(constants.USER_ROLE_ANONYMOUS)
    print(data)
    jwt_token = gen_jwt_token(data, JWT_SECRET)
    print(jwt_token)
    return json.dumps({"token": jwt_token}, cls=DatetimeEncoder)


@app.route("/v1/missing", methods=['GET'], authorizer=authorizer)
def list_all_missing_cases():
    with contextlib.closing(session_factory()) as session:
        missings = session.query(Missing).all()
        if not missings:
            raise NotFoundError("No missing case")
        else:
            missings_schema = MissingSchema(many=True, exclude=('resident.caregivers', 'resident.beacons'))
            result = missings_schema.dump(missings)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/missing/active", methods=['GET'], authorizer=authorizer)
def list_active_missing_cases():
    with contextlib.closing(session_factory()) as session:
        missings = session.query(Missing).filter(Missing.status == 1).all()
        if not missings:
            raise NotFoundError("No active missing case")
        else:
            missings_schema = MissingSchema(many=True, exclude=('resident.caregivers', 'resident.beacons'))
            result = missings_schema.dump(missings)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/missing/{id}", methods=['GET'], authorizer=authorizer)
def get_missing_by_id(id):
    with contextlib.closing(session_factory()) as session:
        missing = session.query(Missing).get(id)
        if not missing:
            raise NotFoundError("Missing case not found")
        else:
            missing_schema = MissingSchema()
            result = missing_schema.dump(missing)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident", methods=['GET'], authorizer=authorizer)
def list_all_residents():
    with contextlib.closing(session_factory()) as session:
        residents = session.query(Resident).all()
        if not residents:
            raise NotFoundError("No resident found")
        else:
            residents_schema = ResidentSchema(exclude=('beacons', 'missings', 'caregivers'), many=True)
            result = residents_schema.dump(residents)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident/missing", methods=['GET'], authorizer=authorizer)
def list_missing_residents():
    with contextlib.closing(session_factory()) as session:
        residents = session.query(Resident).filter(Resident.status == 1).all()
        if not residents:
            raise NotFoundError("No active resident found")
        else:
            residents_schema = ResidentSchema(exclude=('beacons', 'missings', 'caregivers'), many=True)
            result = residents_schema.dump(residents)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident/{id}", methods=['GET'], authorizer=authorizer)
def get_resident_by_id(id):
    with contextlib.closing(session_factory()) as session:
        resident = session.query(Resident).get(id)
        if not resident:
            raise NotFoundError("Missing case not found")
        else:
            resident_schema = ResidentSchema()
            result = resident_schema.dump(resident)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident/{id}/caregivers", methods=['GET'], authorizer=authorizer)
def list_caregivers_by_resident_id(id):
    with contextlib.closing(session_factory()) as session:
        resident = session.query(Resident).get(id)
        if not resident:
            raise NotFoundError("Missing case not found")
        else:
            resident_schema = ResidentSchema(only=('caregivers',))
            result = resident_schema.dump(resident)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon', methods=['GET'], authorizer=authorizer)
def list_all_beacons():
    with contextlib.closing(session_factory()) as session:
        beacons = session.query(Beacon).all()
        if not beacons:
            raise NotFoundError("No beacon found")
        else:
            beacons_schema = BeaconSchema(many=True, exclude=('resident',))
            result = beacons_schema.dump(beacons)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon/{id}', methods=['GET'], authorizer=authorizer)
def get_beacon_by_id(id):
    with contextlib.closing(session_factory()) as session:
        beacon = session.query(Beacon).get(id)
        if not beacon:
            raise NotFoundError("No beacon found")
        else:
            beacon_schema = BeaconSchema(exclude=('resident.missings',))
            result = beacon_schema.dump(beacon)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon/missing', methods=['GET'], authorizer=authorizer)
def list_beacons_of_active_missing_cases():
    with contextlib.closing(session_factory()) as session:
        beacons = session.query(Beacon) \
            .join(Resident, Resident.id == Beacon.resident_id) \
            .join(Missing, Missing.resident_id == Resident.id) \
            .filter(Missing.status == 1).all()
        if not beacons:
            raise NotFoundError("No beacon of missing residents found")
        else:
            beacons_schema = BeaconSchema(many=True,
                                          exclude=('resident.caregivers', 'resident.beacons', 'resident.missings'))
            result = beacons_schema.dump(beacons)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon/missing_uuid', methods=['GET'], authorizer=authorizer)
def list_uuid_of_active_missing_cases_beacons():
    with contextlib.closing(session_factory()) as session:
        beacons = session.query(Beacon) \
            .join(Resident, Resident.id == Beacon.resident_id) \
            .join(Missing, Missing.resident_id == Resident.id) \
            .filter(Missing.status == 1).all()
        if not beacons:
            raise NotFoundError("No beacon of missing residents found")
        else:
            uuid_list = set()
            for beacon in beacons:
                uuid_list.add(beacon.uuid)
            return json.dumps({"uuid_list": uuid_list}, cls=SetEncoder)


##
# Report of new missing case automatically close existing active missing cases
##
@app.route('/v1/missing', methods=['POST'], authorizer=authorizer)
def create_new_missing_case():
    json_body = app.current_request.json_body

    # Load json data into object
    missing_schema = MissingSchema(
        exclude=('resident.beacons', 'resident.missings', 'resident.missing_active', 'resident.caregivers'))
    missing, errors = missing_schema.load(json_body)
    # Invalid JSON body
    if errors:
        raise ChaliceViewError(errors)

    with contextlib.closing(session_factory()) as session:
        try:
            # Check resident id is valid
            resident = session.query(Resident).get(missing.resident_id)
            if not resident:
                raise NotFoundError('Resident not exists')
            resident.status = 1
            session.merge(resident)
            # Close existing active missing cases
            session.query(Missing).filter(Missing.resident_id == missing.resident_id, Missing.status == 1) \
                .update({'status': 0, 'closed_by': missing.reported_by,
                         'closed_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})
            # Add new missing case
            session.add(missing)
            # Notify other caregivers
            notify_new_missing(db_session=session, missing=missing)
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            return missing_schema.dump(missing)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/missing/close', methods=['PUT'], authorizer=authorizer)
def close_missing_case():
    json_body = app.current_request.json_body

    # Load json data into object
    schema = MissingClosingSchema()
    missing, errors = schema.load(json_body)
    # Invalid JSON body
    if errors:
        raise ChaliceViewError(errors)

    with contextlib.closing(session_factory()) as session:
        try:
            # Check resident id is valid
            resident = session.query(Resident).get(missing.resident_id)
            if not resident:
                raise NotFoundError('Resident not exists')
            resident.status = 0
            session.merge(resident)
            # Close existing active missing cases
            updated = session.query(Missing).filter(Missing.resident_id == missing.resident_id,
                                                    Missing.status == 1).all()
            count = session.query(Missing).filter(Missing.resident_id == missing.resident_id, Missing.status == 1) \
                .update({'status': 0, 'closed_by': missing.closed_by, 'closure': missing.closure,
                         'closed_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = MissingClosingSchema(many=True)
            return {'count': count, 'updated': schema.dump(updated).data}
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/beacon/{id}/enable', methods=['PUT'], authorizer=authorizer)
def enable_beacon_by_id(id):
    with contextlib.closing(session_factory()) as session:
        try:
            beacon = session.query(Beacon).get(id)
            count = session.query(Beacon).filter(Beacon.id == id, Beacon.status == 0).update({'status': 1})
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = BeaconSchema(exclude=('resident',))
            return schema.dump(beacon).data
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/beacon/{id}/disable', methods=['PUT'], authorizer=authorizer)
def disable_beacon_by_id(id):
    with contextlib.closing(session_factory()) as session:
        try:
            beacon = session.query(Beacon).get(id)
            count = session.query(Beacon).filter(Beacon.id == id, Beacon.status == 1).update({'status': 0})
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = BeaconSchema(exclude=('resident',))
            return schema.dump(beacon).data
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/location', methods=['POST'], authorizer=authorizer)
def add_location_by_beacon_id():
    json_body = app.current_request.json_body
    # Load json data into object
    schema = LocationSchema(exclude=('user', 'locator', 'resident', '', ''))
    location, errors = schema.load(json_body)
    # Invalid JSON body
    if errors:
        raise ChaliceViewError(errors)

    with contextlib.closing(session_factory()) as session:
        try:
            beacon = session.query(Beacon).get(location.beacon_id)
            if not beacon:
                raise BadRequestError("Invalid beacon id")
            missing = session.query(Missing) \
                .filter(Missing.resident_id == beacon.resident_id, Missing.status == 1).first()
            if not missing:
                raise BadRequestError("No active missing case")
            location.resident_id = missing.resident_id
            location.missing_id = missing.id
            session.add(location)

            # Send notification on 1st time found
            if not (missing.latitude and missing.longitude):
                notify_found_missing(db_session=session, missing=missing)

            # Update latest location to missing
            missing.latitude = location.latitude
            missing.longitude = location.longitude
            missing.address = location.address
            session.merge(missing)

            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            return schema.dump(location)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/location/beacon', methods=['POST'], authorizer=authorizer)
def add_location_by_beacon_info():
    json_body = app.current_request.json_body
    # Load json data into object
    schema = LocationBeaconSchema()
    location, errors = schema.load(json_body)
    # Invalid JSON body
    if errors:
        raise ChaliceViewError(errors)

    with contextlib.closing(session_factory()) as session:
        try:
            beacon = session.query(Beacon).filter(Beacon.uuid == location['uuid'], Beacon.major == location['major'],
                                                  Beacon.minor == location['minor']).first()
            if not beacon:
                raise BadRequestError("Invalid beacon id")

            missing = session.query(Missing).filter(Missing.resident_id == beacon.resident_id,
                                                    Missing.status == 1).first()
            if not missing:
                raise BadRequestError("No active missing case")

            location['beacon_id'] = beacon.id
            location.pop('uuid', None)
            location.pop('major', None)
            location.pop('minor', None)
            location = Location(**location)
            location.resident_id = missing.resident_id
            location.missing_id = missing.id
            session.add(location)

            # Send notification on 1st time found
            if not (missing.latitude and missing.longitude):
                notify_found_missing(db_session=session, missing=missing)

            # Update latest location to missing
            missing.latitude = location.latitude
            missing.longitude = location.longitude
            missing.address = location.address
            session.merge(missing)

            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = LocationSchema(exclude=('user', 'locator', 'resident'))
            return schema.dump(location)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.schedule(Rate(1, unit=Rate.HOURS))
def expire_missing_case(event):
    ago_24_hours = datetime.utcnow() - timedelta(days=1)
    with contextlib.closing(session_factory()) as session:
        try:
            expired_list = session.query(Missing).filter(Missing.created_at < ago_24_hours, Missing.status == 1).all()
            for expired_missing in expired_list:
                # Update missing case as expired
                expired_missing.status = 0
                expired_missing.closure = 'Expired after 24 hours'
                expired_missing.closed_at = datetime.utcnow()
                session.merge(expired_missing)
                # Notify all caregivers
                notify_expired_missing(db_session=session, missing=expired_missing)
            session.flush()
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/test', methods=['GET'], authorizer=authorizer)
def hello():
    result = get_authorized_user(app.current_request)
    return result


@app.route('/v1/user/notification_status', methods=['POST'], authorizer=authorizer)
def notification_status():
    conn = connect_database()
    json_body = app.current_request.json_body
    user_id = json_body['user_id']
    status = 0
    with conn.cursor() as cur:
        sql = "SELECT pinpoint_status FROM user WHERE id={}".format(user_id)
        cur.execute(sql)
        for row in cur:
            status = row[0]
    return {"status": status}


@app.route('/v1/pinpoint/register_endpoint', methods=['POST'], authorizer=authorizer)
def register_endpoint():
    conn = connect_database()
    json_body = app.current_request.json_body
    pinpoint_endpoint = json_body['endpointID']
    user_id = json_body['user_id']
    message = ""
    with conn.cursor() as cur:
        sql = "SELECT id FROM user WHERE endpointID='{}'".format(pinpoint_endpoint)
        response = cur.execute(sql)
        if response != 0:
            for row in cur:
                with conn.cursor() as cur2:
                    sql = "UPDATE user SET endpointID=NULL, pinpoint_status=0 WHERE id={}".format(row[0])
                    cur2.execute(sql)

    with conn.cursor() as cur:
        sql = "UPDATE user SET endpointID='{}', pinpoint_status=1 WHERE id={}".format(pinpoint_endpoint, user_id)
        cur.execute(sql)
        message = "Successfully registered endpoint for: {}".format(user_id)
    conn.commit()
    conn.close()
    return json.dumps({"Message": message})


@app.route('/v1/pinpoint/disable_endpoint', methods=['POST'], authorizer=authorizer)
def disable_endpoint():
    conn = connect_database()
    json_body = app.current_request.json_body
    user_id = json_body['user_id']
    message = ""
    status = 0
    with conn.cursor() as cur:
        sql = "SELECT pinpoint_status from user where id={}".format(user_id)
        response = cur.execute(sql)
        for row in cur:
            if row[0] == 1:
                status = 0
                message = "Successfully disabled notification for user:{}".format(user_id)
            else:
                status = 1
                message = "Successfully enabled notification for user:{}".format(user_id)
    with conn.cursor() as cur:
        sql = "UPDATE user set pinpoint_status={} WHERE id={}".format(status, user_id)
        cur.execute(sql)
    conn.commit()
    conn.close()
    return {"Message": message, "status": status}


def prepare_message(beacon_id):
    conn = connect_database()
    resident_id = 0
    body = ""
    title = "Update"
    payload = {}
    endpoints = {}

    with conn.cursor() as cur:
        sql = "SELECT resident_id FROM beacon WHERE id={}".format(beacon_id)
        cur.execute(sql)
        for row in cur:
            resident_id = row[0]

    with conn.cursor() as cur:
        sql = "SELECT fullname FROM resident where id={}".format(resident_id)
        cur.execute(sql)
    for row in cur:
        body = "{}'s location has been reported.".format(row[0])

    with conn.cursor() as cur:
        sql = "SELECT DISTINCT user.endpointID FROM user INNER JOIN caregiver on user.id=caregiver.relative_id AND caregiver.resident_id={}".format(
            resident_id)
        cur.execute(sql)

    for row in cur:
        if row[0] != None:
            endpoints[row[0]] = {}

    payload['body'] = body
    payload['title'] = title
    payload['endpoints'] = endpoints

    sent_message(payload)


def sent_message(event):
    endpoints = event['endpoints']
    title = event['title']
    body = event['body']
    print("Endpoints: {}".format(endpoints))
    response = pinpoint_client.send_messages(
        ApplicationId='b080c5f132c24c52930fe52cf32b7038',
        MessageRequest={
            'Endpoints': endpoints,
            'MessageConfiguration': {
                'APNSMessage': {
                    'Action': 'OPEN_APP',
                    'Body': body,
                    'Title': title
                }
            }
        }
    )
    return response


def connect_database():
    try:
        conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    except Exception as e:
        print(e)
        conn = pymysql.connect()
    print("SUCCESS: Connection to RDS mysql instance succeeded")
    return conn
