import os

from flask import Flask, render_template


def create_app(instance_dir=None):
    template_dir = 'ui/templates'
    static_dir = 'ui/static'
    base_path = os.path.abspath(os.path.dirname(__file__))

    if instance_dir is None:
        instance_dir = os.path.join(os.getcwd(), 'instance')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, instance_relative_config=True,
                instance_path=instance_dir)

    app.config.from_pyfile(os.path.join(base_path, 'config/settings.py'))
    app.config.from_pyfile(os.path.join('settings.py'), silent=True)

    @app.before_first_request
    def before_first_request():
        try:
            os.mkdir(os.path.join(os.getcwd(), 'instance'))
        except FileExistsError:
            pass
        try:
            with open(os.path.join(os.getcwd(), 'instance/__init__.py'), "x") as f1:
                f1.write('')
            with open(os.path.join(os.getcwd(), 'instance/settings.py'), "x") as f2:
                f2.write("SECRET_KEY=''")
        except FileExistsError:
            pass

    print(app.config.get('SECRET_KEY'))

    @app.route('/')
    def index():
        return render_template('index.html', title='Index')

    return app
