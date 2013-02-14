# +++++++++++++++++++++++++++++++++++++++++++WFDN+++++++++++++++++++++++++++++++++++
import webapp2
import jinja2, os, logging, cgi ,json, random, time
from google.appengine.ext import db
from google.appengine.api import memcache, mail
from webfunctions import validate_name, validate_pass, validate_match, validate_email, make_salt, make_pw_hash, valid_pw, make_secure_val, check_secure_val, validate_cats, validate_title
from colors import *
jinja_environment = jinja2.Environment(autoescape=False,loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))


B = """
<input type="button" class="button"  value="Bar Plot" onmouseup="window.location = '%(id)s?ptype=bar'" >
"""
BP = """
<input type="button" class="button"  value="Bar Plot" onmouseup="window.location = '%(id)s?ptype=bar'" >
<input type="button" class="button"  value="Pie Plot" onmouseup="window.location = '%(id)s?ptype=pie'" >
"""
LASB = """
<input type="button" class="button"  value="Line Plot" onmouseup="window.location = '%(id)s?ptype=line'" >
<input type="button" class="button"  value="Area Plot" onmouseup="window.location = '%(id)s?ptype=area'" >
<input type="button" class="button"  value="Scatter Plot" onmouseup="window.location = '%(id)s?ptype=scatter'" >
<input type="button" class="button"  value="Bar Plot" onmouseup="window.location = '%(id)s?ptype=bar'" >
"""

FOOTER = """
<footer>
	Powererd by  <a href="https://github.com/mbostock/d3/wiki">D3</a> and <a href="http://nvd3.com/">NVD3</a>.
</footer>
"""

g_data =([{"key": "set1", "values": [[1.0, 100], [2.0, 200], [3.0, 400]]},
		{"key": "set2", "values": [[1.0, 110], [2.0, 310], [3.0, 150]]},
		{"key": "set3", "values": [[1.0, 220], [2.0, 140], [3.0, 320]]},
		{"key": "set4", "values": [[1.0, 330], [2.0, 130], [3.0, 270]]}])

#colorDict ={'Rset1': ["#FFF200", "#7065AD", "#EE2971", "#51B848"],'Rset2':["#297fff", "#7137f8", "#00d400", "#ff7f2a", "#ff0000","#808080", "#000000", "#ffcc00", "#37c8ab", "#ff2ad4"],'CBset3':["#A7CEE2","#2078B4", "#B4D88B", "#34A048", "#F69999", "#E21F26","#FDBF6E", "#F57E20"],'d3set10':["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd","#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],'d3set20' : ["#1f77b4", "#aec7e8","#ff7f0e", "#ffbb78","#2ca02c", "#98df8a","#d62728", "#ff9896","#9467bd", "#c5b0d5","#8c564b", "#c49c94","#e377c2", "#f7b6d2","#7f7f7f", "#c7c7c7","#bcbd22", "#dbdb8d","#17becf", "#9edae5"],'d3set20b':["#393b79", "#5254a3", "#6b6ecf", "#9c9ede","#637939", "#8ca252", "#b5cf6b", "#cedb9c","#8c6d31", "#bd9e39", "#e7ba52", "#e7cb94","#843c39", "#ad494a", "#d6616b", "#e7969c","#7b4173", "#a55194", "#ce6dbd", "#de9ed6"],'d3set20c':["#3182bd", "#6baed6", "#9ecae1", "#c6dbef","#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2","#31a354", "#74c476", "#a1d99b", "#c7e9c0","#756bb1", "#9e9ac8", "#bcbddc", "#dadaeb","#636363", "#969696", "#bdbdbd", "#d9d9d9"],'Rset3':["#ff6600", "#2a7fff", "#6f7c91", "#37c871","#00ffff", "#ffff00", "#ff7f2a", "#ff2a2a","#5f5fd3", "#8a6f91", "#37c871", "#8d5fd3","#87aade", "#d3bc5f", "#918a6f", "#d35f5f","#8dd35f", "#ff80b2", "#93aca7", "#37c871"]}
# cSet = 'Rset2'
# axisdict = {'0d':'d3.format(\',r\')','1d':'d3.format(\',.1f\')','2d':'d3.format(\',.2f\')','3d':'d3.format(\',.3f\')','strf':'function(d) { return d3.time.format(\'%x\')(new Date(d))}'}

def modJson(inData,tFormat=None):	# change the strings into numbers
	plotData = json.loads(inData)
	shapes = ['circle', 'cross', 'triangle-up', 'triangle-down', 'diamond', 'square']
	for i in xrange(len(plotData)): #iter set (columns)
		plotData[i]['shape'] = shapes[i % 6] 
		for j in xrange(len(plotData[i]['values'])): #iter rows
			if tFormat:
				 
				try:
					tss =time.strptime(plotData[i]['values'][j][0],tFormat)
					ts2 =time.mktime(tss)*1000
					plotData[i]['values'][j][0] = ts2
					#current limitation: Must include a year > 1970
				except:
					plotData[i]['values'][j] = plotData[i]['values'][j]
			try:
				plotData[i]['values'][j][1] = float(plotData[i]['values'][j][1])
			except:
				plotData[i]['values'][j] = plotData[i]['values'][j]
	plotData = json.dumps(plotData)
	return plotData

	
