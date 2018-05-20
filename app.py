import json
import datetime
import pymysql
import boto3
from chalice import Chalice
from chalice import IAMAuthorizer
from chalice import BadRequestError

db_host = "iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com"
db_name = "elderly_track"
db_username = "root"
db_password = "Soe7014Ece"

app = Chalice(app_name="elderly_track")
authorizer = IAMAuthorizer()

lam = boto3.client('lambda',
                   aws_access_key_id='AKIAIVUZMXV4RPNA6TXQ',
                   aws_secret_access_key='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',
                   region_name='ap-southeast-1'
                   )
pinpoint_client = boto3.client(
    'pinpoint',
    aws_access_key_id='AKIAIVUZMXV4RPNA6TXQ',
    aws_secret_access_key='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',
    region_name='us-east-1'
)


@app.route('/v1/user/login_with_email', methods=['POST'], authorizer=authorizer)
def login():
    conn = connect_database()
    json_body = app.current_request.json_body
    email = json_body['email']
    message = ""

    with conn.cursor() as cur:
        sql = "SELECT id, username, email, role, status FROM user WHERE email='{}'".format(email)
        response = cur.execute(sql)
        if response == 0:
            raise BadRequestError("email does not exists.")
        else:
            for row in cur:
                result = {"user_id": row[0], "username": row[1], "email": row[2], "role": row[3], "status": row[4]}
                return json.dumps(result)
    conn.close()


@app.route('/v1/beacon/load_distinctUUID', methods=['GET'], authorizer=authorizer)
def load_distinctUUID():
    conn = connect_database()
    beacons = []
    with conn.cursor() as cur:
        sql = "SELECT DISTINCT uuid from beacon"
        response = cur.execute(sql)
        for row in cur:
            beacons.append({"uuid": row[0]})

    conn.commit()
    conn.close()
    return json.dumps({"beacons": beacons})


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


@app.route('/v1/resident/relatives', methods=['POST'], authorizer=authorizer)
def get_relatives():
    conn = connect_database()
    json_body = app.current_request.json_body
    user_id = json_body['user_id']
    message = ""
    results = []

    with conn.cursor() as cur:
        sql = "SELECT caregiver.resident_id, resident.fullname, resident.dob, resident.nric, resident.status, resident.created_at, resident.remark, resident.hide_photo, resident.image_path, resident.thumbnail_path FROM caregiver INNER JOIN resident ON caregiver.resident_id=resident.id WHERE caregiver.relative_id={} ORDER BY caregiver.relative_id ASC".format(
            user_id)
        cur.execute(sql)
        for row in cur:
            beacons = []
            locations = []
            with conn.cursor() as cur2:
                # Get beacon list
                sql = "SELECT id, resident_id, uuid, major, minor, status, created_at FROM beacon WHERE resident_id={}".format(
                    row[0])
                cur2.execute(sql)
                for row2 in cur2:
                    beacons.append(
                        {"id": row2[0], "resident_id": row2[1], "uuid": row2[2], "major": row2[3], "minor": row2[4],
                         "status": row2[5], "created_at": str(row2[6])})
                with conn.cursor() as cur3:
                    sql = "SELECT id,beacon_id,locator_id,user_id,longitude,latitude,address,created_at FROM location_history WHERE created_at>=ADDDATE(CURRENT_TIMESTAMP,INTERVAL -30 DAY) AND beacon_id={} ORDER BY created_at DESC LIMIT 5".format(
                        row2[0])
                    cur3.execute(sql)
                    for row3 in cur3:
                        locations.append(
                            {"id": row3[0], "beacon_id": row3[1], "locator_id": row3[2], "user_id": row3[3],
                             "longitude": str(row3[4]), "latitude": str(row3[5]), "address": row3[6],
                             "created_at": str(row3[7])})

            results.append({"id": row[0], "fullname": row[1], "dob": str(row[2]), "nric": row[3], "status": row[4],
                            "created_at": str(row[5]), "remark": row[6], "hide_photo": row[7], "image_path": row[8],
                            "thumbnail_path": row[9], "beacons": beacons, "locations": locations})
    return json.dumps(results)
    conn.close()


