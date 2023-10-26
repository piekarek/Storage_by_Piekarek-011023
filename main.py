from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from models import User, db, PrimerList, Primer, primer_list_association  # Import the PrimerList model
from auth import auth
from flask_migrate import Migrate, upgrade, init
import os
from flask_mail import Mail

def create_app():
    app = Flask(__name__)

    # App-Konfiguration
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Datenbank-Initialisierung
    db.init_app(app)
    migrate = Migrate(app, db)

    # Login-Manager-Initialisierung
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # E-Mail-Konfiguration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'bypiekarek@gmail.com'
    app.config['MAIL_PASSWORD'] = 'ccfz kujg ssqo djbf'

    mail = Mail(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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

    @app.route('/migrate')
    def migrate_db():
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'migrations')):
            init(directory=os.path.join(os.path.dirname(__file__), 'migrations'))

        with app.app_context():
            upgrade()

        if not User.query.filter_by(is_admin=True).first():
            admin = User(email="admin@example.com", name="Admin", is_approved=True, is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        return "Migration durchgeführt und Datenbank aktualisiert!"

    @app.route('/primers')
    @login_required
    def primers():
        # Get all the primer lists ordered by visibility and then by name
        primer_lists = PrimerList.query.order_by(PrimerList.visibility, PrimerList.name).all()
        return render_template('primers.html', primer_lists=primer_lists)

    @app.route('/get-primers-for-list/<int:primerListId>', methods=['GET'])
    def get_primers_for_list(primerListId):
        # Fetch the associated primers from the database
        primers = db.session.query(Primer).join(primer_list_association).filter(
            primer_list_association.c.primer_list_id == primerListId).all()
        # Convert the primers to a format suitable for DataTables and return
        primer_data = [primer.serialize for primer in primers]

        return jsonify(primer_data)

    @app.route('/add_primer_list', methods=['POST'])
    @login_required
    def add_primer_list():
        name = request.form.get('name')
        visibility = request.form.get('visibility')
        user_id = current_user.id

        if not name or not visibility:
            return jsonify({'status': 'error', 'message': 'Name und Sichtbarkeit sind erforderlich.'}), 400

        new_primer_list = PrimerList(name=name, visibility=visibility, user_id=user_id)
        db.session.add(new_primer_list)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Primer-Liste erfolgreich erstellt.',
                        'primer_list': {'id': new_primer_list.id, 'name': new_primer_list.name,
                                        'visibility': new_primer_list.visibility}})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)