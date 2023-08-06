from flask import Flask, render_template


def create_app():
    template_dir = 'ui/templates'
    static_dir = 'ui/static'

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    @app.route('/')
    def index():
        return render_template('index.html', title='Index')

    return app
