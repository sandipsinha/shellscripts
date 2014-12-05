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

print 'Deleting the Prior Files', deletefolder

deletecmd='rm -f ' + deletefolder

os.system(deletecmd)


print 'Starting the Data Extract process'

p=subprocess.Popen('/home/pythonautomate/Automate/automatebi.sh',stdout=open('logs/dataextract.txt','w'),stdin=PIPE, stderr=PIPE,shell=True)

while p.returncode is None: 
    p.poll()
    time.sleep(20)
    print 'Still running the extract process'
(output, err) = p.communicate()
pattern = '*Done*'
root=os.path.dirname(os.path.abspath(__file__))
logdir=root+ '/logs'
errfile=logdir +'/' + 'dataextract.txt'
ferr=open(errfile, "r")


lines = ferr.readlines()
if lines:
   print 'Last line is ', lines[-1]
   if fnmatch(lines[-1],pattern):
      pass
   else:
      subject='Error in the data extract process'
      ferr.close()
      sendmail(cfg.to,cfg.recv,subject,'',errfile)
      sys.exit("Error in Data Extract")

print 'Data Extract Done'
ferr.close()