def tab2json(plotdata,title):
    #Simple, accomodates direct paste from excel. No 1E-7 input.
    pd = plotdata.split('\r\n') #split on each line

    Y2=[]
    title = []
    ly = len(pd[0].split('\t'))-1 #number of Y columns
    splon = '\t'
    if ly == 0:
        ly = len(pd[0].split(','))-1
        splon = ','
    
    for ind in xrange(ly): #for Y col each line
        X=[]
        Y=[]	
        I = pd[0].split(splon)
        title.append(I[ind+1])
        for i in pd[1:len(pd)]: #for each row
            if i != '':
                I = i.split(splon)
                try:
                    X.append(float(I[0]))
                except:
                    X.append(I[0])
                try:
                    Y.append(float(I[ind+1]))
                except:
                    Y.append(0.0)
        Y2.append(Y)
    J2=''
    for ind in xrange(ly):	
        z=[]
        for i in xrange(len(X)):
            z.append([X[i],Y2[ind][i]])
            
        j ={'key':title[ind],'values':z }	
        J = json.dumps(j,sort_keys=True, indent=4)
        J2+=J+','
	size = str(len(X)*ly)
    return '['+J2[:-1]+']',size
	
def add_to_link(index,keyword,link):
	for entry in index:
		if entry[0] == keyword:
			if link in entry[1]:
				entry[2] = entry[2]+1
			else:
				entry[1].append(link)
			return
	value = 1
	index.append([keyword,[link],value])
	
def add_to_name(index,keyword,ID):
	for entry in index:
		if entry[0] == keyword:
			#entry[1].append(ID)
			entry[1]=ID
			return

	index.append([keyword,ID])
		
def SankeyNodesLinks(dbTC):
	catlink=[]
	catname=[]
		#Put all the titles into the nodes	
	for SET in dbTC:
		catbox = SET.CATS.split(',')
		for i in xrange(len(catbox)):
			if i+1 < len(catbox): #take the next subcatergory if there is one
				linked = catbox[i+1]
			else:	#else the final node is the 
				linked = SET.TITLE
			name = catbox[i].lower()	
			add_to_link(catlink,name,linked.lower())
			add_to_name(catname,name,'')#SET.key().id())
		name = SET.TITLE.lower()
		add_to_name(catname,name,SET.key().id())

	#next part	
	name = []
	[name.append({'name':cat[0].lower(),'id':cat[1]}) for cat in catname]
	links = []
	values = []
	for cat in catlink:
		for linked in cat[1]:
			for i in xrange(len(catname)):
				if catname[i][0] == cat[0]:
					src = i
				if catname[i][0] == linked:
					trg = i

			intoLink = {'source':src,'target':trg,'value':cat[2]}
			links.append(intoLink )
			
	j = {'nodes':name,'links':links}
	J=json.dumps(j)
	return J
	
def add_to_nodes(index,name,children):
	for item in index:
		if name in item:
			return
	index.append([name,children])
	return
	

