#!/usr/bin/python
"""rss2email: get RSS feeds emailed to you
http://rss2email.infogami.com

Usage:
  run [--no-send]
  help (or --help, -h) (see this)
  opmlexport
  opmlimport filename
"""
__version__ = "2.68-xdg"
__author__ = "Lindsey Smith (lindsey@allthingsrss.com)"
__copyright__ = "(C) 2004 Aaron Swartz. GNU GPL 2 or 3."
___contributors__ = ["Dean Jackson", "Brian Lalor", "Joey Hess",
                     "Matej Cepl", "Martin 'Joey' Schulze",
                     "Marcel Ackermann (http://www.DreamFlasher.de)",
                     "Lindsey Smith (maintainer)", "Erik Hetzner", "Aaron Swartz (original author)",
                     "Dieter Plaetinck" ]

import urllib2
from os.path import join

urllib2.install_opener(urllib2.build_opener())

### Options which can be overridden in your config.py ###

# The email address messages are from by default:
DEFAULT_FROM = "bozo@dev.null.invalid"

# The default address to send messages to:
DEFAULT_TO = "bozo@dev.null.invalid"

# 1: Send text/html messages when possible.
# 0: Convert HTML to plain text.
HTML_MAIL = 0

# 1: Only use the DEFAULT_FROM address.
# 0: Use the email address specified by the feed, when possible.
FORCE_FROM = 0

# 1: Receive one email per post.
# 0: Receive an email every time a post changes.
TRUST_GUID = 1

# 1: Generate Date header based on item's date, when possible.
# 0: Generate Date header based on time sent.
DATE_HEADER = 0

# A tuple consisting of some combination of
# ('issued', 'created', 'modified', 'expired')
# expressing ordered list of preference in dates
# to use for the Date header of the email.
DATE_HEADER_ORDER = ('modified', 'issued', 'created')

# 1: Apply Q-P conversion (required for some MUAs).
# 0: Send message in 8-bits.
# http://cr.yp.to/smtp/8bitmime.html
#DEPRECATED
QP_REQUIRED = 0
#DEPRECATED

# 1: Show debug messages on CLI and logfile (when enabled).
# 0: Only show messages level info and higher.
DEBUG = 0

# 1: Log to $XDG_DATA_HOME/r2e/log
# 0: Don't log
LOG = 0

# 1: Use the publisher's email if you can't find the author's.
# 0: Just use the DEFAULT_FROM email instead.
USE_PUBLISHER_EMAIL = 0

# 1: Use SMTP_SERVER to send mail.
# 0: Call /usr/sbin/sendmail to send mail.
SMTP_SEND = 0

SMTP_SERVER = "smtp.yourisp.net:25"
AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
SMTP_USER = 'username'  # for SMTP AUTH, set SMTP username here
SMTP_PASS = 'password'  # for SMTP AUTH, set SMTP password here

# Set this to add a bonus header to all emails (start with '\n').
BONUS_HEADER = ''
# Example: BONUS_HEADER = '\nApproved: joe@bob.org'

# Set this to override From addresses. Keys are feed URLs, values are new titles.
OVERRIDE_FROM = {}

# Set this to override the timeout (in seconds) for feed server response
FEED_TIMEOUT = 60

# Optional CSS styling
USE_CSS_STYLING = 0
STYLE_SHEET='h1 {font: 18pt Georgia, "Times New Roman";} body {font: 12pt Arial;} a:link {font: 12pt Arial; font-weight: bold; color: #0000cc} blockquote {font-family: monospace; }  .header { background: #e0ecff; border-bottom: solid 4px #c3d9ff; padding: 5px; margin-top: 0px; color: red;} .header a { font-size: 20px; text-decoration: none; } .footer { background: #c3d9ff; border-top: solid 4px #c3d9ff; padding: 5px; margin-bottom: 0px; } #entry {border: solid 4px #c3d9ff; } #body { margin-left: 5px; margin-right: 5px; }'

# If you have an HTTP Proxy set this in the format 'http://your.proxy.here:8080/'
PROXY=""

# To most correctly encode emails with international characters, we iterate through the list below and use the first character set that works
# Eventually (and theoretically) ISO-8859-1 and UTF-8 are our catch-all failsafes
CHARSET_LIST='US-ASCII', 'BIG5', 'ISO-2022-JP', 'ISO-8859-1', 'UTF-8'

