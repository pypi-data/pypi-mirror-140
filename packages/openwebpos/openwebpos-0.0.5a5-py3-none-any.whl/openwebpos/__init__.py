import os
from pathlib import Path

from flask import Flask, render_template


def create_app(instance_dir=None):
    template_dir = 'ui/templates'
    static_dir = 'ui/static'
    base_path = os.path.abspath(os.path.dirname(__file__))
    home_dir = Path.home()

    if instance_dir is None:
        try:
            os.mkdir(os.path.join(home_dir, '.openwebpos'))
            os.mkdir(os.path.join(home_dir, '.openwebpos/instance'))
        except FileExistsError:
            pass

        try:
            with open(os.path.join(home_dir, ".openwebpos/instance/__init__.py"), "x") as f:
                f.write('')
            with open(os.path.join(home_dir, ".openwebpos/instance/settings.py"), "x") as sf:
                sf.write('')
        except FileNotFoundError:
            print("The 'instance' directory does not exist")
        except FileExistsError:
            pass

        instance_dir = os.path.join(Path.home(), '.openwebpos/instance')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, instance_relative_config=True,
                instance_path=instance_dir)

    app.config.from_pyfile(os.path.join(base_path, 'config/settings.py'))
    app.config.from_pyfile(os.path.join('settings.py'), silent=True)

    print(app.config.get('SECRET_KEY'))

    @app.route('/')
    def index():
        return render_template('index.html', title='Index')

    return app