class Plot3Handler(webapp2.RequestHandler):
	def render_str(self, template, **params):
		t=jinja_environment.get_template(template)
		return t.render(params)	

	def render(self, template, **kw):
		self.response.out.write(self.render_str(template,**kw))		
		
	def checkCookies(self):
		UNH = self.request.cookies.get('UNH','0')
		UNA = self.request.cookies.get('UNA','0')
		
		if check_secure_val(UNH):
			id = UNH.split('|')[0]
			q = UNPW.get_by_id(int(id))
			UN = q.UN
			loggedIn = True
		else:
			loggedIn = False
			UN = '0'
			
		admin = False
		if check_secure_val(UNA): admin = True	
		else: admin = False
		
		return loggedIn,admin,UN
		
	def getState(self):
		return 'Kingston'.lower()
		
	def getUserColour(self,UN='0'):
		cSetMainSec = self.request.cookies.get('cSetMain','0')
		if check_secure_val(cSetMainSec): cSetMain = cSetMainSec.split('|')[0]	
		else: cSetMain = '0'
		
		if cSetMain=='0' and UN != '0':
			dBUN = db.GqlQuery("SELECT * FROM UNPW WHERE UN=:USER",USER=UN).get()
			if dBUN:
				cSetMain = dBUN.CSET
			else:
				cSetMain = 'd3set20'
		elif cSetMain=='0':
			cSetMain = 'd3set20'
		return cSetMain
		
	def getPlotColour(self,dS=None):
		if dS: cSet=dS.CSET	#get the plot colour
		else:	#if its not in the db check cookies
			cSetSec = self.request.cookies.get('cSet','0')
			if check_secure_val(cSetSec): cSet = cSetSec.split('|')[0]	
			else: cSet = '0'
			if cSet=='0':	#if its not in the cookies, set default
				cSet = 'd3set20'
		return cSet
		
	def getPlotColourGlobe(self,dS):
		#chose the users prefered value, else the plots default value, else the default
		cSetSec = self.request.cookies.get('cSet','0')
		if check_secure_val(cSetSec): cSet = cSetSec.split('|')[0]	
		else: cSet = '0'
		if cSet=='0':
			if dS: cSet=dS.CSET
			else: cSet='d3set20'
		return cSet
		
	def add_to_dash(self,index,id,ptype=None,top='auto',left='auto',w='300px',h='300px'):
		for item in index:
			if item[0] == id:
				if top:item[1] = top
				if left: item[2] = left
				if w: item[3] = w
				if h: item[4] = h
				if ptype: item[5] = ptype
				return
		newItem = [id,'auto','auto','300px','300px',ptype]
		index.append(newItem)
		return
		
	def remove_from_dash(self,index,id):
		for i in xrange(len(index)):
			if (str(index[i][0]) == str(id)):
				del index[i]
				return index
				
		
	def checkDataFormat(self,dS,entry_id,GlobeRandom=''):
		firstEl = json.loads(dS.PLOTDATA)[0]['values'][0][0]
		#First Element a string?
		if isinstance(firstEl,str) or isinstance(firstEl,unicode) and (len(json.loads(dS.PLOTDATA))==1):
			buttonSet = BP %{"id":GlobeRandom+str(entry_id)}
			noXlabels = True	#dont use xlabels, we already have them
			ptype = 'bar'
		#Is there more than one Y col?
		elif (isinstance(firstEl,str) or isinstance(firstEl,unicode)):
			buttonSet = B %{"id":GlobeRandom+str(entry_id)}
			noXlabels = True
			ptype = 'bar'
		#Numbers it is
		else:
			buttonSet = LASB %{"id":GlobeRandom+str(entry_id)}
			noXlabels = False
			ptype = 'line'
		return ptype,buttonSet,noXlabels
		
	def secureCookie(self,cName,cVal):
		secVal = make_secure_val(cVal)
		self.response.headers.add_header('Set-Cookie', cName+'=%s' %str(secVal))
		
		
class PERSONAL3DB(db.Model,Plot3Handler):
	UN = db.StringProperty(required = True)
	TS = db.DateTimeProperty(auto_now_add = True)
	CATS = db.StringProperty(required = True)
	PLOTDATA = db.TextProperty(required = True)
	TITLE = db.StringProperty(required = True)
	DESC = db.TextProperty()	#description
	XL = db.StringProperty()	#y-axis Label
	YL = db.StringProperty()	#x-axis Label
	SZ = db.StringProperty()	#number of datapoints in the set
	XF = db.StringProperty()	#x-axis format
	YF = db.StringProperty()	#y-axis format
	CSET = db.StringProperty()	#color format
	
class RANDOM3DB(db.Model,Plot3Handler):
	TS = db.DateTimeProperty(auto_now_add = True)
	PLOTDATA = db.TextProperty(required = True)
	TITLE = db.StringProperty()
	DESC = db.TextProperty()	#description
	XL = db.StringProperty()	#y-axis Label
	YL = db.StringProperty()	#x-axis Label
	SZ = db.StringProperty()	#number of datapoints in the set
	XF = db.StringProperty()	#x-axis format
	YF = db.StringProperty()	#y-axis format
	CSET = db.StringProperty()	#color format
	
	
class UNPW(db.Model):
	UN = db.StringProperty(required = True)
	PW = db.StringProperty(required = True)
	EM = db.StringProperty()		#email
	TS = db.DateTimeProperty(auto_now_add = True)	#time
	CSET = db.StringProperty()		#default colour set
	STATUS = db.StringProperty()	#admin
	DASH = db.StringProperty()		#dashboard info json[[id,x,y,rx,ry],[..]]
	
class COMMENTS(db.Model):
	UN = db.StringProperty()
	COMM = db.TextProperty(required = True)
	TS = db.DateTimeProperty(auto_now_add=True)
	EM = db.StringProperty()
	
# *******************************************SANKEY DIAGRAMS**********************************************************************		
	
class MainHandler(Plot3Handler):
    def get(self):
	
		Feature = self.getState()
		#Get and check the cookie, find the UN
		[loggedIn,admin,UN] = self.checkCookies()
		
		vtype = self.request.get("vtype")
		dbtype = self.request.get("dbtype")
		
		#Check if the user is logged in, set flags
		UNstr=''
		if loggedIn is not True:
			#UNstr = UN+'\'s Database' 
			self.redirect('/landing')
			return
		
		dbTC = memcache.get('dbTC'+UN)
		if dbTC is None:	#in memcache?
			dbTC = db.GqlQuery("SELECT TITLE,CATS FROM PERSONAL3DB WHERE UN = :USER ORDER BY TS DESC",USER=UN).fetch(40)
			#logging.error("DB QUERY")
			if dbTC: memcache.set('dbTC'+UN,dbTC) #in DB?
			else: self.redirect('/addNew')	
			

		cSetMain = self.getUserColour(UN)
		
		JSankey = SankeyNodesLinks(dbTC)
		
		global lastID
		global lastptype
		lastID=None
		lastptype=None
		
		
		if not vtype:
			vtype = 'sankey'
		if vtype == 'sankey':
			self.render('main_Sankey.html',dataset=JSankey,UN=UN,loggedIn=loggedIn,colorset=colorDict[cSetMain])

		# else:
			# self.response.out.write(JTree)
			# self.render('main_Tree.html',dataset=JTree)
			


