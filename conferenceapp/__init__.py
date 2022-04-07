from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail, Message

from flask_wtf.csrf import CSRFProtect

from flask_migrate import Migrate

#Instantiate an object of flask
app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect(app)


#Local imports start here
from conferenceapp import config
app.config.from_object(config.ProductionConfig)
#load below the config from instance folder
app.config.from_pyfile('config.py', silent=False)

db = SQLAlchemy(app)
#instantiate mail after loding config files
mail = Mail(app)
migrate= Migrate(app,db)


#Load your routes/views
from conferenceapp.myroutes import adminroutes, userroutes #since routes is now a module of its own
from conferenceapp import forms, mymodels