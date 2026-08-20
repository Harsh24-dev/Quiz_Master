from flask import Flask
from backend.models import db
from backend.api_controllers import *

app = None

def setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_db.sqlite3"
    db.init_app(app)
    api.init_app(app)
    app.app_context().push() #Create an app context so the app is accessible globally
    db.create_all()
    app.debug=True
    print("Quiz Master app started.")

setup_app()

from backend.controllers import *

if __name__ == "__main__":
    app.run(debug=True) #Run Flask app