# *******************************************ADD-DATA**********************************************************************	
	 
class AddDataHandler(Plot3Handler):
	def get(self):
		#Get and check the cookie, find the UN
		[loggedIn,admin,UN] = self.checkCookies()
		if loggedIn:
			self.render('add_data_form.html',loggedIn=loggedIn,UN=UN)
		else:
			self.redirect('logout')
			return
		
	def post(self):
		[loggedIn,admin,UN] = self.checkCookies()
			
		cats = self.request.get('cats')
		cats = cgi.escape(cats)
		title = self.request.get('title')
		title = cgi.escape(title)
		description = self.request.get('description')
		description = cgi.escape(description)
		xlabel = self.request.get('xlabel')
		xlabel = cgi.escape(xlabel)
		ylabel = self.request.get('ylabel')
		ylabel = cgi.escape(ylabel)

		#self.response.out.write(json.loads(plotData)[1]['values'])
		#plotdata = cgi.escape(plotdata)
		#plotdata_js,size = tab2json(plotdata,title)
		#print validate_cats(cats)
		#print validate_title(title)
		#return
	
		xf = self.request.get('XF')		
		yf = self.request.get('YF')

		if xf=='strf':tFormat = self.request.get('tFormat')
		else: tFormat = None

		plotData = self.request.get('plotData')
		plotData = modJson(plotData,tFormat)

		cSet = self.getPlotColour() #set the user's default colour when adding data
		if cSet=='0':
			cSet='d3set20'

		if not validate_cats(cats):
			w2 = 'Category string must be included and be CSV </br>'
			self.render('add_data_form.html',loggedIn=loggedIn,warn2=w2,data=plotData)
			return
		if not validate_title(title):
			w1 = 'Title must be included and be between 3 and 32 characters </br>'
			self.render('add_data_form.html',loggedIn=loggedIn,warn1=w1,data=plotData)
			return

		#check there isn't an identical entry *This works for Title only
		# TITLEcheck = db.GqlQuery("SELECT * FROM PERSONAL3DB WHERE TITLE = :titlecheck", titlecheck = title).fetch(100)
		# if TITLEcheck:
		# 		w1="There is already an entry with this title or  in your database"
		# 		self.render('add_data_form.html',loggedIn=loggedIn,UN=UN,warn1=w1,data=plotData)
		# 		return

		#check there isn't an identical entry *This works for Title and Cats
		dbTC = memcache.get('dbTC'+UN)
		if dbTC is None:	#in memcache?
			dbTC = db.GqlQuery("SELECT TITLE,CATS FROM PERSONAL3DB WHERE UN = :USER ORDER BY TS DESC",USER=UN).fetch(50)
			#logging.error("DB QUERY")
			if dbTC: memcache.set('dbTC'+UN,dbTC) #in DB?
		if dbTC:
			for SET in dbTC:
				if title.lower() in SET.TITLE.lower() or title.lower() in [CAT.lower() for CAT in SET.CATS.split(',')]:	
			 		w1="There is already an entry with this title or catergory in your database"
			 		self.render('add_data_form.html',loggedIn=loggedIn,UN=UN,warn1=w1,data=plotData)
					return

		#for match in TITLEcheck:
		#	if match.CATS==cats:
		#		w1="There is already an identical entry in your database"
		#		self.render('add_data_form.html',loggedIn=loggedIn,warn1=w1,data=plotData)
		#		return

		entry = PERSONAL3DB(UN=UN,CATS=cats,PLOTDATA=plotData,TITLE=title,DESC=description,XL=xlabel,YL=ylabel,CSET=cSet,XF=xf,YF=yf)
		entry.put()
		entry_id=str(entry.key().id())
		memcache.set(entry_id,entry) #put in memcache
		memcache.delete('dbTC'+UN)
		ptype,buttonSet,noXlabels = self.checkDataFormat(entry,entry_id)
		#self.redirect('/%s?ptype=%s' %(entry_id,ptype))
		

# *******************************************PLOTS**********************************************************************		
class PlotSet(Plot3Handler):
		
	def get(self,entry_id):
		[loggedIn,admin,UN] = self.checkCookies()	
		if loggedIn == False:
			self.redirect('/login')
		
		dS = memcache.get(str(entry_id))
		if dS is None:
			dS=PERSONAL3DB.get_by_id(int(entry_id))
			logging.error("DB QUERY")
			if dS: memcache.set(str(entry_id),dS)
			else:
				self.response.out.write('There\'s nothing here Bob!')
				return
		ptype = self.request.get("ptype")
		logging.error("DB QUERY!")
		
		cSet = self.getPlotColour(dS)
		if not cSet: cSet = self.getUserColour(UN)
		
		if dS.UN != UN:
			self.response.out.write('This is not your data!')
		
		ptype2,buttonSet,noXlabels = self.checkDataFormat(dS,entry_id)
		if not ptype: ptype=ptype2
		
		
		if not dS.XF:	#set the axis if there is no default
			dS.XF = '1d'
		if not dS.YF:
			dS.YF = '1d'
		
		self.render('PlotSet.html',ptype=ptype,plotData=dS.PLOTDATA,UN=dS.UN,cats=dS.CATS,title=dS.TITLE,description=dS.DESC,xlabel=dS.XL,ylabel=dS.YL,size=dS.SZ,id=int(entry_id),buttonSet=buttonSet,colorset=colorDict[cSet],XF=axisdict[dS.XF],YF=axisdict[dS.YF],xflag=noXlabels,loggedIn=loggedIn)

			

