import json
import datetime
import os

import pymysql
import boto3
from chalice import Chalice, NotFoundError, ChaliceViewError, CognitoUserPoolAuthorizer, ConflictError
from chalice import IAMAuthorizer
from chalice import BadRequestError
from sqlalchemy import exc

from chalicelib.db.base import session_factory
from chalicelib.db.models import *
from chalicelib.db.schemas import *
import contextlib

## Used in clients
# lam = boto3.client('lambda',
#                    aws_access_key_id='AKIAIVUZMXV4RPNA6TXQ',
#                    aws_secret_access_key='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',
#                    region_name='ap-southeast-1'
#                    )
from chalicelib.utils import SetEncoder

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

# Debug mode
app.debug = True
authorizer = None  # Set to None to disable authorization


@app.route('/v1/test', methods=['GET'], authorizer=authorizer)
def hello():
    return {'hello': 'world'}


@app.route('/v1/user/login_with_email', methods=['POST'], authorizer=authorizer)
def login():
    json_body = app.current_request.json_body
    email = json_body['email']
    if not email:
        raise BadRequestError("Email must be supplied.")

    with contextlib.closing(session_factory()) as session:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise NotFoundError("Email not found")
        else:
            user_schema = UserSchema(exclude=('password_hash', 'access_token'))
            result = user_schema.dump(user)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/user/login_anonymous', methods=['GET'], authorizer=authorizer)
def anonymousLogin():
    conn = connect_database()

    with conn.cursor() as cur:
        sql = "SELECT MAX(id) FROM user"
        cur.execute(sql)
        for row in cur:
            user_id = row[0] + 1
        sql = "INSERT INTO user (id,username,role,status) VALUES ({},'anonymous',5,10)".format(user_id)
        cur.execute(sql)
    conn.commit()
    conn.close()
    return json.dumps({"user_id": user_id, "username": "anonymous", "role": 5, "status": 10})


@app.route("/v1/missing", methods=['GET'], authorizer=authorizer)
def missing_all():
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
def missing_active():
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
def missing_one(id):
    with contextlib.closing(session_factory()) as session:
        missing = session.query(Missing).filter(Missing.id == id).first()
        if not missing:
            raise NotFoundError("Missing case not found")
        else:
            missing_schema = MissingSchema()
            result = missing_schema.dump(missing)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident", methods=['GET'], authorizer=authorizer)
def resident_all():
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


@app.route("/v1/resident/active", methods=['GET'], authorizer=authorizer)
def resident_active():
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
def resident_one(id):
    with contextlib.closing(session_factory()) as session:
        resident = session.query(Resident).filter(Resident.id == id).first()
        if not resident:
            raise NotFoundError("Missing case not found")
        else:
            resident_schema = ResidentSchema()
            result = resident_schema.dump(resident)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident/{id}/caregivers", methods=['GET'], authorizer=authorizer)
def resident_caregivers(id):
    with contextlib.closing(session_factory()) as session:
        resident = session.query(Resident).filter(Resident.id == id).first()
        if not resident:
            raise NotFoundError("Missing case not found")
        else:
            resident_schema = ResidentSchema(only=('caregivers',))
            result = resident_schema.dump(resident)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon', methods=['GET'], authorizer=authorizer)
def beacon_list():
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
def beacon_one(id):
    with contextlib.closing(session_factory()) as session:
        beacon = session.query(Beacon).filter(Beacon.id == id).first()
        if not beacon:
            raise NotFoundError("No beacon found")
        else:
            beacon_schema = BeaconSchema(exclude=('resident.missings',))
            result = beacon_schema.dump(beacon)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon/missing', methods=['GET'], authorizer=authorizer)
def beacon_missing():
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
def beacon_missing_uuid():
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
def create_missing():
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
            resident = session.query(Resident).filter(Resident.id == missing.resident_id).first()
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
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            return missing_schema.dump(missing)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/missing/close', methods=['PUT'], authorizer=authorizer)
def close_missing():
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
            resident = session.query(Resident).filter(Resident.id == missing.resident_id).first()
            if not resident:
                raise NotFoundError('Resident not exists')
            resident.status = 0
            session.merge(resident)
            # Close existing active missing cases
            missing = session.query(Missing).filter(Missing.resident_id == missing.resident_id, Missing.status == 1) \
                .update({'status': 0, 'closed_by': missing.reported_by,
                         'closed_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')})
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            return schema.dump(missing)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))

    # json_body = app.current_request.json_body
    # message = ""
    # beacon_id = json_body['beacon_id']
    # user_id = json_body['user_id']
    # longitude = round(float(json_body['longitude']), 8)
    # latitude = round(float(json_body['latitude']), 8)
    # conn = connect_database()
    # with conn.cursor() as cur:
    #     sql = "SELECT * FROM location WHERE beacon_id={}".format(beacon_id)
    #     sql_response = cur.execute(sql)
    #     if sql_response == 0:
    #         with conn.cursor() as cur:
    #             sql = "INSERT INTO location (beacon_id,user_id,longitude,latitude) VALUES ({},{},{},{})".format(
    #                 beacon_id, user_id, longitude, latitude)
    #             cur.execute(sql)
    #         message = "Successfully insert"
    #     else:
    #         with conn.cursor() as cur:
    #             sql = "UPDATE location SET longitude={},latitude={},user_id={} WHERE beacon_id={}".format(longitude,
    #                                                                                                       latitude,
    #                                                                                                       user_id,
    #                                                                                                       beacon_id)
    #             cur.execute(sql)
    #         message = "Successfully updated"
    # with conn.cursor() as cur:
    #     sql = "INSERT INTO location_history (beacon_id,user_id,longitude,latitude) VALUES ({},{},{},{})".format(
    #         beacon_id, user_id, longitude, latitude)
    #     cur.execute(sql)
    # conn.commit()
    # conn.close()
    # prepare_message(beacon_id)
    # return {"Message": message}


@app.route('/v1/beacon/{id}/enable', methods=['PUT'], authorizer=authorizer)
def disable_beacon():
    with contextlib.closing(session_factory()) as session:
        try:
            beacon = session.query(Beacon).filter(Beacon.id == id, Beacon.status == 0) \
                .update({'status': 1})
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = BeaconSchema(exclude=('resident',))
            return schema.dump(beacon)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/beacon/{id}/disable', methods=['PUT'], authorizer=authorizer)
def disable_beacon():
    with contextlib.closing(session_factory()) as session:
        try:
            beacon = session.query(Beacon).filter(Beacon.id == id, Beacon.status == 1) \
                .update({'status': 0})
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = BeaconSchema(exclude=('resident',))
            return schema.dump(beacon)
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))

    # json_body = app.current_request.json_body
    # beacon_id = json_body['beacon_id']
    # conn = connect_database()
    # status = 0
    # message = ""
    # with conn.cursor() as cur:
    #     sql = "SELECT status from beacon where id={}".format(beacon_id)
    #     cur.execute(sql)
    #     for row in cur:
    #         if row[0] == 2:
    #             status = 1
    #             message = "Successfully enabled beacon:{}".format(beacon_id)
    #         elif row[0] == 1:
    #             status = 2
    #             message = "Successfully disabled beacon:{}".format(beacon_id)
    #         else:
    #             status = 0
    #     sql = "UPDATE beacon SET status={} WHERE id={}".format(status, beacon_id)
    #     cur.execute(sql)
    # conn.commit()
    # conn.close()
    # return {"Message": message}


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
