import itertools, os, time

start=time.time()

#files=itertools.chain(*((j+"/"+i for i in os.listdir(j) if i.endswith(".py")) for j in ("../src","../srcplug"))) 
files=[]
for j in ("../src","../srcplug","../util"):
    for i in os.listdir(j):
        if i.endswith(".py"):
            files.append(j+"/"+i)
codelines=0
blanklines=0
commentlines=0

clength=40
olength=12

for j in files:
    with open(j) as f:
        lines=0
        blank=0
        comment=0
        for l in f.readlines():
            ls=l.strip()
            if len(ls)==0:
                blank+=1
            elif ls[0]=="#":
                comment+=1
            else:
                lines+=1
        codelines+=lines
        blanklines+=blank
        commentlines+=comment
        #print ("file",j,"\tcode:",lines,"lines\tblank:",blank,"lines\tcomment:",comment,"lines")
        tmp="file "+str(j)
        tmp+=" "*(clength-len(tmp))
        tmp+="code: "+str(lines)
        tmp+=" "*(clength+olength-len(tmp))
        tmp+="blank: "+str(blank)
        tmp+=" "*(clength+2*olength-len(tmp))
        tmp+="comment: "+str(comment)
        print (tmp)
print ("----------------------")
print ("total values: ")
print ("code lines:",codelines)
print ("blank lines:",blanklines)
print ("comment lines:",commentlines)
print ("total lines:",codelines+blanklines+commentlines)

end=time.time()
print ()
print ("start time:",start,"end time",end,"dif",end-start)
