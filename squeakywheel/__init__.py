from flask import Flask
app = Flask(__name__)
import sys,os
cwd = os.path.abspath(os.path.dirname(__file__))
print(cwd)
sys.path.append(cwd+'/')
from squeakywheel import views
