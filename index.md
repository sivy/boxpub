# Boxpub

Boxpub is a very simple script that makes it moderately easy to run a blog from your Dropbox.

### Pre-requisites

1. A Dropbox Account
2. A Dropbox developer account
3. A Dropbox app - it can be in "develop" mode
4. A web host that can run python apps
5. Knowledge of the Linux Arcanacus

Open up the settings for your Dropbox application and find the "Generated access token" section. Click the button to generate a token and copy it.

### Installation

    % mkdir /opt/
    % cd /opt/
    % git clone https://github.com/sivy/boxpub.git
    % cd boxpub
    % virtualenv env
    % source env/bin/activate
    (env) % pip install -r requirements
    (env) % pip install .

    % sudo ./gunicorn_start

### Configuration

Installation will put a basic config file in `/etc/boxpub/config.py`. Edit this file to add your generated token where it says:

    DROPBOX_PRIVATE_TOKEN = '<your token here>'

### Using Boxpub

Important locations and things:

* `Dropbox/apps/boxpub/posts`: Your blog posts go here, in `YYYY-MM-DD-post-title.md` format, and require a minimal YAML-format header
* `Dropbox/apps/boxpub/templates`:
    - `index.html`
    - `post.html`
    - `archive.html`



### Thanks

* Gunicorn and Supervisor setup. <http://prakhar.me/articles/flask-on-nginx-and-gunicorn/>
* asciiart! <http://patorjk.com/software/taag/>