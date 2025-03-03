from flask import render_template, Blueprint, request, redirect, url_for, flash, current_app, abort
from werkzeug.utils import secure_filename
import random, boto3, urllib.parse, re

site_main = Blueprint("site_main", __name__)

def shortid(length:int=8):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_"
    return("".join(random.choice(characters) for _ in range(length)))

@site_main.route("/")
def home():
    if(request.method == "POST"):
        reason = secure_filename(reason)
        if(not reason):
            reason = "misc"
        home_redirect = redirect(f"{url_for('site_main.success', file_id=unique_name)}" + (f"reason={reason}" if reason else ""))

        if("file" not in request.files):
            flash("No file selected", "red")
            return(home_redirect)
            
        file = request.files["file"]
        if(file.filename == ""):
            flash("No file selected", "red")
            return(home_redirect)
        
        # Server-side size check
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset pointer
        
        if(file_size > 1 * 1024 * 1024 * 1024):
            flash("File size exceeds 1 GiB", "red")
            return(home_redirect)
        
        # Generate unique filename
        name = secure_filename(file.filename)
        if(not name):
            name = "file"
        unique_name = f"{reason}/{shortid()}.{name}"
        
        try:
            current_app.config["S3_CLIENT"].upload_fileobj(file, current_app.config["S3_BUCKET_NAME"], unique_name)
        except Exception as e:
            flash("File upload failed", "red")
            return(home_redirect)
            
        return redirect(home_redirect)

    reason = request.args.get("reason", None)
    return(render_template("index.html", title="Home", reason=reason))

@site_main.route("/success")
def success():
    file_id = request.args.get("file_id")
    if(not file_id):
        return(redirect(url_for("site_main.home")))
    file_url = url_for("site_main.file", file_id=file_id, _external=True)
    return(render_template("success.html", file_url=file_url))

@site_main.route("/f/<path:file_path>")
def file(file_id):
    file_path = urllib.parse.unquote(file_path)
    s3_key = file_path

    try:
        s3_obj = current_app.config["S3_CLIENT"].get_object(
            Bucket=current_app.config["S3_BUCKET_NAME"],
            Key=file_id
        )
    except s3.exceptions.NoSuchKey:
        abort(404)
    except s3.exceptions.ClientError:
        abort(404)
    except Exception as e:
        print(f"Error retrieving file: {e}")
        abort(404)

    filename = os.path.basename(file_path)
    og_filename_list = filename.split(".")
    og_filename_list.pop(0)
    og_filename = ".".join(s for s in og_filename_list)

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