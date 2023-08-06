from flask import Flask, render_template


def create_app(owpos_instance_path=None):
    template_dir = 'ui/templates'
    static_dir = 'ui/static'

    if owpos_instance_path is None:
        raise Exception("Please create an instance directory with an __init__.py and settings.py file.")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, instance_relative_config=True,
                instance_path=owpos_instance_path)

    app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    @app.route('/')
    def index():
        return render_template('index.html', title='Index')

    return app
