# Return emails and phones of related cargives
from chalicelib.db.models import UserProfile, Caregiver, Resident


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
    # TODO
    pass


def send_sms(phones, content):
    # TODO
    pass


# Notify related caregivers by emails and sms after expired a missing case
def notify_expired_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    # TODO #####################
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
    # TODO #####################
    # Send email to caregivers
    title = "Missing case created"
    content = ""
    send_emails(emails, content)
    # Send sms to caregivers
    content = "Missing case created: "
    send_sms(phones, content)


# Notify related caregivers by emails and sms after location of a missing case is reported
def notify_found_missing(db_session, missing):
    emails, phones = get_caregiver_emails_phones(db_session, missing)
    resident = db_session.query(Resident).get(missing.resident_id)
    # TODO #####################
    # Send email to caregivers
    title = "Missing case location detected"
    content = ""
    send_emails(emails, content)
    # Send sms to caregivers
    content = "Missing case location detected"
    send_sms(phones, content)
