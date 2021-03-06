
from flask import Flask
from flask_cors import CORS
from config import ProductionConfig

# initialize the app
app = Flask(__name__, instance_relative_config=True)

# allows us to make requests from one website to another website in the browser 
cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# load the views
from app import views

# load the models
from app import models


# load the config file
app.config.from_object(ProductionConfig)
