from flask import  *
import mysql.connector
app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Abcd@1234",
   database="intern"
)

def getAllFaculty():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * from faculty")
    rows = mycursor.fetchall()
    return rows

def fillDays():
    mycursor = mydb.cursor()
    sql="insert into student(dayy) values(%s)"
    val=["mon","tue","wed","thur","fri"]
    mycursor.executemany(sql,val)
    rows = mycursor.fetchall()

def getCourseName(cid):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT name from course where cid='"+cid+"' ; ")
    rows = mycursor.fetchall()
    return rows[0][0]

def getFacultyCourses(fid):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT cid1,cid2,cid3,cid4 from mapping where fid="+str(fid))
    rows = mycursor.fetchall()
    return rows

def getCourses():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * from course")
    rows = mycursor.fetchall()
    return rows

def getFacultyName(fid):
    mycursor = mydb.cursor()
    sql = "select name from faculty where fid="+str(fid)
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    return rows[0][0]

def getFacultyRoom(fid):
    mycursor = mydb.cursor()
    sql = "select room from mapping where fid="+str(fid)
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    return rows[0][0]

def getSubjectFaculty(cid):
    mycursor = mydb.cursor()
    sql="SELECT fid FROM mapping WHERE '"+cid+"' IN (cid1,cid2,cid3,cid4);"
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    fac=[]
    for r in rows:
        a=getFacultyName(r[0])
        fac.append((a,r[0]))
    return fac

def indexFinder(cid):
    subs=getCourses()
    for i in range(len(subs)):
        if cid==subs[i][1]:
            return i
    else:
        return -1

#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------

@app.route('/',methods=['GET','POST'])
def Homepage():
    return render_template("Homepage.html")

@app.route('/Student',methods=['GET','POST'])
def Student():
    rows=getCourses()
    fac=[]
    for c in rows:
        fac.append(getSubjectFaculty(c[1]))
    return render_template("Student.html", rows=rows,fac=fac)


@app.route('/lectureHall',methods=['GET','POST'])
def lectureHall():
    return render_template("lectureHall.html")

@app.route('/Faculty',methods=['GET','POST'])
def Faculty():
    fac = getAllFaculty()
    return render_template("Faculty.html",fac=fac)

@app.route('/backtoHome')
def backtoHome():
    return render_template("Homepage.html")

@app.route('/backtohall')
def backtohall():
    return render_template("lectureHall.html")

@app.route('/backtostudent')
def backtostudent():
    return render_template("Student.html")

#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------


@app.route('/getlectureroom',methods=['POST'])
def getlectureroom():
    if request.method =='POST':
        roomnum=request.form.get('LH')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT cid1,cid2,cid3,cid4,fid from mapping where room='" + roomnum + "'")
        details = mycursor.fetchall()
        mycursor.execute("SELECT * from tt")
        period = mycursor.fetchall()
        l = []
        for i in range(1, len(period)):
            l.append(period[i][0])
        l2 = []
        for i in details:
            y = i[4]
            for j in range(len(i) - 1):
                l2.append(getCourseName(i[j])+" "+getFacultyName(y))
        l2 = [l2] * 5
        e1 = []
        days = ['Mon(Lecture)', 'Tue(Lab)', 'Wed(Lecture)', 'Thur(Lab)', 'Fri(Lecture)']
        for i in range(len(l2)):
            k = l2[i]
            k = k[::-1]
            k.append(days[i])
            k = k[::-1]
            e1.append(k)
        return render_template("getlecturehallTimetable.html",rows=e1)

helper=[]
@app.route('/getfacultyTT',methods=['POST'])
def getfacultyTT():
    if request.method=='POST':
        fid=request.form.get('fac')
        cname=getFacultyCourses(fid)
        room=getFacultyRoom(fid)
        k=[]
        for i in range(4):
            k.append(cname[0][i])
        p=[]
        for i in k:
            p.append((indexFinder(i),i))

        full=['']*8
        for i in range(len(p)):
            for j in range(len(full)):
                if p[i][0]==j:
                    full[j]=p[i][1]+' '+str(room)
        res=[full]*5
        e1 = []
        days = ['Mon(Lecture)', 'Tue(Lab)', 'Wed(Lecture)', 'Thur(Lab)', 'Fri(Lecture)']
        for i in range(len(res)):
            k = res[i]
            k = k[::-1]
            k.append(days[i])
            k = k[::-1]
            e1.append(k)

        return render_template("Get-LectureTimeTable.html",rows=e1)

@app.route('/registered',methods=['POST'])
def registered():
    global helper
    if request.method =='POST':
        roll=request.form.get('num')
        name=request.form.get('name')
        noSubs=len(getCourses())
        li=[]
        for i in range(noSubs):
            var=request.form.get("sb"+str(i))
            if var is not None:
                li.append((var,request.form.get("fac"+str(i))))
        mycursor = mydb.cursor()
        mycursor.execute("select roll  from student where roll="+str(roll))
        result= mycursor.fetchall()
        if len(result):
            m = "This Roll Number already registered"
            l = "/Student"
            ms = '<script type="text/javascript">alert("' + m + '");location="' + l + '";</script>'

        else:

            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO student VALUES(%s,%s)", (name,int(roll)))
            mydb.commit()
            for i in li:
                helper.append((roll, i[1],i[0]))
                mycursor.execute("INSERT INTO register VALUES(%s,%s,%s)", (int(roll),int(i[1]),i[0]) )
                mydb.commit()

            m = "Successfully registered"
            l = "/getStudentTimetable"
            ms = '<script type="text/javascript">alert("' + m + '");location="' + l + '";</script>'

    return ms


@app.route("/getStudentTimetable",methods=["GET","POST"])
def getStudentTimetable():
    global helper
    ful = [""] * 8
    for i in range(len(helper)):
        x = indexFinder(helper[i][2])
        if x != -1:
            t = getCourseName(helper[i][2])
            q = getFacultyName(helper[i][1])
            r = getFacultyRoom(helper[i][1])
            com = str(t) + '(' + str(q) + ',' + str(r) + ')'
            ful[x] = com
    result=[ful]*5
    e1=[]
    days=['Mon(Lecture)','Tue(Lab)','Wed(Lecture)','Thur(Lab)','Fri(Lecture)']
    for i in range(len(result)):
        k=result[i]
        k=k[::-1]
        k.append(days[i])
        k=k[::-1]
        e1.append(k)
    helper=[]
    return render_template('getStudentTimetable.html',rows=e1)




#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True, host= '192.168.0.190')


