from flask import render_template, Blueprint, request, redirect, url_for, flash, current_app, abort, Response
from werkzeug.utils import secure_filename
import random, boto3, urllib.parse, re, os, magic

site_main = Blueprint("site_main", __name__)

def shortid(length:int=8):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_"
    return("".join(random.choice(characters) for _ in range(length)))

@site_main.route("/", methods=["GET", "POST"])
def home():
    reason = request.args.get("reason", "misc")
    reason = secure_filename(reason)
    if(not reason):
        reason = "misc"
    if(request.method == "POST"):
        home_redirect = redirect(f"{url_for('site_main.home')}" + (f"?reason={reason}" if reason else ""))
            
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
        try:
            mime = magic.Magic(mime=True)
            file_data = file.read(2048)
            file.seek(0)
            content_type = mime.from_buffer(file_data)
        except Exception as e:
            print(e)
            content_type = "application/octet-stream"
        
        # Generate unique filename
        name = secure_filename(file.filename)
        if(not name):
            name = "file"
        unique_name = f"{reason}/{shortid()}.{name}"
        print(file_size)
        
        try:
            current_app.config["S3_CLIENT"].upload_fileobj(
                Key=unique_name,
                Bucket=current_app.config["S3_BUCKET_NAME"],
                Fileobj=file,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {
                        "original-filename": file.filename
                    }
                }
                # ContentLength=file_size
            )
        except Exception as e:
            flash("File upload failed", "red")
            print(e)
            return(home_redirect)
            
        return(redirect(url_for('site_main.success', file_path=unique_name)))

    return(render_template("index.html", title="Home", reason=reason))

@site_main.route("/success/<path:file_path>")
def success(file_path):
    # reason = request.args.get("reason")
    # name = request.args.get("name")
    # file_id = request.args.get("file_id")
    # if(not name or not reason):
    #     return(redirect(url_for("site_main.home")))
    # file_url = url_for("site_main.file", file_path=file_path, _external=True)
    file_url = f"https://upload.bhm.gg/f/{file_path}"
    return(render_template("success.html", file_url=file_url))

@site_main.route("/f/<path:file_path>")
def file(file_path):
    file_path = urllib.parse.unquote(file_path)
    s3_key = file_path

    try:
        s3_obj = current_app.config["S3_CLIENT"].get_object(
            Bucket=current_app.config["S3_BUCKET_NAME"],
            Key=file_path
        )
    except Exception as e:
        print(f"Error retrieving file: {e}")
        abort(404)

    filename = os.path.basename(file_path)
    og_filename_list = filename.split(".")
    og_filename_list.pop(0)
    og_filename = ".".join(s for s in og_filename_list)

    content_type = s3_obj["ContentType"]
    original_filename = s3_obj["Metadata"].get("original_filename", og_filename)

    disposition = "attachment"
    if(content_type.startswith("image/")):
        disposition = "inline"
    elif(content_type == "application/pdf"):
        disposition = "inline"
    elif(content_type.startswith("video/")):
        disposition = "inline"

    headers = {
        "Content-Type": s3_obj["ContentType"],
        "Content-Disposition": f"{disposition}; filename=\"{og_filename}\"",
        "Content-Length": str(s3_obj["ContentLength"])
    }
    return Response(
        s3_obj["Body"].iter_chunks(),
        headers=headers,
        direct_passthrough=True
    )
