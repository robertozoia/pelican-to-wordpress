# pelican-to-wordpress

Pelican To Wordpress is a minimal script for migrating [Pelican](http://pelican.com) posts to Wordpress. (Pelican is a static blog generator written in Python.)

I wrote this script because I needed to export my blog's content to Wordpress, and none of the options I found produced acceptable results (including several Wordpress importer plugins).

## Requirements

* This script has been tested on Python 2.7.10.
* The only required library is python-wordpress-xmlrpc (version 2.3 was used).
* All your posts must be in the same directory. No sub-directories supported. (I know, this sucks.)

~~~
$ pip install python-wordpress-xmlrpc
~~~

## Usage

Open the script in your favorite editor and fill in the following variables:

~~~
WP_SITE_URL = r'http://example.com'
WP_USERNAME = 'wordpress_username'
WP_PASSWORD = r'wordpress_password'
FILE_PATH = r"/path/to/your/posts"
~~~

Run pelicantowordpress.py from the command line:

~~~
$ python pelicantowordpress.py
~~~

Done

## Things to consider

* This script only works for Pelican posts, not pages.
* All posts are exported as 'draft', so you can review them on Wordpress before publishing.
* No media (i.e., images) is exported to Wordpress.  No local URL conversion is done. 