class DeleteSet(Plot3Handler):
	def get(self):
		[loggedIn,admin,UN] = self.checkCookies()	
		if loggedIn==True:
			entry_id = self.request.get("id")
			dS=PERSONAL3DB.get_by_id(int(entry_id))
			if dS:
				if dS.UN==UN:
					dS.delete()
					key = str(entry_id)
					memcache.delete(key)
					memcache.delete('dbTC'+UN)
					UNdb = db.GqlQuery("SELECT * FROM UNPW WHERE UN=:USER",USER=UN).get()
					dashlist = json.loads(UNdb.DASH)	#get user's the dash list
					dashlist = self.remove_from_dash(dashlist,entry_id) #remove that ID to it with default properties
					UNdb.DASH = json.dumps(dashlist)
					UNdb.put()
					self.redirect('/')
				else: self.response.out.write('Thats not your set to delete carl')
			else: self.response.out.write('Nothing Here to Delete..')
		else: self.redirect('\login')
			
			
# -----------------------------------SETTINGS---------------------------------------------------------------------------------------------				
class MainSettingHandler(Plot3Handler):
	def get(self):
		[loggedIn,admin,UN] = self.checkCookies()
		if loggedIn: self.render('settings_main.html')
		else: self.redirect('/logout')
		

	def post(self):
		#get the color set, add it to cookie, if USER, set to user default in UNPW DB
		[loggedIn,admin,UN] = self.checkCookies()
		cSetMain = self.request.get('cSet')
		if cSetMain is '': cSetMain = self.getUserColour(UN)
		
		self.secureCookie('cSetMain',cSetMain)
		#self.response.headers.add_header('Set-Cookie', 'cSetMain=%s' %str(cSetMain))
		
		[loggedIn,admin,UN] = self.checkCookies()	
		if loggedIn == True:
			dBUN= db.GqlQuery("SELECT * FROM UNPW WHERE UN=:USER",USER=UN).get()
			dBUN.CSET = cSetMain
			dBUN.put()

		self.redirect('/')
		

		
class PlotSettingHandler(Plot3Handler):
	def get(self):
		[loggedIn,admin,UN] = self.checkCookies()
		if loggedIn: self.render('settings.html',admin=loggedIn,UN=UN)
		else: self.response.out.write('You are not an logged in')

	def post(self):
		#get the color set, add it to the PLOT's entry in the database
		cSet = self.request.get('cSet')
		xf = self.request.get('XF')
		yf = self.request.get('YF')
		entry_id = self.request.get("id")
		[loggedIn,admin,UN] = self.checkCookies()	
		
		#self.response.headers.add_header('Set-Cookie', 'cSet=%s' %str(cSet))
		self.secureCookie('cSet',cSet)
		
		if loggedIn == True: 
			key = str(entry_id)
			dS = memcache.get(key)
			if dS is None:
				dS=PERSONAL3DB.get_by_id(int(entry_id))
				logging.error("DB QUERY")
			if dS and dS.UN==UN:	#only save if the post ID is the user's
				if cSet: dS.CSET = cSet
				if xf: dS.XF=xf
				if yf: dS.YF=yf
				dS.put()
				memcache.set(key,dS)
			else: self.response.out.write('nice try')
		self.redirect('/'+entry_id)
		

# -----------------------------------USER LOGIN---------------------------------------------------------------------------------------------	
		
class Login(Plot3Handler):
	def write_login(self,input_name="",w1="",wp2=""):
		# self.response.out.write(signin %{"Uname":input_name,"w1":w1,"w2":wp2,})
		self.render('login.html',Uname = input_name,w1=w1,w2=wp2)
		
	def get(self):
		self.write_login()

	def post(self):
		input_name = self.request.get('username')
		input_name = cgi.escape(input_name)
		validname = validate_name(input_name)
		
		input_pass = self.request.get('password')
		input_pass = cgi.escape(input_pass)
		validpass = validate_pass(input_pass)
		
		if validname and validpass:
			q = db.GqlQuery("SELECT * FROM UNPW WHERE UN = :1",input_name).get()
			if not q:
				w1 = 'Username doesnt exist'
				self.write_login(input_name,w1)
			else:
				if q.UN and valid_pw(input_name, input_pass, q.PW):
					pn=str(q.key().id())
					self.secureCookie('UNH',pn)
					#pnsec = make_secure_val(pn)
					#self.response.headers.add_header('Set-Cookie', 'UNH=%s' %pnsec)
					if q.STATUS=='admin':
						self.secureCookie('UNA','admin')
						#admsec = make_secure_val('admin')
						#self.response.headers.add_header('Set-Cookie', 'UNA=%s'%admsec)
					self.redirect('/')
				else:
					wp2 = 'Not a valid password'
					self.write_login(input_name,'',wp2)
				
					
		elif not validname:
			w1 = 'Not a valid username'
			self.write_login('',w1)
		else:		
			wp2 = 'Not a valid password'
			self.write_login(input_name,'',wp2)
			
