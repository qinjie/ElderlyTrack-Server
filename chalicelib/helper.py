# Return emails and phones of related cargives
import json

import boto3

from chalicelib import config
from chalicelib.db.models import UserProfile, Caregiver, Resident, User
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
    subject = "Missing case expired"
    message = "Dear caregiver, {}'s missing case is expired. \nPlease report again if the elderly is not found yet"\
        .format(resident.fullname)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    send_sms(phones, content)


# Notify related caregivers by emails and sms after closing a missing case
def notify_close_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    user = db_session.query(User).get(missing.closed_by)
    subject = "Missing case closed"
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
    subject = "Missing case created"
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
    subject = "Missing case location detected"
    address = "."
    if missing.address:
        address = " at {}.".format(missing.address)
    message = "Dear caregiver, {}'s location is reported{}\n\nhttp://www.google.com/maps/place/{},{}"\
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
    subject = "Password reset"
    message = "Dear {}, you have requested for a password reset. Please use the following " \
              "code to change your password.\n\nIf this is not your request, please ignore this email.\n\n{}"\
        .format(user.username, token)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to user
    send_emails([user_profile.email], content)
