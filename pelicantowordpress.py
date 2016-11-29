# -*- coding: utf-8

#
# Pelican to Wordpress exporter.
# Written by Roberto Zoia 2016-11-29
#
# This is a minimum-functionality script that migrates Pelican posts
# to WordPress.
#
# * Assumes that Pelican posts are in Markdown
# * All posts must be in the same directory (I know, this may suck for some
#  people, you are invited to modify the code using os.walk, etc.)
# * Does not export media content to Wordpress nor converts any local URLs.
# * All posts are marked as 'draft' so you can revise them before publishing.
# * All tags are converted to lowercase to avoid conflicts. (Otherwise using
#   'Dog' and 'dog' as tags in different posts will raise an error from
#   Wordpress.)
#

# Configuration parameters

WP_SITE_URL = r'http://example.com'
WP_USERNAME = 'wordpress_username'
WP_PASSWORD = r'wordpress_password'


#

import os
import os.path
import re
from datetime import datetime

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo





##
## PELICAN side of things
##

FILE_PATH = r"""/Users/robertoz/Desktop/tmp/remains"""
VALID_YAML_TAGS = [
    'TITLE',
    'TITLE_LINK',
    'DATE',
    'SLUG',
    'CATEGORY',
    'TAGS',
    'STATUS',
    'LANG',
]


def get_files(fpath):
    """Get all files in dir specified by fpath"""
    # http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
    # This works if there is at least one file in the directory
    (_, _, filenames) = os.walk(fpath).next()

    for f in filenames:
        if f.startswith('.'):
            filenames.remove(f)
    return filenames


def get_meta_and_content_from_file(fpath):

    #
    # Had to use regex because YAML libraries don't recognize things as
    # title:  Link: Best posts of 2016
    #
    regex = r"(?P<tag>\w+):\s+(?P<value>.*)"
    p = re.compile(regex)

    r_meta = {}
    r_content = ''

    with open(os.path.join(FILE_PATH, fpath),'r') as infile:
        post = infile.read()

    post_lines = post.split('\n')

    # Get metadata
    for line in post_lines:
        # We are using whitelines as a delimiter between meta tags and
        # actual content. Yes, feeble, but enough for our purposes
        if len(line):
            r = p.findall(line)

            if len(r):
                k, v = r[0]
                k = k.upper()

                # filter valid tags
                # print "debug: k, v: %s: %s" % (k, v)

                # import ipdb; ipdb.set_trace()

                if k in VALID_YAML_TAGS:
                    if k == 'DATE':
                        v = v[:10]

                    r_meta[k] = v
            else:
                r_content = r_content + line + '\n'

    return {
            'meta': r_meta,
            'content': r_content,
        }


##
## WORDPRESS side of things
##

def to_wp_tags(p_tags):

    tags = [t.lower().strip() for t in  p_tags.split(',')]
    return tags

def log_into_wordpress(wp_site, wp_username, wp_password):

    wp = Client(os.path.join(wp_site, 'xmlrpc.php'),
        wp_username,
        wp_password
        )
    return wp


def inject_into_wordpress(wp, p_post):

    wp_post = WordPressPost()
    wp_post.title = p_post['meta']['TITLE']
    wp_post.post_status = 'draft'
    wp_post.date = datetime.strptime(p_post['meta']['DATE'], "%Y-%m-%d")

    terms_names = {}

    if p_post['meta'].has_key('TAGS'):
        terms_names['post_tag'] = to_wp_tags(p_post['meta']['TAGS'])

    if p_post['meta'].has_key('CATEGORY'):
        terms_names['category'] = p_post['meta']['CATEGORY'].strip()

    if p_post['meta'].has_key('SLUG'):
        wp_post.slug = p_post['meta']['SLUG'].strip()

    if len(terms_names):
        wp_post.terms_names = terms_names

    wp_post.content = p_post['content']

    wp.call(NewPost(wp_post))


if __name__=='__main__':

    # Open Wordpress connection
    wp_conn = log_into_wordpress(WP_SITE_URL, WP_USERNAME, WP_PASSWORD)

    # Get posts filenames
    fnames = get_files(FILE_PATH)


    for f in fnames:
        m = get_meta_and_content_from_file(f)

        inject_into_wordpress(wp_conn, m)

        print "Injected: '%s' with date %s" % (m['meta']['TITLE'], m['meta']['DATE'])
