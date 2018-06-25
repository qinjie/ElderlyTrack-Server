# Return emails and phones of related cargives
from chalicelib.db.models import UserProfile, Caregiver, Resident
from chalicelib import config
import boto3


ses_client = boto3.client('ses', region_name=config.SES_REGION)
sns_client = boto3.client('sns', region_name=config.SNS_REGION)


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
  from_address = config.EMAIL_ADMIN
  subject = content['subject']
  message = content['message']
  try:
    ses_client.send_email(
      Source=from_address,
      Destination={
        'ToAddresses': emails,
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
      ReplyToAddresses=[
        from_address
      ]
    )
  except Exception as e:
    print e.message     


def send_sms(phones, content):
  subject = content['subject']
  message = content['message']
  sns_client.set_sms_attributes(
    attributes={
      'DefaultSenderID': 'Elderly'
    }
  )
  for phoneNumber in phoneNumbers:
    try:
      sns_client.publish(
        PhoneNumber=phoneNumber,
        Message=message,
        Subject=subject
      )
    except Exception as e:
      print e.message


# Notify related caregivers by emails and sms after expired a missing case
def notify_expired_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    subject = "Missing case expired"
    message = "Dear caregiver, {} missing case is expired. Please report again if the elderly is not found yet".format(resident.fullname)
    content = {
      'message': message,
      'subject': subject
    }
    # Send email to caregivers
    title = "Missing case expired"
    content = ""
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
    title = "Missing case location detected"
    content = ""
    send_emails(emails, content)
    # Send sms to caregivers
    content = "Missing case location detected"
    send_sms(phones, content)


# Send Verification email to caregiver upon registered
def send_verification_email(email):
	ses_client.send_custom_verification_email(
      EmailAddress=email,
      TemplateName='EmailVerification',
      ConfigurationSetName='EmailVerification'
    )
