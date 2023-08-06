import os
import time
import logging
from io import BytesIO
from datetime import datetime

import json

from urllib.request import urlopen
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from croniter import croniter
from flask.wrappers import Response

import jwt
import boto3
import flask
import requests

from .renderer.excel import ExcelRenderer
from .models import Session, AnalysisRun, AnalysisSend
from .constants import DATETIME_FORMAT
logger = logging.getLogger(__name__)

BASE_API_URL = os.getenv('DATA_API_BASE_URL', '')
API_RETRY = int(os.getenv('API_RETRY', 3))
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BASE_API_URL = os.getenv('DATA_API_BASE_URL', '')
ROUTE = os.getenv("PLATFORM_ROUTE")

storage_name = os.getenv('STORAGE_NAME')

global ACCESS_KEY_ID, SECRET_ACCESS_KEY, REGION_NAME, BUCKET_NAME
ACCESS_KEY_ID = ''
SECRET_ACCESS_KEY = ''
REGION_NAME = ''
BUCKET_NAME = ''

if storage_name == 's3_storage':
    ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    REGION_NAME = os.getenv('REGION_NAME')
    BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
elif storage_name == 'ceph_storage':
    ACCESS_KEY_ID = os.getenv('CEPH_ACCESS_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('CEPH_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.getenv('CEPH_BUCKET_NAME')
    REGION_NAME = os.getenv('CEPH_REGION_NAME')
else:
    logger.info("No storages are found")


def get_token():
    headers = {"Content-Type" : "application/x-www-form-urlencoded" , "Accept" : "application/json"};
    post_data = {"grant_type": "client_credentials", "client_id" : API_KEY, "client_secret" : API_SECRET};
    token_url = BASE_API_URL + "/auth/oauth/token";
    response = requests.post(token_url,data=post_data,headers=headers,verify=False);
    json = response.json();
    auth = str(json["access_token"])
    return auth


def get_jwt_token():
    try:
        jwt_token = flask.request.cookies.get('OPSRAMP_JWT_TOKEN', '')
    except:  # outside Flask
        jwt_token = os.getenv('OPSRAMP_JWT_TOKEN', '')

    return jwt_token


def get_headers():
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {get_token()}'
    }

    return headers


def get_msp_id():
    msp_id = None
    jwt_token = get_jwt_token()
    if jwt_token:
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        msp_id = decoded['orgId']

    return msp_id


def get_user_id():
    user_id = None
    jwt_token = get_jwt_token()
    if jwt_token:
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        user_id = decoded['userId']

    return user_id


def call_requests(method, url, params=None, data=None, json=None, verify=True):
    headers = get_headers()
    retry = 1
    while retry <= API_RETRY:
        try:
            resp = requests.request(method, url, params=params, data=data, json=json, headers=headers, verify=verify)
            if not resp.ok:
                time.sleep(retry * 2)
                retry+=1
                continue
        except requests.exceptions.ConnectionError:
            time.sleep(retry * 2)
            retry+=1
            continue

        return resp


def call_get_requests(url, params=None, verify=True):
    return call_requests('GET', url, params, verify=verify)


def call_post_requests(url, params=None, data=None, verify=True):
    return call_requests('POST', url, params, data, verify=verify)

def is_authenticated():
    REQUIRE_AUTH_REDIRECT = os.getenv('REQUIRE_AUTH_REDIRECT') == 'true'
    if not REQUIRE_AUTH_REDIRECT:
        return True

    url = f'{BASE_API_URL}/api/v2/users/me'
    res = call_get_requests(url)

    return res.status_code == 200


def login_required(view):
    '''Decorator that check authentication'''
  
    def wrap(*args, **kwargs):
        if not is_authenticated():
            return Response('Not authorized', status=401)
        result = view(*args, **kwargs)
        return result
    return wrap


def get_epoc_from_datetime_string(str_datetime):
    timestamp = datetime.strptime(str_datetime, DATETIME_FORMAT).timestamp()
    return timestamp

def get_run_result(run_id, field=None, default_value=None):
    with Session() as session:
        run = session.query(AnalysisRun).filter_by(id=run_id).first()

    result = run.get_result() if run else {}
    if field:
        result = result.get(field, default_value)

    return result

