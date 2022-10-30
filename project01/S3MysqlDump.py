#!/usr/bin/python
import boto3
import os
import time
import getpass
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
#Mysql configuration.
user = “user name”
password = “the password”
host = “127.0.0.1”
database = “database name”
#AWS configuration
AWS_ACCESS_KEY_ID = ‘IAM account key’
AWS_SECRET_ACCESS_KEY = ‘IAM secret key’
S3_BUCKET = ‘S3 bucket name’
#Email configuration works with gmail account. 
fromaddr = “from which email id ”
toaddr = [‘to which email you want to send’]
msg = MIMEMultipart()
msg[‘From’] = fromaddr
msg[‘To’] = “, “.join(toaddr)
server = smtplib.SMTP(‘smtp.gmail.com’, 587)
server.starttls()
server.login(fromaddr, “password of from email id ”)
# "os.popen" python module to execute bash commands to take the database dumps. For connecting to s3 "boto3" module .
def get_dump():
    filestamp = time.strftime(‘%Y-%m-%d-%I’)
    os.popen(“mysqldump -u %s -p%s -h %s -e — opt -c %s | zip -P    <password for zipping the file> > %s.zip” % (user,password,host,database,database+”_”+filestamp))
 
    data_dump = database+”_”+filestamp+”.zip”
    data = open(data_dump, ‘rb’)
    s3 = boto3.resource(‘s3’,
         aws_access_key_id=AWS_ACCESS_KEY_ID,
         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
         config=Config(signature_version=’s3v4')
          )
   try:
     s3.Bucket(S3_BUCKET).put_object(Key= data_dump, Body=data)
   except botocore.exceptions.ClientError as e:
        if e.response[‘Error’][‘Code’] == “404”:
             msg[‘Subject’] = “Dump uploaded failed!”
             body = “Mysql dump failed to upload to S3 “
             msg.attach(MIMEText(body, ‘plain’))
             text = msg.as_string()
             server.sendmail(fromaddr, toaddr, text)
             server.quit()
   else:
           msg[‘Subject’] = “Dump uploaded sucessfully!”
           body = “Mysql dump uploaded to S3 “
           msg.attach(MIMEText(body, ‘plain’))
           text = msg.as_string()
           server.sendmail(fromaddr, toaddr, text)
           server.quit()
           os.popen(“rm -rf ”+data_dump)
if __name__==”__main__”:
 get_dump()
