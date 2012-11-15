class GLOBAL3DB(db.Model):
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
	SERIES = db.StringProperty()	#data series name, used to feature datasets

class GlobalHandler(Plot3Handler):
	    def get(self):
		
		Feature = self.getState()
		#Get and check the cookie, find the UN
		[loggedIn,admin,UN] = self.checkCookies()
		
		vtype = self.request.get("vtype")
	
		dbTCg = memcache.get('dbTCg')
		if dbTCg is None: #in memcache?
			dbTCg = db.GqlQuery("SELECT TITLE,CATS,SZ FROM GLOBAL3DB WHERE SERIES = :FEATURE ORDER BY TS DESC",FEATURE=Feature).fetch(40)
			logging.error("DB QUERY")
			if dbTCg: memcache.set('dbTCg',dbTCg) #in DB?
			else:
				if admin==True: self.redirect('/addNewGlobal')
				else: 
					self.response.out.write('The Website had not been initialized')
					# self.redirect('/login')
					return
				
		#self.response.out.write(dbtype)
		JSankey = SankeyNodesLinks(dbTCg)
		# JTree = TreeNodesLinks(dbTC)
		cSetMain = self.getUserColour(UN)
		
		global lastID
		global lastptype
		lastID=None
		lastptype=None
		
		PageTitle = 'PLOT3.com'
		
		if not vtype:
			vtype = 'sankey'

		if vtype == 'sankey':
			self.render('main_Sankey_Global.html',dataset=JSankey,Title=PageTitle,loggedIn=loggedIn,admin=admin,colorset=colorDict[cSetMain])

class GlobalAddDataHandler(Plot3Handler):
	def get(self):
		#Get and check the cookie, find the UN
		[loggedIn,admin,UN] = self.checkCookies()
		
		if admin:
			self.render('add_data_global.html',loggedIn=loggedIn)
		else:
			self.response.out.write('Your not an admin Joe!')
			return
		
	def post(self):
		[loggedIn,admin,UN] = self.checkCookies()
		series = self.request.get('series')
		series = (cgi.escape(series)).lower()
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
		plotdata = self.request.get('plotdata')
		plotdata = cgi.escape(plotdata)
		plotdata_js,size = tab2json(plotdata,title)
		
		xf = self.request.get('XF')		
		yf = self.request.get('YF')
		
		cSet = self.request.cookies.get('cSet','0')
		if cSet=='0':
			cSet='d3set20'
		entry = GLOBAL3DB(SERIES=series,UN=UN,CATS=cats,PLOTDATA=plotdata_js,TITLE=title,DESC=description,XL=xlabel,YL=ylabel,SZ=size,CSET=cSet,XF=xf,YF=yf)
		entry.put()
		entry_id=str(entry.key().id())
		memcache.set(entry_id+'g',entry) #put in memcache
		memcache.delete('dbTCg')
		self.redirect('/global%s' %entry_id)

class GlobalPlotSet(Plot3Handler):
		
	def get(self,entry_id):
		[loggedIn,admin,UN] = self.checkCookies()	
		
		key = str(entry_id)+'g'
		dS = memcache.get(key)
		if dS is None:
			dS=GLOBAL3DB.get_by_id(int(entry_id))
			logging.error("DB QUERY")
			if dS: memcache.set(key,dS)
			else:
				self.response.out.write('There\'s nothing here Bob!')
				return
		ptype = self.request.get("ptype")
		logging.error("DB QUERY!")
		
		cSet = self.getPlotColourGlobe(dS)
		
		ptype2,buttonSet,noXlabels = self.checkDataFormat(dS,entry_id,'global')
		if not ptype: ptype=ptype2
				
		global lastID
		global lastptype
		lastID = entry_id
		lastptype = ptype
		
		if not dS.XF:	#set the axis if there is no default
			dS.XF = '1d'
		if not dS.YF:
			dS.YF = '1d'
			
		self.render('PlotSet.html',ptype=ptype,plotData=dS.PLOTDATA,UN=dS.UN,cats=dS.CATS,title=dS.TITLE,description=dS.DESC,xlabel=dS.XL,ylabel=dS.YL,size=dS.SZ,id=int(entry_id),buttonSet=buttonSet,colorset=colorDict[cSet],XF=axisdict[dS.XF],YF=axisdict[dS.YF],globe=True,xflag=noXlabels)

class GlobalMainSettingHandler(Plot3Handler):
	def get(self):
		self.render('settings_main.html')	

	def post(self):
		#get the color set, add it to cookie, if USER, set to user default in UNPW DB
		cSetMain = self.request.get('cSet')
		if cSetMain is None:
			cSetMain = 'Rset2'
		#self.response.headers.add_header('Set-Cookie', 'cSetMain=%s' %str(cSetMain))
		self.secureCookie('cSetMain',cSetMain)
		self.redirect('/global')

class GlobalPlotSettingHandler(Plot3Handler):
	def get(self):
		[loggedIn,admin,UN] = self.checkCookies()
		self.render('settings.html',admin=admin)
		
		
	def post(self):
		#get the color set, add it to the PLOT's entry in the database
		cSet = self.request.get('cSet')
		xf = self.request.get('XF')
		yf = self.request.get('YF')
		entry_id = self.request.get("id")
		
		[loggedIn,admin,UN] = self.checkCookies()
		self.response.headers.add_header('Set-Cookie', 'cSet=%s' %str(cSet))
		self.secureCookie('cSet',cSet)
		
		if admin == True:
			key = str(entry_id)+'g'
			dS = memcache.get(key)
			if dS is None:
				dS=GLOBAL3DB.get_by_id(int(entry_id))
				logging.error("DB QUERY")
			if cSet: dS.CSET = cSet
			if xf: dS.XF=xf
			if yf: dS.YF=yf
			dS.put()
			memcache.set(key,dS)
		self.redirect('/global'+str(entry_id))
