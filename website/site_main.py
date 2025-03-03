from flask import render_template, Blueprint, request, redirect, url_for, flash, current_app, abort
from werkzeug.utils import secure_filename
import random, boto3

site_main = Blueprint("site_main", __name__)

def shortid(length):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_"
    return("".join(random.choice(characters) for _ in range(length)))

@site_main.route("/")
def home():
    if(request.method == "POST"):
        if("file" not in request.files):
            flash("No file selected", "red")
            return(redirect(url_for("site_main.home")))
            
        file = request.files["file"]
        if(file.filename == ""):
            flash("No file selected", "red")
            return redirect(url_for("site_main.home"))
        
        # Server-side size check
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset pointer
        
        if(file_size > 1 * 1024 * 1024 * 1024):
            flash("File size exceeds 1 GiB", "red")
            return(redirect(url_for("site_main.home")))
        
        # Generate unique filename
        original_name = secure_filename(file.filename)
        unique_name = f"{original_name}-{shortid()}"
        
        # Upload to S3
        s3 = boto3.client(
            "s3",
            endpoint_url=current_app.config["S3_ENDPOINT_URL"],
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"]
        )
        
        try:
            s3.upload_fileobj(file, current_app.config["S3_BUCKET_NAME"], unique_name)
        except Exception as e:
            flash("File upload failed", "red")
            return(redirect(url_for("site_main.home")))
            
        return redirect(url_for("site_main.success", file_id=unique_name))
    reason = request.args.get("reason", None)
    return(render_template("index.html", title="Home", reason=reason))

@site_main.route("/success")
def success():
    file_id = request.args.get("file_id")
    if(not file_id):
        return(redirect(url_for("site_main.home")))
    file_url = url_for("site_main.file", file_id=file_id, _external=True)
    return(render_template("success.html", file_url=file_url))

@site_main.route("/file/<string:file_id>")
def file(file_id):
    s3 = boto3.client(
        "s3",
        endpoint_url=current_app.config["S3_ENDPOINT_URL"],
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"]
    )

    try:
        s3_obj = s3.get_object(
            Bucket=current_app.config["S3_BUCKET_NAME"],
            Key=file_id
        )
    except s3.exceptions.NoSuchKey:
        abort(404)
    except s3.exceptions.ClientError:
        abort(404)

    # Extract original filename from the stored key
    original_filename = file_id.rsplit("-", 1)[0]

    headers = {
        "Content-Type": s3_obj["ContentType"],
        "Content-Disposition": f"attachment; filename=\"{original_filename}\"",
        "Content-Length": str(s3_obj["ContentLength"])
    }

    return Response(
        s3_obj["Body"].iter_chunks(),
        headers=headers,
        direct_passthrough=True
    )