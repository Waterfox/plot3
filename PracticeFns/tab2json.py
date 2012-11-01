def tab2json(plotdata,title):
    #Simple, accomodates direct paste from excel. No 1E-7 input.
    #Next, add more than one column
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
        title.append=I[ind+1]
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
    return '['+J2[:-1]+']'