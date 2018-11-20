# Return emails and phones of related cargives
import contextlib
import datetime
import json

import boto3
from chalice import ChaliceViewError
from sqlalchemy import and_

from chalicelib import config
from chalicelib.db.base import session_factory
from chalicelib.db.models import UserProfile, Caregiver, Resident, User, Missing
from chalicelib.utils import SetEncoder

ses_client = boto3.client('ses', region_name=config.SES_REGION)
sns_client = boto3.client('sns', region_name=config.SNS_REGION)
lambda_client = boto3.client('lambda', region_name=config.LAMBDA_REGION)


def get_caregiver_emails_phones(db_session, missing):
    # Get all caregiver email and phone
    caregiver_profiles = db_session.query(UserProfile) \
        .join(Caregiver, UserProfile.user_id == Caregiver.user_id) \
        .filter(Caregiver.resident_id == missing.resident_id) \
        .all()
    emails = []
    phones = []
    for profile in caregiver_profiles:
        if profile.email:
            emails.append(profile.email)
        if profile.phone:
            phones.append(profile.phone)
    return emails, phones


def send_emails(emails, content):
    payload = {
        'emails': emails,
        'content': content
    }
    lambda_client.invoke(
        FunctionName='elderly_track-dev-send_emails',
        InvocationType='Event',
        LogType='Tail',
        Payload=json.dumps(payload, cls=SetEncoder)
    )


def send_sms(phones, content):
    payload = {
        'phones': phones,
        'content': content
    }
    lambda_client.invoke(
        FunctionName='elderly_track-dev-send_sms',
        InvocationType='Event',
        LogType='Tail',
        Payload=json.dumps(payload, cls=SetEncoder)
    )


# Notify related caregivers by emails and sms after expired a missing case
def notify_expired_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    subject = "(ElderlyTrack) Missing case expired"
    message = "Dear caregiver, {}'s missing case is expired. \nPlease report again if the elderly is not found yet" \
        .format(resident.fullname)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    send_sms(phones, content)


def expire_missing_case_minutes_older(minutes):
    deadline = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
    hours = minutes / 60.0
    with contextlib.closing(session_factory()) as session:
        query_missing = session.query(Missing)
        query_resident = session.query(Resident)
        try:
            expired_list = query_missing.filter(and_(Missing.created_at < deadline, Missing.status == 1)).all()
            for missing_case in expired_list:
                print(missing_case)
                # Update missing case as expired
                missing_case.status = 0
                missing_case.closure = "Expired after {:.2f} hours".format(hours)
                missing_case.closed_at = datetime.datetime.utcnow()
                session.merge(missing_case)
                # Update resident status to 0 if missing is closed
                resident = query_resident.get(missing_case.resident_id)
                resident.status = 0
                # Notify all caregivers
                notify_expired_missing(db_session=session, missing=missing_case)
                session.flush()

            session.commit()
        except Exception as e:
            session.rollback()
            raise ChaliceViewError(str(e))


# Notify related caregivers by emails and sms after closing a missing case
def notify_close_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    user = db_session.query(User).get(missing.closed_by)
    subject = "(ElderlyTrack) Missing case closed"
    closure = ""
    if missing.closure:
        closure = "Closure: {}".format(missing.closure)
    message = "Dear caregiver, {}'s missing case is closed by {}.\n\n{}".format(resident.fullname,
                                                                                user.username, closure)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    send_sms(phones, content)


# Notify related caregivers by emails and sms after a new missing case created
def notify_new_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    user = db_session.query(User).get(missing.reported_by)
    subject = "(ElderlyTrack) Missing case created"
    remark = ""
    if missing.remark:
        remark = "Remark: {}".format(missing.remark)
    message = "Dear caregiver, {} is reported missing by {}!\n\n{}".format(resident.fullname,
                                                                           user.username, remark)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    send_sms(phones, content)


# Notify related caregivers by emails and sms after location of a missing case is reported
def notify_found_missing(db_session, missing, location):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    subject = "(ElderlyTrack) Missing case location detected"
    address = "."
    if missing.address:
        address = " at {}.".format(missing.address)
    message = "Dear caregiver, {}'s location is reported{}\n\nhttp://www.google.com/maps/place/{},{}" \
        .format(resident.fullname, address, location.latitude, location.longitude)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    send_sms(phones, content)


def notify_password_reset(db_session, user, token):
    user_profile = db_session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    subject = "(ElderlyTrack) Password reset"
    message = "Dear {}, \n\nYou have requested for a password reset. Please use the following " \
              "code to change your password.\n\n" \
              "Reset Code: {}\n\n" \
              "If this is not your request, please ignore this email." \
        .format(user.username, token)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to user
    return send_emails([user_profile.email], content)
