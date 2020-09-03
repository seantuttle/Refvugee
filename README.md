# Refvugee

A small blog-style website I built with help from the Django tutorial
by Corey Schafer (highly recommended). I originally made it for a school
project, but ended up not needing it because of COVID complications. I stopped
working on it after that, so that is why it is incomplete.

On this site, a person can make posts and write comments if they have signed
up for an account. There is a comment reporting system where an email will be
sent to some administrator if a comment is reported. There are also post notifcations
built in as a toggleable option for users. Note that no email functions currently
work since there is no email specified (to do this, go to settings.py and enter
email info). There is also a really simple keyword search function that looks for
any posts that contain one or multiple of the given key words.

This site uses sqlite for its database backend, so you'll need to do some
initial migrations to create a sqlite database on your machine. To do this,
run the following commands:
manage.py makemigrations
manage.py migrate

When you are ready to make the site live, use the command manage.py runserver
and then follow the link to the server running on your localhost.