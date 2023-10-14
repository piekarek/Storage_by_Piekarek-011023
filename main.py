from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from models import User, Primer, PrimerList, db
from auth import auth
from flask_migrate import Migrate, upgrade, init
import os
from flask_mail import Mail
from forms import PrimerForm
from models import PrimerList

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

    @app.route('/add_primer', methods=['GET', 'POST'])
    @login_required
    def add_primer():
        form = PrimerForm()
        if form.validate_on_submit():
            primer = Primer(
                application=form.application.data,
                pcr=form.pcr.data,
                target=form.target.data,
                oligos=form.oligos.data,
                sequence=form.sequence.data,
                box=form.box.data,
                position=form.position.data,
                reference=form.reference.data,
                comment=form.comment.data
            )
            db.session.add(primer)
            db.session.commit()
            flash('Primer added successfully!', 'success')
            return redirect(url_for('primers'))
        return render_template('add_primer.html', form=form)

    @app.route('/primers')
    @login_required
    def primers():
        all_primers = Primer.query.all()
        return render_template('primers.html', primers=all_primers)

    @app.route('/get_primer_lists', methods=['GET'])
    @login_required
    def get_primer_lists():
        user_lists = PrimerList.query.filter_by(user_id=current_user.id).all()
        return jsonify({"primerLists": [list.name for list in user_lists]})

    @app.route('/add_primer_list', methods=['POST'])
    @login_required
    def add_primer_list():
        list_name = request.form.get('list_name')
        if not list_name:
            return jsonify(success=False, message="List name is required"), 400

        existing_list = PrimerList.query.filter_by(name=list_name, user_id=current_user.id).first()
        if existing_list:
            return jsonify(success=False, message="List with this name already exists"), 400

        primer_list = PrimerList(name=list_name, user_id=current_user.id)
        db.session.add(primer_list)
        db.session.commit()
        return jsonify(success=True, message="Primer list added successfully")

    @app.route('/edit_primer/<int:primer_id>', methods=['GET', 'POST'])
    @login_required
    def edit_primer(primer_id):
        primer = Primer.query.get_or_404(primer_id)
        form = PrimerForm(obj=primer)
        if form.validate_on_submit():
            primer.application = form.application.data
            primer.pcr = form.pcr.data
            primer.target = form.target.data
            primer.oligos = form.oligos.data
            primer.sequence = form.sequence.data
            primer.box = form.box.data
            primer.position = form.position.data
            primer.reference = form.reference.data
            primer.comment = form.comment.data
            db.session.commit()
            flash('Primer updated successfully!', 'success')
            return redirect(url_for('primers'))
        return render_template('edit_primer.html', form=form, primer=primer)

    @app.route('/delete_primers', methods=['POST'])
    @login_required
    def delete_primers():
        ids_to_delete = request.json.get('ids', [])
        try:
            Primer.query.filter(Primer.id.in_(ids_to_delete)).delete(synchronize_session='fetch')
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, message=str(e))

    return app

    @app.route('/create_primer_list', methods=['POST'])
    @login_required
    def create_primer_list():
        try:
            data = request.get_json()
            new_list = PrimerList(name=data['name'], user_id=current_user.id)
            db.session.add(new_list)
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, message=str(e))



app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