def get_result_by_run(run_id, field=None, default_value=None):
    try:
        s3 = get_s3_client()
        run_id= f'analytics-apps/{ROUTE}/json/{run_id}'
        res_object = s3.get_object(Bucket=BUCKET_NAME,Key=run_id)
        serializedObject = res_object['Body'].read()
        result = json.loads(serializedObject)
        if field:
            result = result.get(field, default_value)
        return result
    except Exception:
        logger.error('An error occurred (NoSuchKey) when calling the GetObject operation: The specified key does not exist')
        pass


def get_run_params(run_id, field=None, default_value=None):
    with Session() as session:
        run = session.query(AnalysisRun).filter_by(id=run_id).first()

    if run:
        return run.params


def get_ses_client():
    return boto3.client('ses',
                        region_name=REGION_NAME,
                        aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY)


def get_s3_client():
    return boto3.client('s3',
                        region_name=REGION_NAME,
                        aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY)
    

def send_email(subject, from_email, to_emails, body, attachment=None):
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_emails

    # message body
    part = MIMEText(body, 'html')
    message.attach(part)

    if attachment:
        attachment_body = urlopen(attachment).read()
        part = MIMEApplication(attachment_body)
        part.add_header('Content-Disposition', 'attachment', filename=attachment)
        message.attach(part)

    resp = get_ses_client().send_raw_email(
        Source=message['From'],
        Destinations=to_emails.split(','),
        RawMessage={
            'Data': message.as_string()
        }
    )

    return resp


def upload_to_s3(content, location):
    '''
    :param: content: bytes
    :param: location: str
    '''
    s3 = boto3.resource('s3',
                        region_name=REGION_NAME,
                        aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY)
    object_url = f'https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{location}'

    try:
        s3.Bucket(BUCKET_NAME).put_object(Body=content,
                                             Key=location)
        return object_url
    except Exception:
        pass
    

def generate_pdf(analysis_run):
    logger.info('Entered into pdf generation process')
    url = os.getenv("PDF_SERVICE")
    # analysis_run = json.dumps(analysis_run)
    data = {
        'domain': BASE_API_URL,
        'report': ROUTE,
        'run': analysis_run,
        'route': '/full-view',
        'token': get_token(),
        'size': 'A4'
    }

    res = requests.post(url, data=data).json()
    logger.info('Pdf response is: %s', res)
    return res



def generate_excel(analysis_run, file_name=None):
    try:
        excel_renderer = ExcelRenderer(analysis_run)
        workbook = excel_renderer.render()
    except Exception as ex:
        raise ex

    if file_name:
        output = None
        workbook.save(file_name)
    else:
        output = BytesIO()
        workbook.save(output)

    return output


def upload_excel(analysis_run, excel_file):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    s3_path = f'{analysis_run.analysis.app.slug}/excel/{timestamp}.xlsx'

    return upload_to_s3(excel_file, s3_path)


def run_scheduled_send(analysis_send, func_compute):
    analysis_run = analysis_send.analysis.run(func_compute, None, True)

    if analysis_run:
        if analysis_send.format == 'pdf':
            pdf_info = generate_pdf(analysis_run)
            attachment = pdf_info['Location']
        elif analysis_send.format == 'excel':
            excel_file = generate_excel(analysis_run)
            if excel_file:
                attachment = upload_excel(analysis_run, excel_file.getvalue())
            else:
                attachment = None

        with Session.begin() as session:
            update_send = session.query(AnalysisSend).filter_by(id=analysis_send.id).first()
            update_send.attachment = attachment
            update_send.is_ran = True

        to_emails = analysis_send.recepients
        send_email(analysis_send.subject, os.getenv('FROM_EMAIL'), to_emails, analysis_send.message, attachment)


def check_schedule_send(func_compute):
    app_id = os.getenv('OAP_APP_ID')
    now = datetime.now()
    now_hour = datetime(now.year, now.month, now.day, now.hour)

    with Session() as session:
        sends = session.query(AnalysisSend) \
                       .filter_by(is_active=True) \
                       .filter(AnalysisSend.schedule.is_not(None)) \
                       .join(AnalysisSend.analysis) \
                       .filter_by(app_id=app_id).all()

    for send in sends:
        if croniter.is_valid(send.schedule) and croniter.match(send.schedule, now_hour):
            os.environ['OPSRAMP_JWT_TOKEN'] = send.jwt_token
            run_scheduled_send(send, func_compute)
            print(send.id, '='*10)