@app.route("/v1/resident/missing", methods=['GET'], authorizer=authorizer)
def index():
    conn = connect_database()
    result = []
    with conn.cursor() as cur:
        response = cur.execute(
            "SELECT missing.resident_id, resident.fullname, resident.dob, resident.nric, resident.status, resident.created_at, missing.created_at, missing.remark, resident.hide_photo, resident.image_path, resident.thumbnail_path, MAX(missing.created_at) FROM missing INNER JOIN resident ON missing.resident_id=resident.id GROUP BY missing.resident_id")
        if response == 0:
            return {"Success": 0, "Message": "No missing resident"}
    for row in cur:
        beacons = []
        relatives = []
        locations = []
        beacon_id = []
        # Get the beacon list
        with conn.cursor() as cur2:
            cur2.execute(
                "SELECT id,resident_id,uuid,major,minor,status,created_at FROM beacon WHERE resident_id={}".format(
                    row[0]))
        for row2 in cur2:
            beacons.append({"id": row2[0], "resident_id": row2[1], "uuid": row2[2], "major": row2[3], "minor": row2[4],
                            "status": row2[5], "created_at": str(row2[6])})
            beacon_id.append(row2[0])
        # Get relatives list
        with conn.cursor() as cur2:
            cur2.execute(
                "SELECT caregiver.relative_id, user.username, user.email, user.access_token, user.email_confirm_token, user.role, user.phone_number, user.status, user.allowance, user.timestamp FROM caregiver INNER JOIN user ON caregiver.relative_id=user.id WHERE caregiver.resident_id={} ORDER BY caregiver.relative_id ASC".format(
                    row[0]))
            for row2 in cur2:
                relatives.append({"id": row2[0], "username": row2[1], "email": row2[2], "access_token": row2[3],
                                  "email_confirm_token": row2[4], "role": row2[5], "phone_number": row2[6],
                                  "status": row2[7], "allowance": row2[8], "timestamp": str(row2[9])})
                # Get locations list
        with conn.cursor() as cur2:
            for beacon in beacon_id:
                response = cur2.execute(
                    "SELECT id,beacon_id,locator_id,user_id,longitude,latitude,address,created_at FROM location_history WHERE created_at >= ADDDATE(CURRENT_TIMESTAMP, INTERVAL -30 DAY) AND beacon_id={} ORDER BY created_at DESC LIMIT 5".format(
                        beacon))
                for row2 in cur2:
                    locations.append({"id": row2[0], "beacon_id": row2[1], "locator_id": row2[2], "user_id": row2[3],
                                      "longitude": str(row2[4]), "latitude": str(row2[5]), "address": row2[6],
                                      "created_at": str(row2[7])})
        result.append({"id": row[0], "fullname": row[1], "dob": str(row[2]), "nric": row[3], "status": row[4],
                       "created_at": str(row[5]), "reported_at": str(row[6]), "remark": row[7], "hide_photo": row[8],
                       "image_path": row[9], "thumbnail_path": row[10], "beacons": beacons, "relatives": relatives,
                       "locations": locations})

    conn.close()
    return json.dumps(result)


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


@app.route('/v1/resident/report_missing', methods=['POST'], authorizer=authorizer)
def report_resident():
    json_body = app.current_request.json_body
    message = ""
    conn = connect_database()
    resident_id = json_body['resident_id']
    reported_by = json_body['user_id']
    remark = json_body['remark']
    status = 0
    with conn.cursor() as cur:
        sql_response = cur.execute(
            "SELECT status FROM missing WHERE resident_id={} AND reported_by={} AND created_at>=CURRENT_DATE".format(
                resident_id, reported_by))
        if sql_response == 0:
            with conn.cursor() as cur:
                sql = "INSERT INTO missing (resident_id,reported_by,remark) VALUES ({},{},'{}')".format(resident_id,
                                                                                                        reported_by,
                                                                                                        remark)
                cur.execute(sql)
            with conn.cursor() as cur:
                sql = "UPDATE resident SET status=1 WHERE id={}".format(resident_id)
                cur.execute(sql)
            message = "Successfully report resident {}".format(resident_id)
        else:
            for row in cur:
                if row[0] == 0:
                    status = 1
                else:
                    status = 0
            with conn.cursor() as cur:
                sql = "UPDATE missing SET status={},remark='{}' WHERE resident_id={} AND reported_by={} AND created_at>=CURRENT_DATE".format(
                    status, remark, resident_id, reported_by)
                cur.execute(sql)
            with conn.cursor() as cur:
                sql = "UPDATE resident SET status={},remark='{}' WHERE id={}".format(status, remark, resident_id)
                cur.execute(sql)
            message = "Successfully update resident {}".format(resident_id)
        conn.commit()
        conn.close()
        print(message)
        return {"Message": message}


@app.route('/v1/resident/report_found', methods=['POST'], authorizer=authorizer)
def report_found_resident():
    json_body = app.current_request.json_body
    message = ""
    beacon_id = json_body['beacon_id']
    user_id = json_body['user_id']
    longitude = round(float(json_body['longitude']), 8)
    latitude = round(float(json_body['latitude']), 8)
    conn = connect_database()
    with conn.cursor() as cur:
        sql = "SELECT * FROM location WHERE beacon_id={}".format(beacon_id)
        sql_response = cur.execute(sql)
        if sql_response == 0:
            with conn.cursor() as cur:
                sql = "INSERT INTO location (beacon_id,user_id,longitude,latitude) VALUES ({},{},{},{})".format(
                    beacon_id, user_id, longitude, latitude)
                cur.execute(sql)
            message = "Successfully insert"
        else:
            with conn.cursor() as cur:
                sql = "UPDATE location SET longitude={},latitude={},user_id={} WHERE beacon_id={}".format(longitude,
                                                                                                          latitude,
                                                                                                          user_id,
                                                                                                          beacon_id)
                cur.execute(sql)
            message = "Successfully updated"
    with conn.cursor() as cur:
        sql = "INSERT INTO location_history (beacon_id,user_id,longitude,latitude) VALUES ({},{},{},{})".format(
            beacon_id, user_id, longitude, latitude)
        cur.execute(sql)
    conn.commit()
    conn.close()
    prepare_message(beacon_id)
    return {"Message": message}


@app.route('/v1/beacon/disable_beacon', methods=['POST'], authorizer=authorizer)
def disable_beacon():
    json_body = app.current_request.json_body
    beacon_id = json_body['beacon_id']
    conn = connect_database()
    status = 0
    message = ""
    with conn.cursor() as cur:
        sql = "SELECT status from beacon where id={}".format(beacon_id)
        cur.execute(sql)
        for row in cur:
            if row[0] == 2:
                status = 1
                message = "Successfully enabled beacon:{}".format(beacon_id)
            elif row[0] == 1:
                status = 2
                message = "Successfully disabled beacon:{}".format(beacon_id)
            else:
                status = 0
        sql = "UPDATE beacon SET status={} WHERE id={}".format(status, beacon_id)
        cur.execute(sql)
    conn.commit()
    conn.close()
    return {"Message": message}


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