I have a boilerplate flask app with the following file structure:

```
.
├── .env
├── app.py
└── website
    ├── __init__.py
    ├── models.py
    ├── site_main.py
    ├── static
    │   ├── css
    │   │   // various css files (unimportant for this task)
    │   └── js
    │       ├── index.js
    │       └── master.js
    └── templates
        ├── index.html
        └── master.html
```

The file contents are as follows:

.env:
```
SQLITE_DB_NAME=<database file name>
FLSAK_SECRET_KEY=<secret key>
// other environment variables
```

app.py:
```python
from dotenv import load_dotenv
import os

load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
if(not FLASK_SECRET_KEY):
    raise ValueError("`FLASK_SECRET_KEY` environment variable not set.")

def start():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = FLASK_SECRET_KEY

    from website import site_main
    # from .api_main import api_main

    app.register_blueprint(site_main, url_prefix="/")

    return app

app = start()

if(__name__ == "__main__"):
	app.run(host="0.0.0.0", debug=True)
```

site_main.py:
```python
from flask import render_template, Blueprint
import random

site_main = Blueprint("site_main", __name__)

def shortid(length):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_"
    return("".join(random.choice(characters) for _ in range(length)))

@site_main.route("/")
def home():
    reason = request.args.get("reason", None)
    return(render_template("index.html", title="Home", reason=reason))

@site_main.route("/success")
def success():
    file_id = request.args.get("file_id")
    if(not file_id):
        return(redirect(url_for("site_main.home")))
    # you write this file
    return(render_template("success.html"))

@site_main.route("/<string:file_id>")
def file(file_id):
    # some more code here
    pass
```

index.js:
```javascript
document.addEventListener ("alpine:init", () => {
    Alpine.data ("main", () => ({
        file: null,
        modal: false,
        parse () {
            file = event.target.files[0];
            if(file.size > 1 * 1024 * 1024 * 1024) {
                this.modal = true;
                event.target.value = null;
            }
        },
    }))
})
```

master.js:
```javascript
document.addEventListener ("alpine:init", () => {
    Alpine.data ("master", () => ({
        flashes: [],
    }))
})
```

index.html:
```html
{% extends "master.html" %}

{% block head %}
<script src="{{ url_for('static', filename='js/index.js') }}"></script>
{% endblock %}

{% block body %}
<div class="flex">
    <form class="flex vertical start" method="post" x-data="main">
        <h1>Upload a file</h1>
        <label for="file"><h2>Upload a File</h2></label>
        <input
            type="file"
            id="file"
            name="file"
            x-model="file"
            @change="parse ()">

        <a><button type="submit">Upload!</button></a>
        <div class="modal" x-show="modal" @click="modal = !modal"></div>
        <div class="modal-alert flex vertical start" x-show="modal">
            <h1>Yout Files are Too Powerful!</h1>
            <p>The maximum file size is 1 GiB</p>
            <a><button @click="modal = !modal" type="button">Gotcha!</button></a>
        </div>
    </form> 
</div>
{% endblock %}
```

master.html:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie-edge">
    <link rel="icon" type="image/x-ixon" href="{{ url_for('static', filename='images/d20.png') }}">
	<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
	<link rel="stylesheet" href="{{ url_for('static', filename='css/text.css') }}">
	<link rel="stylesheet" href="{{ url_for('static', filename='css/input.css') }}">
	<link rel="stylesheet" href="{{ url_for('static', filename='css/containers.css') }}">
	<link rel="stylesheet" href="{{ url_for('static', filename='css/ui.css') }}">
	<link rel="stylesheet" href="{{ url_for('static', filename='css/markdown.css') }}">
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Noto+Sans&display=swap" rel="stylesheet">	
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
	<!-- <script src="https://unpkg.com/showdown/dist/showdown.min.js"></script> -->
	<!-- <script src="https://unpkg.com/htmx.org@1.9.9"></script> -->
	<script src="{{ url_for('static', filename='js/master.js') }}"></script>
	<title>{{ title }} | Wayfarer {{ cruleset.name }}</title>
	{% block head %}{% endblock %}
</head>

<body>

{% with messages = get_flashed_messages(with_categories=true) %}
	{% for category, message in messages %}
		<div class="interior flex horizontal center {{ category }} bar" x-data="{ dismissed: false }" x-show="!dismissed">
			<span style="width: calc(100% - 80px)">{{ message }}</span>
			<a style="margin: 0" @click="dismissed = !dismissed">
				<span>&times</span>
			</a>
		</div>
	{% endfor %}
{% endwith %}

{% block body %}{% endblock %}

<div class="flex" style="background-color: inherit">
	<div class="flex horizontal center" style="background-color: inherit">
		<span class="small">
			<a href="https://github.com/BlackHat-Magic/Upload-BHM-gg" target="_blank">View Source Code</a></span>
	</div>
</div>
</body>
</html>
```

I want the app to take the user's file, verify that it is under 1GiB (server-side; I think client side already works), then upload it to an s3 bucket. The file name in the s3 bucket should be the name of the file that got uploaded plus some random string generated with the `shortid` function (8 characters should be enough since it offers almost 300 trillion possibilities).

It then returns a link to the `success` endpoint, which displays a page structured similarly to the `index.html` page that only has a button that copies a URL to the flask site that returns the s3 file to the clipboard.

The `file` endpoint should return the file with the specified ID/key from the s3 bucket (similar to `proxy_pass` in nginx) provided in the URL. If it doesn't exist, it should 404.

Can you do that for me please? Also, fix any bugs you find in my code if you can. Explain your additions and changes.