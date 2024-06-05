import os
from dotenv import load_dotenv

load_dotenv()

DOMAIN = os.getenv('DOMAIN')
ADMIN_USER = os.getenv('ADMIN_USER')
ADMIN_PASSWD = os.getenv('ADMIN_PASSWD')
SEARCH_BASE = os.getenv('SEARCH_BASE')
EMAIL_FROM = 'joe_doe@domain.local'
SMTP_SERVER = 'smtp.domain.local'
SMTP_PORT = 25