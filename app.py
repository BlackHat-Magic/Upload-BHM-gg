from dotenv import load_dotenv
import os

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def start():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FLASK_SECRET_KEY
    app.config["S3_ENDPOINT_URL"] = S3_ENDPOINT_URL
    app.config["S3_ACCESS_KEY_ID"] = S3_ACCESS_KEY_ID
    app.config["S3_SECRET_ACCESS_KEY"] = S3_SECRET_KEY
    app.config["S3_BUCKET_NAME"] = S3_BUCKET_NAME
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB limit

    from website import site_main
    # from .api_main import api_main

    app.register_blueprint(site_main, url_prefix="/")

    return app

app = start()

if(__name__ == "__main__"):
	app.run(host="0.0.0.0", debug=True)