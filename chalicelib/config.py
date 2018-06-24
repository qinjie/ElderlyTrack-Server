import os

SES_REGION = os.environ.get('SES_REGION', 'us-east-1')
SNS_REGION = os.environ.get('SNS_REGION', 'ap-southeast-1')
EMAIL_ADMIN = os.environ.get('EMAIL_ADMIN', 'admin@elderlytrack.com')