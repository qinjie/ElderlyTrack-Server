import contextlib
import json
from datetime import timedelta
from random import randint

import boto3
import pymysql
from chalice import BadRequestError
from chalice import Chalice, NotFoundError, ChaliceViewError, Rate, \
    AuthResponse
from sqlalchemy import exc

from chalicelib import constants, config, auth
from chalicelib.auth import JWT_SECRET
from chalicelib.auth import encode_password, get_jwt_token, decode_jwt_token, gen_jwt_token, \
    encode_password_reset_token, verify_password_reset_token
from chalicelib.db.base import session_factory
from chalicelib.db.schemas import *
from chalicelib.helper import notify_expired_missing, notify_found_missing, notify_new_missing, \
    notify_close_missing, notify_password_reset
from chalicelib.utils import SetEncoder

db_host = "iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com"
db_name = "elderly_track"
db_username = "root"
db_password = "Soe7014Ece"

ses_client = boto3.client('ses', region_name=config.SES_REGION)
sns_client = boto3.client('sns', region_name=config.SNS_REGION)

app = Chalice(app_name="elderly_track")

# Debug mode
# authorizer = None             # Set to None to disable authorization
app.debug = True


# JWT Token Authorizer
@app.authorizer()
def authorizer(auth_request):
    token = auth_request.token
    decoded = decode_jwt_token(token, JWT_SECRET)
    # Here login_info = email + "|" + role
    return AuthResponse(routes=['*'], principal_id=decoded['sub'])


@app.lambda_function()
def send_emails(event, context):
    emails = event['emails']
    content = event['content']
    from_address = config.EMAIL_ADMIN
    subject = content['subject']
    message = content['message']
    ses_client.send_email(
        Source=from_address,
        Destination={
            'ToAddresses': emails
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'utf8'
            },
            'Body': {
                'Text': {
                    'Data': message,
                    'Charset': 'utf8'
                }
            }
        },
        ReplyToAddresses=[from_address]
    )


@app.lambda_function()
def send_sms(event, context):
    phones = event['phones']
    content = event['content']
    subject = content['subject']
    message = content['message']
    sns_client.set_sms_attributes(
        attributes={
            'DefaultSenderID': 'Elderly'
        }
    )
    for phone in phones:
        if not phone.startswith('+65'):
            phone = '+65' + phone
        print(phone)
        try:
            sns_client.publish(
                PhoneNumber=phone,
                Message=message,
                Subject=subject
            )
        except Exception as e:
            print
            e.message


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
        print("{}, {}, {}".format(user.email, user.role, user.id))
        # Add to token ==> email + "|" + role
        jwt_token = get_jwt_token(user.email + "," + str(user.role) + "," + str(user.id), password,
                                  user.password_salt, user.password_hash, JWT_SECRET)
        info = {'token': jwt_token, 'user': user}
        schema = TokenSchema()
        response = schema.dumps(info)
        if response.errors:
            raise ChaliceViewError(response.errors)
        return response.data


@app.route('/v1/user/login_anonymous', methods=['GET'], authorizer=None)
def login_anonymous():
    data = ',' + str(constants.USER_ROLE_ANONYMOUS) + "," + str(0)
    jwt_token = gen_jwt_token(data, JWT_SECRET)
    info = {'token': jwt_token, 'user': None}
    schema = TokenSchema()
    response = schema.dumps(info)
    if response.errors:
        raise ChaliceViewError(response.errors)
    return response.data


