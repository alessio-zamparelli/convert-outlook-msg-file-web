import io
import os
import sentry_sdk
from flask import Flask, render_template, request, redirect, send_file, abort
from sentry_sdk.integrations.flask import FlaskIntegration
from outlookmsgfile import load
from dotenv import load_dotenv

load_dotenv()

SENTRY_DSN = os.environ.get("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

app = Flask(__name__)


@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# ...
@app.route('/500')
def error500():
    abort(500)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods=['POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file']
        fname = f.filename.replace('.msg', '.eml')
        msg = load(f.stream)
        msg_b = io.BytesIO(msg.as_bytes())
        try:
            if msg_b is not None:
                return send_file(msg_b, mimetype='application/octet-stream', download_name=fname)
                # return Response(msg.as_bytes(), mimetype='application/octet-stream')
            else:
                return redirect('/errore_di_conversione', code=418)
            # f.save(secure_filename(f.filename))
            # return 'file uploaded successfully'
        except TypeError:
            abort(404)


@app.route('/errore_di_conversione', methods=['GET'])
def errore_di_conversione():
    return render_template('errore_di_conversione.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, port=port)
