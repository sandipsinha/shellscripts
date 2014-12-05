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



localtime=time.asctime( time.localtime(time.time()) )
print 'Starting the Data Extract process ', localtime

Startpgm=root + '/automatebi.sh'


logdir=root+ '/logs'


# Initiating the PDI process for Dimenison load***************************************************
print 'Starting the Dimension Load process ', time.asctime( time.localtime(time.time()) )

dimarr=['ssh','-i',cfg.keypair,cfg.pdiserver,cfg.pdidim]

dim = subprocess.Popen(dimarr,stdout=open('logs/pdidim.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)

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
        sendmail(cfg.to,cfg.recv,subject,'',errfile)
        sys.exit("Error in Dimension Load")



print 'Finished PDI Dim Load process ', time.asctime( time.localtime(time.time()) )

#print 'Starting PDI Fact Load process ', time.asctime( time.localtime(time.time()) )
#pdiarr=['ssh','-i',cfg.keypair,cfg.pdiserver,cfg.pdifact]
#t = subprocess.Popen(pdiarr,stdout=open('logs/pdifact.txt','w'),stdin=PIPE, stderr=PIPE,shell=False)

#while t.returncode is None:
#    t.poll()
#    time.sleep(10)
#    print 'Still running the PDI Fact Load  process'
#
#print 'PDI Fact Load Process finished ', time.asctime( time.localtime(time.time()) )

#pattern = "*Done*"
#logdir=root+ '/logs'

#errfile=root +'/' + 'pdifact.txt'
#if os.path.isfile(errfile):
#  ferr=open(errfile, "r")
#  lines = ferr.readlines()
#  if lines:
#     if fnmatch(lines[-1],pattern):
#        pass
#     else:
#       subject='Error in the PDI fact loadprocess'
#       ferr.close()
#       sendmail(cfg.to,cfg.recv,subject,'',errfile)
#       sys.exit("Error in PDI fact load")
#else: 
#       subject='Error in the PDI fact load process'
#       ferr.close()
#       sendmail(cfg.to,cfg.recv,subject,'',errfile)
#       sys.exit("Error in PDI fact load")
