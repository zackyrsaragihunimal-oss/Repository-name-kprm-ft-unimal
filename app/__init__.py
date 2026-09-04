from flask import Flask
from .config import Config
from .extensions import db, login_manager, csrf, migrate
import os


def create_app(config_class=Config):

    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Ensure folders exist
    for folder in [
        app.config['UPLOAD_FOLDER'],
        app.config['BACKUP_FOLDER']
    ]:
        os.makedirs(folder, exist_ok=True)

    for sub in [
        'candidates',
        'coalitions',
        'news',
        'gallery',
        'documents'
    ]:
        os.makedirs(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                sub
            ),
            exist_ok=True
        )

    # =====================================================
    # REGISTER BLUEPRINTS
    # =====================================================

    from .routes.public import public_bp
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.voters import voters_bp
    from .routes.candidates import candidates_bp
    from .routes.coalitions import coalitions_bp
    from .routes.organizations import organizations_bp
    from .routes.elections import elections_bp
    from .routes.polling import polling_bp

    # PENTING:
    # votes_bp = operator
    # public_votes_bp = pemilih
    from .routes.votes import votes_bp, public_votes_bp

    from .routes.content import content_bp
    from .routes.settings_routes import settings_bp
    from .routes.backup import backup_bp
    from .routes.audit import audit_bp
    from .routes.users import users_bp
    from .routes.api import api_bp

    # Public
    app.register_blueprint(public_bp)

    # Authentication
    app.register_blueprint(
        auth_bp,
        url_prefix='/auth'
    )

    # Admin
    app.register_blueprint(
        dashboard_bp,
        url_prefix='/admin'
    )

    app.register_blueprint(
        voters_bp,
        url_prefix='/admin/voters'
    )

    app.register_blueprint(
        candidates_bp,
        url_prefix='/admin/candidates'
    )

    app.register_blueprint(
        coalitions_bp,
        url_prefix='/admin/coalitions'
    )

    app.register_blueprint(
        organizations_bp,
        url_prefix='/admin/organizations'
    )

    app.register_blueprint(
        elections_bp,
        url_prefix='/admin/elections'
    )

    app.register_blueprint(
        polling_bp,
        url_prefix='/admin/polling'
    )

    # Operator voting
    app.register_blueprint(
        votes_bp,
        url_prefix='/admin/votes'
    )

    # Public voting
    app.register_blueprint(
        public_votes_bp,
        url_prefix='/votes'
    )

    app.register_blueprint(
        content_bp,
        url_prefix='/admin/content'
    )

    app.register_blueprint(
        settings_bp,
        url_prefix='/admin/settings'
    )

    app.register_blueprint(
        backup_bp,
        url_prefix='/admin/backup'
    )

    app.register_blueprint(
        audit_bp,
        url_prefix='/admin/audit'
    )

    app.register_blueprint(
        users_bp,
        url_prefix='/admin/users'
    )

    # API
    app.register_blueprint(
        api_bp,
        url_prefix='/api'
    )

    # =====================================================
    # CONTEXT PROCESSOR
    # =====================================================

    @app.context_processor
    def inject_settings():

        from .models.system import Setting

        try:

            settings = {}

            for s in Setting.query.all():
                settings[s.key] = s.value

            return dict(
                site_settings=settings
            )

        except Exception:

            return dict(
                site_settings={}
            )

    return app