## html2text options ##

# Use Unicode characters instead of their ascii psuedo-replacements
UNICODE_SNOB = 0

# Put the links after each paragraph instead of at the end.
LINKS_EACH_PARAGRAPH = 0

# Wrap long lines at position. 0 for no wrapping.
BODY_WIDTH = 0



from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr

# Note: You can also override the send function.

def send(sender, recipient, subject, body, contenttype, extraheaders=None, smtpserver=None):
	"""Send an email.

	All arguments should be Unicode strings (plain ASCII works as well).

	Only the real name part of sender and recipient addresses may contain
	non-ASCII characters.

	The email will be properly MIME encoded and delivered though SMTP to
	localhost port 25.  This is easy to change if you want something different.

	The charset of the email will be the first one out of the list
	that can represent all the characters occurring in the email.
	"""

	# Header class is smart enough to try US-ASCII, then the charset we
	# provide, then fall back to UTF-8.
	header_charset = 'ISO-8859-1'

	# We must choose the body charset manually
	for body_charset in CHARSET_LIST:
	    try:
	        body.encode(body_charset)
	    except (UnicodeError, LookupError):
	        pass
	    else:
	        break

	# Split real name (which is optional) and email address parts
	sender_name, sender_addr = parseaddr(sender)
	recipient_name, recipient_addr = parseaddr(recipient)

	# We must always pass Unicode strings to Header, otherwise it will
	# use RFC 2047 encoding even on plain ASCII strings.
	sender_name = str(Header(unicode(sender_name), header_charset))
	recipient_name = str(Header(unicode(recipient_name), header_charset))

	# Make sure email addresses do not contain non-ASCII characters
	sender_addr = sender_addr.encode('ascii')
	recipient_addr = recipient_addr.encode('ascii')

	# Create the message ('plain' stands for Content-Type: text/plain)
	msg = MIMEText(body.encode(body_charset), contenttype, body_charset)
	msg['To'] = formataddr((recipient_name, recipient_addr))
	msg['Subject'] = Header(unicode(subject), header_charset)
	for hdr in extraheaders.keys():
		try:
			msg[hdr] = Header(unicode(extraheaders[hdr], header_charset))
		except:
			msg[hdr] = Header(extraheaders[hdr])

	fromhdr = formataddr((sender_name, sender_addr))
	msg['From'] = fromhdr

	msg_as_string = msg.as_string()
