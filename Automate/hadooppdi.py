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
hname='hadoop.cfg'
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


#Change the shell script parameter for the local shell script file

with open(fname) as fina, NamedTemporaryFile(dir='.', delete=False) as fout:
    for line in fina:
        if line.startswith("FILEPATH="):
            line = "FILEPATH="+ cfg.filepath + "\n"
        fout.write(line.encode('utf8'))
    os.rename(fout.name, fname)
#****************Now Change the Hadoop cfg file on the EMR Server
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

deletefolder=cfg.filepath+ '*'
root=os.path.dirname(os.path.abspath(__file__))




localtime=time.asctime( time.localtime(time.time()) )
# Initiating the copy process for hadoop cfg***************************************************
root=os.path.dirname(os.path.abspath(__file__))
logdir=root+ '/logs'
print 'Starting the Hadoop cfg copy process ', time.asctime( time.localtime(time.time()) )

hadoopcfg=['scp','-i',cfg.keypair,'hadoop.cfg',cfg.hadoopcfg]
hcfg = subprocess.Popen(hadoopcfg,stdout=open('logs/hadoopcfg.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)
#**************************************
errfile=logdir +'/' + 'hadoopcfg.txt'
ferr=open(errfile, "r")
while hcfg.returncode is None:
    hcfg.poll()
    time.sleep(10)
    print 'Still running the CFG Copy process'
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
print 'Starting the Data Extract process ', localtime

Startpgm=root + '/automatebi.sh'


logdir=root+ '/logs'


# Initiating the PDI process for Dimenison load***************************************************
print 'Starting the Dimension Load process ', time.asctime( time.localtime(time.time()) )

dimarr=['ssh','-i',cfg.keypair,cfg.pdiserver,cfg.pdidim]

dim = subprocess.Popen(dimarr,stdout=open('logs/pdidim.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)

#Now trigger the Hadoop Process to run while the PDI is loading the dimensions#############


print 'Starting the Hadoop process ', time.asctime( time.localtime(time.time()) )

hadoopa=['ssh','-i',cfg.keypair,cfg.hadoopserver,cfg.hadoopdir]
s = subprocess.Popen(hadoopa,stdout=open('logs/hadoop.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)
#**************************************
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
        #sendmail(cfg.to,cfg.recv,subject,'',errfile)
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
#****************************************

print 'Creating a Backup of the days processed data'

bkpgmname = root + '/automatebkup.sh'

bkup=subprocess.Popen(bkpgmname,stdout=open('logs/databkup.txt','w'),stdin=PIPE, stderr=PIPE,shell=True)


#Check if the prior Dimension Load proess has finished successfully.Proceed only if the that job has finished
while dim.returncode is None:
    dim.poll()
    time.sleep(10)
    print 'Still running the Dimension Load process'

errfile=logdir +'/' + 'pdidim.txt'
ferr=open(errfile, "r")

pattern = '*errors*'
lines = ferr.readlines()

if lines:
   for items in lines:
     if fnmatch(items,pattern):
        subject='Error in the Dimension Load process'
        ferr.close()
        #sendmail(cfg.to,cfg.recv,subject,'',errfile)
        sys.exit("Error in Dimension Load")


print 'Starting PDI Fact Load process ', time.asctime( time.localtime(time.time()) )
pdiarr=['ssh','-i',cfg.keypair,cfg.pdiserver,cfg.pdifact]
t = subprocess.Popen(pdiarr,stdout=open('logs/pdifact.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)

while t.returncode is None:
    t.poll()
    time.sleep(10)
    print 'Still running the PDI Fact Load  process'

print 'PDI Fact Load Process finished ', time.asctime( time.localtime(time.time()) )

pattern = "*errors*"
logdir=root+ '/logs'

errfile=logdir +'/' + 'pdifact.txt'
if os.path.isfile(errfile):
  ferr=open(errfile, "r")
  lines = ferr.readlines()
  if lines:
     if fnmatch(lines[-1],pattern):
       subject='Error in the PDI fact loadprocess'
       ferr.close()
       #sendmail(cfg.to,cfg.recv,subject,'',errfile)
       sys.exit("Error in PDI fact load")
else: 
  subject='Error in the PDI fact load process'
  ferr.close()
  #sendmail(cfg.to,cfg.recv,subject,'',errfile)
  sys.exit("Error in PDI fact load")

print 'PDI Fact Load Process finished isuccessfully ', time.asctime( time.localtime(time.time()) )
