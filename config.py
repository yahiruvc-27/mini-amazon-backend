# config.py
import os

RDS_ENDPOINT = os.getenv("RDS_ENDPOINT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
AWS_REGION = os.getenv("AWS_REGION")
SES_SOURCE = os.getenv("SES_SOURCE", "yahiruvc@gmail.com") 
