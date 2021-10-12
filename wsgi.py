import os
import sys
sys.path.append("/var/www/html/slddb")
os.chdir('/var/www/html/slddb')
from flaskr import app as application