@app.route('/v1/user/forgot_password', methods=['POST'], authorizer=None)
def forgot_password():
    json_body = app.current_request.json_body
    email = json_body['email']
    if not email:
        raise BadRequestError("Email must be supplied.")
    # Generate 5 digit code
    token = str(randint(10000, 99999))
    expire = datetime.now() + timedelta(days=1)
    label = 'PASSWORD_RESET'
    # Invalid JSON body
    with contextlib.closing(session_factory()) as session:
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                raise NotFoundError("User not found")
            # Uncomment this if we want to hash the token
            result = encode_password_reset_token(token=token, salt=user.password_salt)
            hashed_token = result['hashed']
            user_token = session.query(UserToken).filter(UserToken.user_id == user.id).first()
            if not user_token:
                schema = UserTokenSchema()
                json_body['user_id'] = user.id
                json_body['token'] = hashed_token
                user_token, errors = schema.load(json_body)
                user_token.expire = expire
                user_token.label = label
                session.add(user_token)
            else:
                # Update the existing user_token
                session.query(UserToken).filter(UserToken.user_id == user.id).update({'token': hashed_token,
                                                                                      'expire': expire, 'label': label})
                session.flush()
            session.commit()
            notify_password_reset(db_session=session, user=user, token=token)
            return json.dumps({"token": token})
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/user/reset_password', methods=['POST'], authorizer=None)
def reset_password():
    json_body = app.current_request.json_body
    email = json_body['email']
    token = str(json_body['token'])
    password = json_body['password']
    if not (email or password or token):
        raise BadRequestError("Email, password and token mush be supplied.")
    with contextlib.closing(session_factory()) as session:
        user = session.query(User).filter(User.email == email).first()
        user_token = session.query(UserToken).filter(UserToken.user_id == user.id).first()
        if not user:
            raise NotFoundError("User not found")
        if datetime.now() > user_token.expire:
            raise BadRequestError("Token is expired.")
        if not user_token:
            raise BadRequestError("Please request for a token first")
        if not verify_password_reset_token(token=token, salt=user.password_salt, hashed_token=user_token.token):
            raise BadRequestError("Token is invalid")
        result = encode_password(password=password, salt=user.password_salt)
        session.query(User).filter(User.email == email).update({'password_hash': result['hashed']})
        session.flush()
        session.commit()
        jwt_token = get_jwt_token(user.email + "," + str(user.role) + "," + str(user.id), password,
                                  user.password_salt, user.password_hash, JWT_SECRET)
        info = {'token': jwt_token, 'user': user}
        schema = TokenSchema()
        response = schema.dumps(info)
        if response.errors:
            raise ChaliceViewError(response.errors)
        return response.data


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
            missings_schema = MissingSchema(many=True, exclude=(
                'resident.caregivers', 'resident.beacons', 'resident.missing_active'))
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


# Return list of residents who are related to current user
@app.route("/v1/resident/relative", methods=['GET'], authorizer=authorizer)
def list_relative_residents():
    current_user = auth.get_authorized_user(app.current_request)
    with contextlib.closing(session_factory()) as session:
        residents = session.query(Resident) \
            .join(Caregiver, Caregiver.resident_id == Resident.id) \
            .filter(Caregiver.user_id == current_user['id']) \
            .all()
        if not residents:
            raise NotFoundError("No resident found")
        else:
            residents_schema = ResidentSchema(exclude=('beacons', 'missings', 'caregivers', 'missing_active.locations'),
                                              many=True)
            result = residents_schema.dump(residents)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route("/v1/resident/missing", methods=['GET'], authorizer=authorizer)
def list_missing_residents():
    with contextlib.closing(session_factory()) as session:
        residents = session.query(Resident) \
            .join(Missing, Missing.resident_id == Resident.id) \
            .filter(Resident.status == 1, Missing.status == 1) \
            .all()
        if not residents:
            raise NotFoundError("No active resident found")
        else:
            residents_schema = ResidentSchema(exclude=('beacons', 'missings', 'caregivers', 'missing_active.locations'),
                                              many=True)
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


@app.route('/v1/beacon/resident/{resident_id}', methods=['GET'], authorizer=authorizer)
def get_beacon_by_resident_id(resident_id):
    with contextlib.closing(session_factory()) as session:
        beacons = session.query(Beacon) \
            .join(Resident, Resident.id == Beacon.resident_id) \
            .filter(Resident.id == resident_id).all()
        if not beacons:
            raise NotFoundError("No beacon found")
        else:
            beacons_schema = BeaconSchema(exclude=('resident',), many=True)
            result = beacons_schema.dump(beacons)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/beacon/missing', methods=['GET'], authorizer=authorizer)
def list_beacons_of_active_missing_cases():
    with contextlib.closing(session_factory()) as session:
        beacons = session.query(Beacon) \
            .join(Resident, Resident.id == Beacon.resident_id) \
            .join(Missing, Missing.resident_id == Resident.id) \
            .filter(Missing.status == 1, Beacon.status == 1).all()
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


##
# Same as /v1/missing except it returns data instead of [data, errors]
##
@app.route('/v1/missing2', methods=['POST'], authorizer=authorizer)
def create_new_missing_case2():
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
            return missing_schema.dump(missing).data
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
            notify_close_missing(db_session=session, missing=missing)
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = MissingClosingSchema(many=True)
            return {'count': count, 'updated': schema.dump(updated).data}
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