#DEPRECATED 	if QP_REQUIRED:
#DEPRECATED 		ins, outs = SIO(msg_as_string), SIO()
#DEPRECATED 		mimify.mimify(ins, outs)
#DEPRECATED 		msg_as_string = outs.getvalue()


	logging.info ('Sending: %s', unu(subject))

	if SMTP_SEND:
		if not smtpserver:
			import smtplib

			try:
				smtpserver = smtplib.SMTP(SMTP_SERVER)
			except KeyboardInterrupt:
				raise
			except Exception, e:
				logging.critical ('Could not connect to mail server "%s"', SMTP_SERVER)
				logging.critical ('Check your config.py file to confirm that SMTP_SERVER and other mail server settings are configured properly')
				if hasattr(e, 'reason'):
					logging.critical ("Reason: %s", e.reason)
				sys.exit(1)

			if AUTHREQUIRED:
				try:
					smtpserver.ehlo()
					smtpserver.starttls()
					smtpserver.ehlo()
					smtpserver.login(SMTP_USER, SMTP_PASS)
				except KeyboardInterrupt:
					raise
				except Exception, e:
					logging.critical ('Could not authenticate with mail server "%s" as user "%s"', SMTP_SERVER, SMTP_USER)
					logging.critical ('Check your config.py file to confirm that SMTP_SERVER and other mail server settings are configured properly')
					if hasattr(e, 'reason'):
						logging.critical ("Reason: %s", e.reason)
					sys.exit(1)

		smtpserver.sendmail(sender, recipient, msg_as_string)
		return smtpserver

	else:
		try:
			p = subprocess.Popen(["/usr/sbin/sendmail", recipient], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			p.communicate(msg_as_string)
			status = p.returncode
			assert status != None, "just a sanity check"
			if status != 0:
				logging.critical ('Sendmail exited with code %s', status)
				sys.exit(1)
		except:
			logging.critical( '''Error attempting to send email via sendmail. Possibly you need to configure your config.py to use a SMTP server? Please refer to the rss2email documentation or website (http://rss2email.infogami.com) for complete documentation of config.py. The options below may suffice for configuring email:
# 1: Use SMTP_SERVER to send mail.
# 0: Call /usr/sbin/sendmail to send mail.
SMTP_SEND = 0

SMTP_SERVER = "smtp.yourisp.net:25"
AUTHREQUIRED = 0 # if you need to use SMTP AUTH set to 1
SMTP_USER = 'username'  # for SMTP AUTH, set SMTP username here
SMTP_PASS = 'password'  # for SMTP AUTH, set SMTP password here
''')
			sys.exit(1)
		return None


### Set up locations
import os
def xdghome(key, default):
	'''Attempts to use the environ XDG_*_HOME paths if they exist otherwise
	   use $HOME and the default path.'''

	xdgkey = "XDG_%s_HOME" % key
	if xdgkey in os.environ.keys() and os.environ[xdgkey]:
		return os.environ[xdgkey]

	return join(os.environ['HOME'], default)

# Setup xdg paths.
CACHE_DIR = join(xdghome('CACHE', '.cache/'), 'r2e/')
DATA_DIR = join(xdghome('DATA', '.local/share/'), 'r2e/')
CONFIG_DIR = join(xdghome('CONFIG', '.config/'), 'r2e/')
FEEDS_CONFIG = join (CONFIG_DIR, 'feeds')
FEEDS_STATE = join (DATA_DIR, 'feeds_state')

# Ensure data paths exist.
for path in [CACHE_DIR, DATA_DIR, CONFIG_DIR]:
	try:
		if not os.path.exists(path):
			os.makedirs(path)
	except Exception, e:
		logging.critical ('Could not check/create directory "%s"', path)
		if hasattr(e, 'reason'):
			logging.critical ("Reason: %s", e.reason)
			sys.exit(1)


### Load the Options ###

# Read options from config file if present.
import sys
sys.path.insert(0,CONFIG_DIR)
try:
	from config import *
except:
	pass

if QP_REQUIRED:
	logging.warning ("QP_REQUIRED has been deprecated in rss2email.")

### Set up logging ###
# http://docs.python.org/library/logging.html#logging-to-multiple-destinations
import logging
LOG_FILENAME = DATA_DIR + 'log'

levels = [ logging.INFO, logging.DEBUG ]
# Couldn't find a proper way to disable logging to file but not to console, so .. :
filenames = [ '/dev/null', LOG_FILENAME ]
logging.basicConfig(level=levels[DEBUG],
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=filenames[LOG]
                    )
console = logging.StreamHandler()
console.setLevel(levels[DEBUG])
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info ('Rss2email started')


### Import Modules ###

import cPickle as pickle, time, traceback, sys, types, subprocess
hash = ()
try:
	import hashlib
	hash = hashlib.md5
except ImportError:
	import md5
	hash = md5.new

unix = 0
try:
	import fcntl
# A pox on SunOS file locking methods
	if (sys.platform.find('sunos') == -1):
		unix = 1
except:
	pass

import socket; socket_errors = []
for e in ['error', 'gaierror']:
	if hasattr(socket, e): socket_errors.append(getattr(socket, e))

#DEPRECATED import mimify
#DEPRECATED from StringIO import StringIO as SIO
#DEPRECATED mimify.CHARSET = 'utf-8'

import feedparser
feedparser.USER_AGENT = "rss2email/"+__version__+ " +http://www.allthingsrss.com/rss2email/"

import html2text as h2t

h2t.UNICODE_SNOB = UNICODE_SNOB
h2t.LINKS_EACH_PARAGRAPH = LINKS_EACH_PARAGRAPH
h2t.BODY_WIDTH = BODY_WIDTH
html2text = h2t.html2text

from types import *

### Utility Functions ###

import threading
class TimeoutError(Exception): pass

class InputError(Exception): pass

def timelimit(timeout, function):
#    def internal(function):
        def internal2(*args, **kw):
            """
            from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/473878
            """
            class Calculator(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()

            c = Calculator()
            c.setDaemon(True) # don't hold up exiting
            c.start()
            c.join(timeout)
            if c.isAlive():
                raise TimeoutError
            if c.error:
                raise c.error[0], c.error[1]
            return c.result
        return internal2
#    return internal


def isstr(f): return isinstance(f, type('')) or isinstance(f, type(u''))
def ishtml(t): return type(t) is type(())
def contains(a,b): return a.find(b) != -1
def unu(s): # I / freakin' hate / that unicode
	if type(s) is types.UnicodeType: return s.encode('utf-8')
	else: return s

### Parsing Utilities ###

def getContent(entry, HTMLOK=0):
	"""Select the best content from an entry, deHTMLizing if necessary.
	If raw HTML is best, an ('HTML', best) tuple is returned. """

	# How this works:
	#  * We have a bunch of potential contents.
	#  * We continue looking for our first choice.
	#    (HTML or text, depending on HTMLOK)
	#  * If that doesn't work, we continue looking for our second choice.
	#  * If that still doesn't work, we just take the first one.
	#
	# Possible future improvement:
	#  * Instead of just taking the first one
	#    pick the one in the "best" language.
	#  * HACK: hardcoded HTMLOK, should take a tuple of media types

	conts = entry.get('content', [])

	if entry.get('summary_detail', {}):
		conts += [entry.summary_detail]

	if conts:
		if HTMLOK:
			for c in conts:
				if contains(c.type, 'html'): return ('HTML', c.value)

		if not HTMLOK: # Only need to convert to text if HTML isn't OK
			for c in conts:
				if contains(c.type, 'html'):
					return html2text(c.value)

		for c in conts:
			if c.type == 'text/plain': return c.value

		return conts[0].value

	return ""

def getID(entry):
	"""Get best ID from an entry."""
	if TRUST_GUID:
		if 'id' in entry and entry.id:
			# Newer versions of feedparser could return a dictionary
			if type(entry.id) is DictType:
				return entry.id.values()[0]

			return entry.id

	content = getContent(entry)
	if content and content != "\n": return hash(unu(content)).hexdigest()
	if 'link' in entry: return entry.link
	if 'title' in entry: return hash(unu(entry.title)).hexdigest()

def getName(r, entry):
	"""Get the best name."""

	feed = r.feed
	if hasattr(r, "url") and r.url in OVERRIDE_FROM.keys():
		return OVERRIDE_FROM[r.url]

	name = feed.get('title', '')

	if 'name' in entry.get('author_detail', []): # normally {} but py2.1
		if entry.author_detail.name:
			if name: name += ": "
			det=entry.author_detail.name
			try:
			    name +=  entry.author_detail.name
			except UnicodeDecodeError:
			    name +=  unicode(entry.author_detail.name, 'utf-8')

	elif 'name' in feed.get('author_detail', []):
		if feed.author_detail.name:
			if name: name += ", "
			name += feed.author_detail.name

	return name

def getEmail(feed, entry):
	"""Get the best email_address."""

	if FORCE_FROM: return DEFAULT_FROM

	if 'email' in entry.get('author_detail', []):
		return entry.author_detail.email

	if 'email' in feed.get('author_detail', []):
		return feed.author_detail.email

	#TODO: contributors

	if USE_PUBLISHER_EMAIL:
		if 'email' in feed.get('publisher_detail', []):
			return feed.publisher_detail.email

		if feed.get("errorreportsto", ''):
			return feed.errorreportsto

	return DEFAULT_FROM

### Simple Database of Feeds ###

class Feed:
	def __init__(self, url, to):
		self.url, self.etag, self.modified, self.seen = url, None, None, {}
		self.to = to

def load():
	# First load all the urls as configured by user
	if not os.path.exists(FEEDS_CONFIG):
		logging.info ('Feedfile "%s" does not exist.  Nothing to do', FEEDS_CONFIG)
		sys.exit(0)
	try:
		feeds = {}
		with open(FEEDS_CONFIG) as file:
			for line in file:
				fields = line.strip().split()
				if not len(fields):
					continue
				url = fields[0]
				if url[0] == '#':
					logging.debug ("Skipping commented out: %s" % url[1:])
					continue
				settings = None
				to = None
				if (len(fields) > 1):
					to = fields[1]
				# yes, we store the url twice.  not the most efficient, but like this
				# you can do fast lookups and have a normal Feed object
				logging.debug ("loading: %s" % url)
				feeds[url] = Feed(url, to)
	except IOError, e:
		logging.critical ("Feedfile could not be opened: %s", e)
		sys.exit(1)

	# Then, add info about where we left off (seen entries), if available
	if os.path.exists(FEEDS_STATE):
		try:
			statefile = open(FEEDS_STATE, 'r')
		except IOError, e:
			logging.critical ( "Feed state file %s could not be opened: %s", FEEDS_STATE, e)
			sys.exit(1)

		# a dictionary with key url, value: a dict
		feeds_state = pickle.load(statefile)
		for url, seen in feeds_state.items():
			if url in feeds:
				feeds[url].seen = seen
	logging.debug ("Feeds:")
	logging.debug (feeds)
	return feeds

def save(feeds):
	'''Add/update all seen entries of all loaded feeds to the state file'''
	if os.path.exists(FEEDS_STATE):
		try:
			statefile = open(FEEDS_STATE, 'r')
		except IOError, e:
			logging.critical ( "Feed state file %s could not be opened: %s.  Cannot merge new info into old", FEEDS_STATE, e)
			sys.exit(1)
		feeds_state = pickle.load(statefile)
	else:
		feeds_state = {}
	try:
		for url, feed in feeds.items():
			feeds_state[url] = feed.seen
		pickle.dump(feeds_state, open(FEEDS_STATE, 'w'))

	except IOError, e:
		logging.error ( "Could not write to state file %s: %s", FEEDS_STATE, e)
		sys.exit(1)

#@timelimit(FEED_TIMEOUT)
def parse(url, etag, modified):
	if PROXY == '':
		return feedparser.parse(url, etag, modified)
	else:
		proxy = urllib2.ProxyHandler( {"http":PROXY} )
		return feedparser.parse(url, etag, modified, handlers = [proxy])


### Program Functions ###

def run():
	feeds = load()
	smtpserver = None
	try:
		default_to = DEFAULT_TO

		for url, f in feeds.items():
			try:
				logging.info ('Processing "%s"', f.url)
				r = {}
				try:
					r = timelimit(FEED_TIMEOUT, parse)(f.url, f.etag, f.modified)
				except TimeoutError:
					logging.warning ('Feed "%s" timed out', f.url)
					continue

				# Handle various status conditions, as required
				if 'status' in r:
					if r.status == 301: f.url = r['url']
					elif r.status == 410:
						logging.warning ("Feed %s gone", f.url)
						continue

				http_status = r.get('status', 200)
				logging.info ("Http status %s", http_status)
				http_headers = r.get('headers', {
				  'content-type': 'application/rss+xml',
				  'content-length':'1'})
				exc_type = r.get("bozo_exception", Exception()).__class__
				if http_status != 304 and not r.entries and not r.get('version', ''):
					if http_status not in [200, 302]:
						logging.warning ("Error %d %s", http_status, f.url)

					elif contains(http_headers.get('content-type', 'rss'), 'html'):
						logging.warning ("Looks like HTML %s", f.url)

					elif http_headers.get('content-length', '1') == '0':
						logging.warning ("Empty page %s", f.url)

					elif hasattr(socket, 'timeout') and exc_type == socket.timeout:
						logging.warning ("Timed out on %s", f.url)

					elif exc_type == IOError:
						logging.warning ('"%s" %s', r.bozo_exception, f.url)

					elif hasattr(feedparser, 'zlib') and exc_type == feedparser.zlib.error:
						logging.warning ("Broken compression %s", f.url)

					elif exc_type in socket_errors:
						exc_reason = r.bozo_exception.args[1]
						logging.warning ("%s %s", exc_reason, f.url)

					elif exc_type == urllib2.URLError:
						if r.bozo_exception.reason.__class__ in socket_errors:
							exc_reason = r.bozo_exception.reason.args[1]
						else:
							exc_reason = r.bozo_exception.reason
						logging.warning ("%s %s", exc_reason, f.url)

					elif exc_type == AttributeError:
						logging.warning ("%s %s", r.bozo_exception, f.url)

					elif exc_type == KeyboardInterrupt:
						raise r.bozo_exception

					elif r.bozo:
						logging.warning ('Error in "%s" feed (%s)', f.url, r.get("bozo_exception", "can't process"))

					else:
						logging.warning ("=== rss2email encountered a problem with this feed ===")
						logging.warning ("=== See the rss2email FAQ at http://www.allthingsrss.com/rss2email/ for assistance ===")
						logging.warning ("=== If this occurs repeatedly, send this to lindsey@allthingsrss.com ===")
						logging.warning (r.get("bozo_exception", "can't process") + ' "%s"', f.url)
						logging.warning ("rss2email %s", __version__)
						logging.warning ("feedparser %s", feedparser.__version__)
						logging.warning ("html2text %s", h2t.__version__)
						logging.warning ("Python %s", sys.version)
						logging.warning ("=== END HERE ===")
					continue

				r.entries.reverse()

				for entry in r.entries:
					id = getID(entry)

					# If TRUST_GUID isn't set, we get back hashes of the content.
					# Instead of letting these run wild, we put them in context
					# by associating them with the actual ID (if it exists).

					frameid = entry.get('id')
					if not(frameid): frameid = id
					if type(frameid) is DictType:
						frameid = frameid.values()[0]

					# If this item's ID is in our database
					# then it's already been sent
					# and we don't need to do anything more.

					if frameid in f.seen:
						if f.seen[frameid] == id: continue

					if not (f.to or default_to):
						logging.warning ("No default email address defined and none given for this feed." )
						logging.warning ("Ignoring feed %s", f.url)
						break

					if 'title_detail' in entry and entry.title_detail:
						title = entry.title_detail.value
						if contains(entry.title_detail.type, 'html'):
							title = html2text(title)
					else:
						title = getContent(entry)[:70]

					title = title.replace("\n", " ").strip()

					datetime = time.gmtime()

					if DATE_HEADER:
						for datetype in DATE_HEADER_ORDER:
							kind = datetype+"_parsed"
							if kind in entry and entry[kind]: datetime = entry[kind]

					link = entry.get('link', "")

					from_addr = getEmail(r.feed, entry)

					name = h2t.unescape(getName(r, entry))
					fromhdr = formataddr((name, from_addr,))
					tohdr = (f.to or default_to)
					subjecthdr = title
					datehdr = time.strftime("%a, %d %b %Y %H:%M:%S -0000", datetime)
					useragenthdr = "rss2email"
					extraheaders = {'Date': datehdr, 'User-Agent': useragenthdr, 'X-RSS-Feed': f.url, 'X-RSS-ID': id}
					if BONUS_HEADER != '':
						for hdr in BONUS_HEADER.strip().splitlines():
							pos = hdr.strip().find(':')
							if pos > 0:
								extraheaders[hdr[:pos]] = hdr[pos+1:].strip()
							else:
								logging.warning ("Malformed BONUS HEADER %s", BONUS_HEADER)

					entrycontent = getContent(entry, HTMLOK=HTML_MAIL)
					contenttype = 'plain'
					content = ''
					if USE_CSS_STYLING and HTML_MAIL:
						contenttype = 'html'
						content = "<html>\n"
						content += '<head><style><!--' + STYLE_SHEET + '//--></style></head>\n'
						content += '<body>\n'
						content += '<div id="entry">\n'
						content += '<h1'
						content += ' class="header"'
						content += '><a href="'+link+'">'+subjecthdr+'</a></h1>\n'
						if ishtml(entrycontent):
							body = entrycontent[1].strip()
						else:
							body = entrycontent.strip()
						if body != '':
							content += '<div id="body"><table><tr><td>\n' + body + '</td></tr></table></div>\n'
						content += '\n<p class="footer">URL: <a href="'+link+'">'+link+'</a>'
						if hasattr(entry,'enclosures'):
							for enclosure in entry.enclosures:
								if (hasattr(enclosure, 'url') and enclosure.url != ""):
									content += ('<br/>Enclosure: <a href="'+enclosure.url+'">'+enclosure.url+"</a>\n")
								if (hasattr(enclosure, 'src') and enclosure.src != ""):
									content += ('<br/>Enclosure: <a href="'+enclosure.src+'">'+enclosure.src+'</a><br/><img src="'+enclosure.src+'"\n')
						if 'links' in entry:
							for extralink in entry.links:
								if ('rel' in extralink) and extralink['rel'] == u'via':
									extraurl = extralink['href']
									extraurl = extraurl.replace('http://www.google.com/reader/public/atom/', 'http://www.google.com/reader/view/')
									content += '<br/>Via: <a href="'+extraurl+'">'+extralink['title']+'</a>\n'
						content += '</p></div>\n'
						content += "\n\n</body></html>"
					else:
						if ishtml(entrycontent):
							contenttype = 'html'
							content = "<html>\n"
							content = ("<html><body>\n\n" +
							           '<h1><a href="'+link+'">'+subjecthdr+'</a></h1>\n\n' +
							           entrycontent[1].strip() + # drop type tag (HACK: bad abstraction)
							           '<p>URL: <a href="'+link+'">'+link+'</a></p>' )

							if hasattr(entry,'enclosures'):
								for enclosure in entry.enclosures:
									if enclosure.url != "":
										content += ('Enclosure: <a href="'+enclosure.url+'">'+enclosure.url+"</a><br/>\n")
							if 'links' in entry:
								for extralink in entry.links:
									if ('rel' in extralink) and extralink['rel'] == u'via':
										content += 'Via: <a href="'+extralink['href']+'">'+extralink['title']+'</a><br/>\n'

							content += ("\n</body></html>")
						else:
							content = entrycontent.strip() + "\n\nURL: "+link
							if hasattr(entry,'enclosures'):
								for enclosure in entry.enclosures:
									if enclosure.url != "":
										content += ('\nEnclosure: ' + enclosure.url + "\n")
							if 'links' in entry:
								for extralink in entry.links:
									if ('rel' in extralink) and extralink['rel'] == u'via':
										content += '<a href="'+extralink['href']+'">Via: '+extralink['title']+'</a>\n'

					smtpserver = send(fromhdr, tohdr, subjecthdr, content, contenttype, extraheaders, smtpserver)

					f.seen[frameid] = id

				f.etag, f.modified = r.get('etag', None), r.get('modified', None)
			except (KeyboardInterrupt, SystemExit):
				raise
			except:
				logging.warning ("=== rss2email encountered a problem with this feed ===")
				logging.warning ("=== See the rss2email FAQ at http://www.allthingsrss.com/rss2email/ for assistance ===")
				logging.warning ("=== If this occurs repeatedly, send this to lindsey@allthingsrss.com ===")
				logging.warning ("Could not parse %s", f.url)
				logging.warning (traceback.extract_stack())
				logging.warning ("rss2email %s", __version__)
				logging.warning ("feedparser %s", feedparser.__version__)
				logging.warning ("html2text %s", h2t.__version__)
				logging.warning ("Python %s", sys.version)
				logging.warning ("=== END HERE ===")
				continue

	finally:
		save(feeds)
		if smtpserver:
			smtpserver.quit()

def opmlexport():
	import xml.sax.saxutils
	feeds = load()

	if feeds:
		print '<?xml version="1.0" encoding="UTF-8"?>\n<opml version="1.0">\n<head>\n<title>rss2email OPML export</title>\n</head>\n<body>'
		for url in feeds:
			url = xml.sax.saxutils.escape(url)
			print '<outline type="rss" text="%s" xmlUrl="%s"/>' % (url, url)
		print '</body>\n</opml>'

def opmlimport(importfile):
	importfileObject = None
	print 'Importing feeds from', importfile
	if not os.path.exists(importfile):
		logging.warning ('OPML import file "%s" does not exist.' % importfile)
	try:
		importfileObject = open(importfile, 'r')
	except IOError, e:
		logging.critical ("OPML import file could not be opened: %s", e)
		sys.exit(1)
	try:
		import xml.dom.minidom
		dom = xml.dom.minidom.parse(importfileObject)
		newfeeds = dom.getElementsByTagName('outline')
	except:
		logging.critical ('Unable to parse OPML file')
		sys.exit(1)

	import xml.sax.saxutils

	for f in newfeeds:
		if f.hasAttribute('xmlUrl'):
			feedurl = f.getAttribute('xmlUrl')
			print feedurl

if __name__ == '__main__':
	args = sys.argv
	try:
		if len(args) < 2: raise InputError, "insufficient args"
		action, args = args[1], args[2:]

		if action == "run":
			if args and args[0] == "--no-send":
				def send(sender, recipient, subject, body, contenttype, extraheaders=None, smtpserver=None):
					logging.info ('Not sending: %s', unu(subject))

			run()

		elif action in ("help", "--help", "-h"): print __doc__

		elif action == "opmlexport": opmlexport()

		elif action == "opmlimport":
			if not args:
				raise InputError, "OPML import '%s' requires a filename argument" % action
			opmlimport(args[0])

		else:
			raise InputError, "Invalid action"

	except InputError, e:
		logging.error (e)
		logging.error (__doc__)

