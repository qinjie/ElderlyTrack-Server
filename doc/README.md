
# Deployment

chalice deploy --stage dev --profile qinjie
chalice deploy --stage proc --profile qinjie



# AWS Resources

1. Mobile Hub
    ElderlyTrack   https://console.aws.amazon.com/mobilehub/home#/f5bfa0c2-86d9-44ca-aab9-0956b4499ca5/build
    - Add Google sign-in Client ID to User sign-in. Mobile hub will automatially create Cognito Federated Identities.
    - Add API Gateway to Cloud Logic

2. Cognito Federated Identities (Auto-created by Mobile Hub)
    elderlytrack_MOBILEHUB_190966844



# Development

Use sqlalchemy as ORM
Use sqlacodegen to generate all the models from the database, but need to take care of the foreign key manually.
    https://pypi.org/project/sqlacodegen/


ssh ubuntu@13.250.218.226 -i ~/Dropbox/_ssh/ec-key-one.pem



## sqlacodegen for SQLAlchemy
Use sqlacodegen (https://pypi.org/project/sqlacodegen/) to generate models for SQLAlchemy ORM

To generate sqlalchemy models on Ubuntu
```
sudo apt install python-minimal
sudo apt install python-mysqldb
sudo apt install python-pip
pip install sqlacodegen
sqlacodegen mysql://root:Soe7014Ece@iot-centre-rds.crqhd2o1amcg.ap-southeast-1.rds.amazonaws.com/elderly_track > models.py
```

## marshmallow
an ORM/ODM/framework-agnostic library for converting complex datatypes, such as objects, to and from native Python datatypes.

## pipreqs
Generate pip requirements.txt file based on imports of any project
```
pip install pipreqs
pipreqs /home/project/location
```



# Reference

https://aws.amazon.com/blogs/compute/build-serverless-applications-in-aws-mobile-hub/
https://cloudly.tech/blog/serverless-authorizers-2/
https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/

http://chalice-workshop.readthedocs.io/en/latest/part1/00-intro-chalice.html
