# The Magical Dropbox-Blogging Castle

Once upon a time there were web apps that let you save a  file on your Dropbox, in a special folder, and that file would become a blog post. This was magical.

These web apps were nice, but not updated often, and only worked on a slow polling process because Dropbox (that's all the reason anyone who knew, needed).

One day, a boy came along and said "these are well and nice but the experience could be even better!" Because he was a programmer and was therefore both lazy and full of hubris, he began to stir his magic pot, and then began to build his Castle. The boy built and built, and others saw what he was building and thought it was pretty good. It was easy to use, had bidirectional syncing with the web UI, and was faster to update than the other web apps.

Sadly, because the boy was a programmer, and both lazy and full of hubris, he was actually shite at marketing and maintenance. His magic Dropbox-blogging castle fell into disrepair until one day, the foundation crumbled and the boy was forced to apologize to his tenants and allow [Castle Markbox](http://markbox.io) to fall.

The boy, dejected, tried to imagine blogging another way, and failed.

Then, he thought... "I don't need a **magic castle**, *I just need the magic*."

This is what he did next.

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