class Logout(Plot3Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'UNH=;Path=/')
		self.response.headers.add_header('Set-Cookie', 'UNA=;Path=/')
		cSet = 'Rset3'
		self.render('Plot3Logo.html',colorset=colorDict[cSet])
	
class Signup(Plot3Handler):
    def write_form(self,input_name="",input_em="",warn1="",p2="",p3="",e4=""):
		self.render('signup.html',Uname = input_name,Uem = input_em,w1=warn1,w2=p2,w3=p3,w4=e4)
		
    def get(self):
		self.write_form()

    def post(self):
		input_name = self.request.get('username')
		input_name = cgi.escape(input_name)
		validname = validate_name(input_name)

		input_pass = self.request.get('password')
		input_pass2 = self.request.get('verify')
		input_pass = cgi.escape(input_pass)
		input_pass2 = cgi.escape(input_pass2)
		validpass = validate_pass(input_pass)
		validmatch = validate_match(input_pass,input_pass2)

		input_em = self.request.get('email')
		input_em = cgi.escape(input_em)
		validem = validate_email(input_em)

		UNchek = db.GqlQuery("SELECT * FROM UNPW WHERE UN = :user", user = input_name)
		
		if  UNchek.get():
			warn1 = "Username is taken"
			self.write_form(input_name,input_em,warn1)
		elif not validem:
			warn4 = "Not a Valid Email"
			self.write_form(input_name,input_em,'','','',warn4)
		elif (not validname):
			warn1 = "Not a Valid Username"
			self.write_form(input_name,input_em,warn1)
		elif validname and (not validpass):
			warn2 = "Not a Valid Password"
			self.write_form(input_name,input_em,'',warn2)
			#self.response.out.write("No good bro")
		elif validname and (not validmatch):
			warn3 = "Passwords do not match"
			self.write_form(input_name,input_em,'','',warn3)
		elif (validname and validpass and validmatch):
			PWH = make_pw_hash(input_name, input_pass)
			dashInit=json.dumps([['save','0px','0px']])
			newu = UNPW(UN=input_name,PW=PWH,EM=input_em,CSET='d3set10',STATUS='',DASH=dashInit)
			newu.put()
			pn=str(newu.key().id())
			self.secureCookie('UNH',pn)
			#pnsec = make_secure_val(pn)
			#self.response.headers.add_header('Set-Cookie', 'UNH=%s' %pnsec)
			self.redirect('/')
			
# -----------------------------------DASHBOARD---------------------------------------------------------------------------------------------		
	
class addDash(Plot3Handler):
	def get(self):
		[loggedIn,admin,UN] = self.checkCookies() # check cookies / memcached
		if loggedIn:
			UNdb = db.GqlQuery("SELECT * FROM UNPW WHERE UN=:USER",USER=UN).get()
		else:
			self.render('NoUser.html')
			return
			
		entry_id  = int(self.request.get('id'))	#take the plot ID
		ptype  = self.request.get('ptype')	#take the plot ID
		if not ptype:
			key = str(entry_id)
			dS = memcache.get(key)
			if dS is None:
				dS=PERSONAL3DB.get_by_id(int(entry_id))
				logging.error("DB QUERY")
				memcache.set(key,dS)
				if dS is None: ptype = bar
			ptype,buttonSet,noXlabel = self.checkDataFormat(dS,entry_id)			
		templist = json.loads(UNdb.DASH)	#get the dash list
		self.add_to_dash(templist,entry_id,ptype) #add that ID to it with default properties
		UNdb.DASH = json.dumps(templist)
		UNdb.put()
		self.redirect('dash')
		
class dashObj(Plot3Handler):
	def dashPrint(self):
		entry_id = self.id
		ptype = self.ptype
		randColor = self.color

		key = str(entry_id)
		dS = memcache.get(key)
		if dS is None:
			dS=PERSONAL3DB.get_by_id(int(entry_id))
			logging.error("DB QUERY")
			if dS: memcache.set(key,dS)
			else:
				self.response.out.write('There\'s nothing here Bob!')
				return
		cSet = self.getPlotColour(dS)
		if not dS.XF: dS.XF = '1d'	#set the axis if there is no default 
		if not dS.YF: dS.YF = '1d'
	
		if ptype=='bar' or ptype=='pie': noXlabels = True
		else: noXlabels = False
		return self.render_str('dashItem.html',item=self,ptype=ptype,plotData=dS.PLOTDATA,title=dS.TITLE,xlabel=dS.XL,ylabel=dS.YL,id=int(entry_id),colorset=colorDict[cSet],XF=axisdict[dS.XF],YF=axisdict[dS.YF],xflag=noXlabels,color=randColor) 		

		
