from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

# Create extensions instances
db = SQLAlchemy()
migrate = Migrate()
mail = Mail() 