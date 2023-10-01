from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from models import User, db
from auth import auth

def create_app():
    app = Flask(__name__)

    # App-Konfiguration
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Ändern Sie dies in einem echten Projekt!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Datenbank-Initialisierung
    db.init_app(app)

    # Login-Manager-Initialisierung
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints registrieren
    app.register_blueprint(auth)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html', name=current_user.name)

    @app.route('/create_db')
    def create_db():
        with app.app_context():
            db.create_all()
        return "Datenbank erstellt!"

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