class Dashboard(Plot3Handler):
	def get(self):
		[loggedIn,admin,UN] = self.checkCookies() # check cookies / memcached
		if loggedIn:
			UNdb = db.GqlQuery("SELECT DASH FROM UNPW WHERE UN=:USER",USER=UN).get()
		else:
			self.redirect('/landing')
			return
		
		cSet = self.getUserColour(UN);
		
		if not UNdb.DASH: self.response.out.write('You haven\'t added any data to your Dashboard yet! Select a plot from <a href=\"\\"> your set</a> and click Add to Dash')
		dashList = json.loads(UNdb.DASH) #convert to list
		dashObjList = []
		for item in dashList:	#take the list and build objects
			if item[0] != 'save':
				x=dashObj()
				x.top = item[1]
				x.left = item[2]
				x.w = item[3]
				x.h = item[4]
				x.ptype = item[5]
				x.id=item[0]
				x.color = colorDict[cSet][random.randint(0, len(colorDict[cSet])-1)]
				dashObjList.append(x)
			elif item[0] == 'save':
				sLeft = item[2]
				sTop = item[1]
				
		self.render('dashboard.html',dashObjList=dashObjList,sTop=sTop,sLeft=sLeft,dashList=UNdb.DASH,cSet=colorDict[cSet],UN=UN)
		
	def post(self):
		[loggedIn,admin,UN] = self.checkCookies() # check cookies / memcached
		if loggedIn:
			UNdb = db.GqlQuery("SELECT * FROM UNPW WHERE UN=:USER",USER=UN).get()
		else:
			self.redirect('/')
			return
		if not UNdb.DASH: self.response.out.write('You haven\'t added any data to your Dashboard yet! Select a plot from <a href=\"\\"> your set</a> and click Add to Dash')
		dashList = json.loads(UNdb.DASH) #convert to list
		#find all the ids in the dash so we know what the posts are.
		for item in dashList:
			if item[0] =='save':	#treat the save button seperately
				pos=None
				pos = self.request.get('savebtn')
				if pos:
					pos = pos.split(',')
					self.add_to_dash(dashList,'save',None,str(pos[1])+'px',str(pos[0])+'px',None,None)
			else:
				id = item[0]
				getpos = str(id)+'pos'
				getres = str(id)+'res'
				pos=None
				res=None
				pos = self.request.get(getpos)
				res = self.request.get(getres)
				if pos: pos = pos.split(',')
				if res: res = res.split(',')
				
				if pos and res:
					self.add_to_dash(dashList,id,None,str(pos[1])+'px',str(pos[0])+'px',str(res[0])+'px',str(res[1])+'px')
				elif pos and not res:
					self.add_to_dash(dashList,id,None,str(pos[1])+'px',str(pos[0])+'px',None,None)
				elif not pos and res:
					self.add_to_dash(dashList,id,None,None,None,str(res[0])+'px',str(res[1])+'px')
		dashSave = json.dumps(dashList)
		UNdb.DASH = dashSave
		UNdb.put()

		
class LandingHandler(Plot3Handler):
	def get(self):
		cSet = self.getUserColour('')
		#cSet = 'Rset3'
		self.render('LandingFront.html',colorset=colorDict[cSet])

class ContactHandler(Plot3Handler):
	def write_contact(self,name="",email="",comm="",w1="",w2=""):
		[loggedIn,admin,UN] = self.checkCookies()
		self.render('contact.html',UN=UN,loggedIn=loggedIn,name=name,em=email,comm=comm,w1=w1,w2=w2)

	def get(self):
		self.write_contact()
		
	def post(self):
		
		input_name = self.request.get('name')
		name = cgi.escape(input_name)

		input_em = self.request.get('email')
		em = cgi.escape(input_em)
		
		input_comm = self.request.get('comm')
		comm = cgi.escape(input_comm)

		if not len(str(comm)) > 3:
			w1="Please leave a message </br>"
			self.write_contact(name,em,'',w1,'')
			return

		if not validate_email(em):
			w2="Valid email required </br>"
			self.write_contact(name,'',comm,'',w2)
			return

		[loggedIn,admin,UN] = self.checkCookies()
		newComm = COMMENTS(UN=name,EM=em,COMM=comm)
		newComm.put()

		message = mail.EmailMessage(sender="Robot@plot-3.appspotmail.com",
                            subject="Contact from P3")
		message.to = 'rob.a.edwards@gmail.com'
		message.body=(name+' has conacted your from PLOT3.com \n' +
					'Email: ' + em + '\n' +
					'Logged in as: ' + UN + '\n' +
					'Message: \n ' + comm )
		message.send()

		recvd = 'Thank you for your Feedback!'
		
		self.render('contact.html',UN=UN,loggedIn=loggedIn,recvd=recvd)
		
		
