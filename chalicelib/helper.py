# Return emails and phones of related cargives
import boto3
import json

from chalicelib import config
from chalicelib.db.models import UserProfile, Caregiver, Resident

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


def send_verification_email_lambda(email):
    print(email)
    lambda_client.invoke(
        FunctionName='elderly_track-dev-send_verification_email',
        InvocationType='Event',
        LogType='Tail',
        Payload=json.dumps({'email': email}, cls=SetEncoder)
    )


# Notify related caregivers by emails and sms after expired a missing case
def notify_expired_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    subject = "Missing case expired"
    message = "Dear caregiver, {} missing case is expired. Please report again if the elderly is not found yet".format(
        resident.fullname)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    content = "Missing case expired: "
    send_sms(phones, content)


# Notify related caregivers by emails and sms after a new missing case created
def notify_new_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    subject = "Missing case created"
    message = "Dear caregiver, {} is reported missing!".format(resident.fullname)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    content = "Missing case created: "
    send_sms(phones, content)


# Notify related caregivers by emails and sms after location of a missing case is reported
def notify_found_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    subject = "Missing case location detected"
    message = "Dear caregiver, {} is reported found.".format(resident.fullname)
    content = {
        'message': message,
        'subject': subject
    }
    # Send email to caregivers
    send_emails(emails, content)
    # Send sms to caregivers
    content = "Missing case location detected"
    send_sms(phones, content)