##
# Similiar to /v1/missing/close
#  Return Missing array instead of with count
#
@app.route('/v1/missing/close2', methods=['PUT'], authorizer=authorizer)
def close_missing_case2():
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
            notify_close_missing(db_session=session, missing=missing)
            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            schema = MissingClosingSchema(many=True)
            return schema.dump(updated).data
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


@app.route('/v1/location/missing/{missing_id}', methods=['GET'], authorizer=authorizer)
def list_latest_locations_of_missing_case(missing_id):
    with contextlib.closing(session_factory()) as session:
        locations = session.query(Location) \
            .join(Missing, Missing.id == Location.missing_id) \
            .filter(Missing.id == missing_id) \
            .order_by(Location.id.desc()) \
            .limit(20) \
            .all()
        if not locations:
            raise NotFoundError("No location of this missing case found")
        else:
            locations_schema = LocationSchema(many=True,
                                              exclude=('resident', 'missing', 'locator', 'user'))
            result = locations_schema.dump(locations)
            if result.errors:  # errors not empty
                raise ChaliceViewError(result.errors)
            return result.data


@app.route('/v1/location', methods=['POST'], authorizer=authorizer)
def add_location_by_beacon_id():
    json_body = app.current_request.json_body
    # Load json data into object
    schema = LocationSchema(exclude=('user', 'locator', 'resident', 'beacon', 'missing.locations'))
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
                notify_found_missing(db_session=session, missing=missing, location=location)

            # Update latest location to missing
            missing.latitude = location.latitude
            missing.longitude = location.longitude
            missing.address = location.address
            session.merge(missing)

            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            return schema.dump(location).data
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/location/one', methods=['POST'], authorizer=authorizer)
def add_location_detail_one():
    # TODO
    json_body = app.current_request.json_body
    # Load json data into object
    schema = LocationSchema(exclude=('user', 'locator', 'resident', '', ''))
    location, errors = schema.load(json_body)
    # Invalid JSON body
    if errors:
        raise ChaliceViewError(errors)
    with contextlib.closing(session_factory()) as session:
        try:
            missing = session.query(Missing) \
                .filter(Missing.resident_id == location.resident_id, Missing.status == 1).first()
            if not missing:
                raise BadRequestError("No active missing case")
            session.add(location)

            # Send notification on 1st time found
            if not (missing.latitude and missing.longitude):
                notify_found_missing(db_session=session, missing=missing, location=location)

            # Update latest location to missing
            missing.latitude = location.latitude
            missing.longitude = location.longitude
            missing.address = location.address
            session.merge(missing)

            # Call flush() to update id value in missing
            session.flush()
            session.commit()
            return json.dumps({"count": count})
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/location/batch', methods=['POST'], authorizer=authorizer)
def add_location_in_batch():
    # TODO
    json_body = app.current_request.json_body
    # Load json data into object
    schema = LocationSchema(many=True, exclude=('user', 'locator', 'resident', '', ''))
    result, errors = schema.load(json_body)
    # Invalid JSON body
    if errors:
        raise ChaliceViewError(errors)

    with contextlib.closing(session_factory()) as session:
        try:
            count = 0
            for location in data:
                missing = session.query(Missing) \
                    .filter(Missing.resident_id == location.resident_id, Missing.status == 1).first()
                if not missing:
                    raise BadRequestError("No active missing case")
                count = count + 1
                session.add(location)

                # Send notification on 1st time found
                if not (missing.latitude and missing.longitude):
                    notify_found_missing(db_session=session, missing=missing, location=location)

                # Update latest location to missing
                missing.latitude = location.latitude
                missing.longitude = location.longitude
                missing.address = location.address
                session.merge(missing)

                # Call flush() to update id value in missing
                session.flush()
                session.commit()
            return json.dumps({"count": count})
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
                # Update resident status to 0 if missing is closed
                session.query(Resident).get(expired_missing.resident_id).update({'status': 0})
                # Notify all caregivers
                notify_expired_missing(db_session=session, missing=expired_missing)

            session.flush()
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise ChaliceViewError(str(e))


@app.route('/v1/test', methods=['GET'], authorizer=None)
def hello():
    # No need to verify email
    # result = send_verification_email_lambda("qinjie@np.edu.sg")
    return json.dumps({message: "Success"})


def connect_database():
    try:
        conn = pymysql.connect(db_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=5)
    except Exception as e:
        print(e)
        conn = pymysql.connect()
    print("SUCCESS: Connection to RDS mysql instance succeeded")
    return conn
