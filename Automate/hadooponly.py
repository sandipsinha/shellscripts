import subprocess
import os,os.path,time
import sys
import fileinput
from config import Config 
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from fnmatch import fnmatch
import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

fname='automatebi.properties'
f = file('automate.cfg')
cfg = Config(f)

def sendmail(to,fromi,subject,content,files):
   if to is not None:
      msg = MIMEMultipart()
      msg['Subject'] = subject
      msg['From'] = fromi
      msg['To'] = to
      if files is not None:
        f=open(files,'rb') 
        attachment = MIMEText(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=files) 

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(files, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="email.txt"')
        msg.attach(part)
      s=smtplib.SMTP('relay.nw.local',9877)
      s.sendmail('Emr-Map-Reduce-Guard@navmanwireless.com',msg['To'],msg.as_string())
      s.quit




with open(fname) as fina, NamedTemporaryFile(dir='.', delete=False) as fout:
    for line in fina:
        if line.startswith("FILEPATH="):
            line = "FILEPATH="+ cfg.filepath + "\n"
        fout.write(line.encode('utf8'))
    os.rename(fout.name, fname)


root=os.path.dirname(os.path.abspath(__file__))




localtime=time.asctime( time.localtime(time.time()) )



logdir=root+ '/logs'


print 'Starting the Hadoop process ', time.asctime( time.localtime(time.time()) )

hadoopa=['ssh','-i',cfg.keypair,cfg.hadoopserver,cfg.hadoopdir]
s = subprocess.Popen(hadoopa,stdout=open('logs/hadoop.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)

errfile=logdir +'/' + 'hadoop.txt'
ferr=open(errfile, "r")
patterne = '*failed*'
patterns = '*SUCCESSFULLY*'
breakind = 'N'

while 1:
 lines = ferr.readlines()
 if lines:   
   for items in lines:
     if fnmatch(items,patterne):
        subject='Error in the Hadoop process'
        ferr.close()
        sendmail(cfg.to,cfg.recv,subject,'',errfile)
        sys.exit("Error in Hadoop")
     elif  fnmatch(items,patterns):
        subject='Hadoop process Successfully'
        breakind = 'Y'
        break
 if breakind == 'Y':
    break
 time.sleep(10)
 print 'Still running the Hadoop process'   
print 'Hadoop Process finished'

