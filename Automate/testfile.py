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
hname='hadoop.cfg'
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
        #msg = MIMEText(f.read())
        #f.close()
        #attachment = MIMEText(f.read())
        #attachment.add_header('Content-Disposition', 'attachment', filename=files)

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(files, "rb").read())
        Encoders.encode_base64(part)
        #part.add_header('Content-Disposition', 'attachment; filename=files)
        msg.attach(part)
      s=smtplib.SMTP('relay.nw.local',9877)
      s.sendmail('Emr-Map-Reduce-Guard@navmanwireless.com',msg['To'],msg.as_string())
      s.quit

root=os.path.dirname(os.path.abspath(__file__))
logdir=root+ '/logs'
errfile=logdir +'/' + 'dataextract.txt'
subject='Error while copying the Hadoop CFG process'
sendmail(cfg.to,cfg.recv,subject,'',errfile)
sys.exit("Error in Hadoop Copy")



with open(fname) as fina, NamedTemporaryFile(dir='.', delete=False) as fout:
    for line in fina:
        if line.startswith("FILEPATH="):
            line = "FILEPATH="+ cfg.filepath + "\n"
        fout.write(line.encode('utf8'))
    os.rename(fout.name, fname)

with open(hname) as fina, NamedTemporaryFile(dir='.', delete=False) as fout:
    for line in fina:
        if line.startswith("bucket"):
            line = "bucket=\""+  cfg.folder + "\"\n"
        elif line.startswith("region"):
            line = "region=\""+  cfg.region + "\"\n"
        elif line.startswith("sqlServerName="):
            line = "sqlServerName=\""+ cfg.sqlServerName + "\"\n"
        elif line.startswith("LoadAsOfDate="):
            line = "LoadAsOfDate=\""+ cfg.AsOfDate + "\"\n"
        elif line.startswith("database="):
            line = "database=\""+ cfg.database + "\"\n"
        elif line.startswith("dbUN="):
            line = "dbUN=\""+ cfg.dbUN + "\"\n"
        elif line.startswith("dbPass="):
            line = "dbPass=\""+ cfg.dbPass + "\"\n"
        elif line.startswith("awsKey="):
            line = "awsKey=\""+ cfg.awsKey + "\"\n"
        elif line.startswith("awsSecretKey="):
            line = "awsSecretKey=\""+ cfg.awsSecretKey + "\"\n"

        fout.write(line.encode('utf8'))
    os.rename(fout.name,hname)
# Initiating the copy process for hadoop cfg***************************************************
root=os.path.dirname(os.path.abspath(__file__))
logdir=root+ '/logs'
print 'Starting the Hadoop cfg copy process ', time.asctime( time.localtime(time.time()) )

hadoopcfg=['scp','-i',cfg.keypair,'hadoop.cfg',cfg.hadoopcfg]
cfg = subprocess.Popen(hadoopcfg,stdout=open('logs/hadoopcfg.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)
#**************************************
errfile=logdir +'/' + 'hadoopcfg.txt'
ferr=open(errfile, "r")
while cfg.returncode is None:
    cfg.poll()
    time.sleep(10)
    print 'Still running the Data Porting process'
#(output, err) = q.communicate()

errfile=logdir +'/' + 'hadoopcfg.txt'
ferr=open(errfile, "r")

pattern = '*error*'
lines = ferr.readlines()
if lines:
   if fnmatch(lines[-1],pattern):
      subject='Error while copying the Hadoop CFG process'
      ferr.close()
      sendmail(cfg.to,cfg.recv,subject,'',errfile)
      sys.exit("Error in Hadoop Copy")

print 'Hadoop CFG Copy Done ', time.asctime( time.localtime(time.time()) )
ferr.close()
#****************************************
