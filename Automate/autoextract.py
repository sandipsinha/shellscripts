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


deletefolder=cfg.filepath+ '*'
root=os.path.dirname(os.path.abspath(__file__))
print 'Deleting the Prior Files', deletefolder

deletecmd='rm -f ' + deletefolder

os.system(deletecmd)


localtime=time.asctime( time.localtime(time.time()) )
print 'Starting the Data Extract process ', localtime

Startpgm=root + '/automatebi.sh'

p=subprocess.Popen(Startpgm,stdout=open('logs/dataextract.txt','w'),stdin=PIPE, stderr=PIPE,shell=True)

while p.returncode is None: 
    p.poll()
    time.sleep(20)
    print 'Still running the extract process'
(output, err) = p.communicate()
pattern = '*failed*'
root=os.path.dirname(os.path.abspath(__file__))
logdir=root+ '/logs'
errfile=logdir +'/' + 'dataextract.txt'
ferr=open(errfile, "r")


lines = ferr.readlines()
if lines:
   print 'Last line is ', lines[-1]
   if fnmatch(lines[-1],pattern):
      subject='Error in the data extract process'
      ferr.close()
      sendmail(cfg.to,cfg.recv,subject,'',errfile)
      sys.exit("Error in Data Extract")

print 'Data Extract Done ', time.asctime( time.localtime(time.time()) )
ferr.close()

print 'Now Starting the Data Porting into S3 ' ,time.asctime( time.localtime(time.time()) )
navmanbiline = "/usr/bin/s3cmd sync " + cfg.filepath + " " +  cfg.bucket + " --force"
navmana=['/usr/bin/s3cmd','sync',cfg.filepath,cfg.bucket,'--force']
q = subprocess.Popen(navmana,stdout=open('logs/navmanS3.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)

while q.returncode is None:
    q.poll()
    time.sleep(10)
    print 'Still running the Data Porting process'
#(output, err) = q.communicate()

errfile=logdir +'/' + 'navmanS3.txt'
ferr=open(errfile, "r")

pattern = '*Done*'
lines = ferr.readlines()
if lines:
   if fnmatch(lines[-1],pattern):
      pass
   else:
      subject='Error in the data porting process'
      ferr.close()
      sendmail(cfg.to,cfg.recv,subject,'',errfile)
      sys.exit("Error in Data Porting")

print 'Data porting Done ', time.asctime( time.localtime(time.time()) )
ferr.close()
