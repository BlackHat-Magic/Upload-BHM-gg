from botocore.client import Config
from flask import Flask
from dotenv import load_dotenv
import os, boto3

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION_NAME = os.getenv("S3_REGION_NAME")

def start():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FLASK_SECRET_KEY
    app.config["S3_BUCKET_NAME"] = S3_BUCKET_NAME
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB limit

    s3 = boto3.client(
        "s3",
        region_name=S3_REGION_NAME,
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version="s3v4")
    )
    app.config["S3_CLIENT"] = s3

    from site_main import site_main
    # from .api_main import api_main

    app.register_blueprint(site_main, url_prefix="/")

    return app

app = start()

if(__name__ == "__main__"):
	app.run(host="0.0.0.0", debug=True)