# (((((((((((((((((((((((((((((((((((RANDOM PLOT)))))))))))))))))))))))))))))))))))		
class RandomAddData(Plot3Handler):
	def get(self):
			loggedIn=False
			self.render('add_data_form.html',loggedIn=loggedIn)

		
	def post(self):
		[loggedIn,admin,UN] = self.checkCookies()
			 
		cats = self.request.get('cats')
		cats = cgi.escape(cats)
		title = self.request.get('title')
		title = cgi.escape(title)
		description = self.request.get('description')
		description = cgi.escape(description)
		xlabel = self.request.get('xlabel')
		xlabel = cgi.escape(xlabel)
		ylabel = self.request.get('ylabel')
		ylabel = cgi.escape(ylabel)

		
		xf = self.request.get('XF')		
		yf = self.request.get('YF')

		if xf=='strf':
			tFormat = self.request.get('tFormat')
		else: tFormat = None

		plotData = self.request.get('plotData')
		plotData = modJson(plotData,tFormat)
		
		cSet = self.getPlotColour() #set the user's default colour when adding data
		if cSet=='0':
			cSet='d3set20'

		entry = RANDOM3DB(PLOTDATA=plotData,loggedIn=loggedIn,UN=UN,TITLE=title,DESC=description,XL=xlabel,YL=ylabel,CSET=cSet,XF=xf,YF=yf)
		entry.put()
		entry_id=str(entry.key().id())
		memcache.set(entry_id+'r',entry) #put in memcache
		self.redirect('/random%s' %entry_id)
		
class RandomPlotSet(Plot3Handler):	
	def get(self,entry_id):
		loggedIn = False
		
		dS = memcache.get(str(entry_id)+'r')
		if dS is None:
			dS=RANDOM3DB.get_by_id(int(entry_id))
			logging.error("DB QUERY")
			if dS: memcache.set(str(entry_id),dS)
			else:
				self.response.out.write('There\'s nothing here Bob!')
				return
		ptype = self.request.get("ptype")
		logging.error("DB QUERY!")
		
		cSet = self.getPlotColour(dS)
		
		ptype2,buttonSet,noXlabels = self.checkDataFormat(dS,entry_id,'random')
		if not ptype: ptype=ptype2
		
		
		if not dS.XF: dS.XF = '1d' #set the axis if there is no default
		if not dS.YF: dS.YF = '1d'
			
			
		self.render('PlotSet.html',ptype=ptype,plotData=dS.PLOTDATA,title=dS.TITLE,description=dS.DESC,xlabel=dS.XL,ylabel=dS.YL,size=dS.SZ,id=int(entry_id),buttonSet=buttonSet,colorset=colorDict[cSet],XF=axisdict[dS.XF],YF=axisdict[dS.YF],xflag=noXlabels,loggedIn=loggedIn,randplot=True)

class RandomPlotSettingHandler(Plot3Handler):
	def get(self):
		self.render('settings.html',admin=True,randset=True) #allow any property to be changed
		
		
	def post(self):
		#get the color set, add it to the PLOT's entry in the database
		cSet = self.request.get('cSet')
		xf = self.request.get('XF')
		yf = self.request.get('YF')
		entry_id = self.request.get("id")

		self.response.headers.add_header('Set-Cookie', 'cSet=%s' %str(cSet))		

		key = str(entry_id)+'r'
		dS = memcache.get(key)
		if dS is None:
			dS=RANDOM3DB.get_by_id(int(entry_id))
			logging.error("DB QUERY")
		if cSet: dS.CSET = cSet
		if xf: dS.XF=xf
		if yf: dS.YF=yf
		dS.put()
		memcache.set(key,dS)
		self.redirect('/random'+str(entry_id))


# Plot3 Samples ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class SampleDash(Plot3Handler):
	def get(self):
		#self.response.out.write('where am I?')
		self.render('Sample_Dash.html')

class Logo(Plot3Handler):
	def get(self):
		cSet = 'Rset3'
		self.render('Plot3Logo.html',colorset=colorDict[cSet])
		
app = webapp2.WSGIApplication([('/', MainHandler),
								
								('/addNew',AddDataHandler),
								('/settings_main',MainSettingHandler),
								('/settings',PlotSettingHandler),							
								('/delete',DeleteSet),
								('/([0-9]+)',PlotSet),								
								('/login',Login),
								('/logout',Logout),
								('/signup',Signup),
								('/addDash',addDash),
								('/dash',Dashboard),
								('/landing',LandingHandler),
								('/contact',ContactHandler),
								#('/addNewGlobal',GlobalAddDataHandler),
								#('/settings_main_global',GlobalMainSettingHandler),
								#('/globalsettings',GlobalPlotSettingHandler),
								#('/global([0-9]+)',GlobalPlotSet),
								('/plotSomething',RandomAddData),
								('/plotsomething',RandomAddData),
								('/PlotSomething',RandomAddData),
								('/random([0-9]+)',RandomPlotSet),
								('/randomSettings',RandomPlotSettingHandler),
								('/sampledash',SampleDash),
								('/logo',Logo)],
                              debug=True)

							  #functions to write (check dash)