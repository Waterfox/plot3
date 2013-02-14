import re, random, string, hashlib, hmac

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
    strsplit = string.split(h,'|')
    hash = strsplit[0]
    salt = strsplit[1]  
    hash2 = hashlib.sha256(name + pw + salt).hexdigest()
    return hash2 == hash
 
secret = 'RobbieSecret'
 
def make_secure_val(s):
    return "%s|%s" %(s, hmac.new(secret,s).hexdigest() )
	
def check_secure_val(h):
    newstr = string.split(h,'|')
    if make_secure_val(newstr[0]) == h:
        return newstr[0]
   
def validate_name(input_name):
	USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	return USER_RE.match(input_name)
	
def validate_pass(input_pass):
	PASS_RE = re.compile(r"^.{3,20}$")
	return PASS_RE.match(input_pass)
	
def	validate_match(input_pass,input_pass2):
	return (input_pass == input_pass2)

def validate_email(input_em):
	if (input_em ==''):
		return True
	else:
		EM_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
		return EM_RE.match(input_em)

def validate_cats(cats):
	CATS_RE = re.compile("(\d+)(,\s*\d+)*")
	if (cats != ''):
		return True
	#return CATS_RE.match(cats)

def validate_title(title):
	TITLE_RE = re.compile(r"^.{3,32}$")
	return TITLE_RE.match(title)