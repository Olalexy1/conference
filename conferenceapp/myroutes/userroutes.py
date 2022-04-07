'''This file is the controller that determines the path when the user visits our routes'''

import json, random

from flask import render_template, request, abort, redirect, flash, make_response, session, url_for

from sqlalchemy import insert, desc

from conferenceapp import app,db
from conferenceapp.mymodels import User, State, Skill, Breakout, user_sessions, Contactus, Posts, Comments, Myorder, Payment, OrderDetails
from conferenceapp.forms import LoginForm, ContactusForm
from conferenceapp import Message, mail


@app.route("/sendmail")
def sendmail():
    subject = "Automated Email"
    sender = "Admin@conference.com"
    recipient = ["ajayiolalekan729@gmail.com"]
    #use try except to check for errors 
    try:
        #instantiate an object of message
        #method1
        #msg= Message(subject=subject,sender=sender,recipients=recipient, body= "This is a sample email sent from python app.")

        #method2
        msg = Message()
        msg.subject = subject
        msg.sender = sender
        msg.body = "Test Message Again using method 2"
        msg.recipients = recipient

        #sending HTML
        htmlstr = "<div><h1 style='color:red'>Thank you for signing up</h1><img src='https://www.google.com/search?q=images+of+nature&sxsrf=APq-WBtj51e_k53tNdPYNOtmtCR71zrJ2w:1649324115249&tbm=isch&source=iu&ictx=1&vet=1&fir=aL4qwrJK-dkI7M%252CS_vTm5ENABcIeM%252C_%253B3du_EqKvbNmtvM%252CbH1YFPQkm85agM%252C_%253Bvrk6TNwYAhtb9M%252CEHfOCDsIOEvcPM%252C_%253Bcmiysi_piO9m3M%252CBa_eiczVaD9-zM%252C_%253BISsdmwh92GPtrM%252CtnVTsEa64LdCyM%252C_%253BuL_rsjXeqb7ObM%252CPSHuCxyQLznhgM%252C_%253BGzBlAT1pJdNniM%252CF99EUUSxga2XkM%252C_%253B7AkFMcgT-uzaxM%252CBa_eiczVaD9-zM%252C_%253BbPEjCGlyljWxvM%252CeOeeJu4TOHIxoM%252C_%253BweIQSehMobmZXM%252CbH1YFPQkm85agM%252C_%253BIObEFTP5-88txM%252CjcfJekXmSUdJHM%252C_%253BUVAHTXdge9JbrM%252CtnVTsEa64LdCyM%252C_%253BM_-opqyyVydhzM%252C0X_sMLtpy1NMdM%252C_%253B8-xblicz86595M%252C8XuhtxSRxFSBCM%252C_&usg=AI4_-kSAIsOUanSPK5cVOYWmncjPC7TNmw&sa=X&ved=2ahUKEwi0poCQ04H3AhUEgRoKHYZBANoQ9QF6BAgIEAE#imgrc=3du_EqKvbNmtvM' width='100'</div>"

        msg.html = htmlstr

        #for sending attachments
        with app.open_resource("invite.pdf") as fp:
            msg.attach("invite_savedas.pdf", "application/pdf", fp.read())

        mail.send(msg)
        return "Mail Sent"
    except:
        return "Connection refused"

@app.route("/")
def home():
    login=LoginForm()
    contactform = ContactusForm()
    id = session.get('loggedin')
    userdeets = User.query.get(id)
    b = Breakout.query.all()
    #connect to api withouth authentication
    #response = requests.get('http://127.0.0.1:8082/api/v1.0/listall')

    #method 1
    #connect to api with authentitcation
    #response = requests.get('http://127.0.0.1:8082/api/v1.0/listall', auth=('samteddy', '1234'))
    #retreive the json in the request
    #hostel_json = response.json()
    #status = hostel_json.get('status')

    #method 2
    try:
        http = urllib3.PoolManager()
        response = http.request('GET', "http://127.0.0.1:8082/api/v1.0/listall")
        hostel_json = json.loads(response.data)
    except:
        hostel_json = {}

    #pass it to the template
    return render_template("user/index.html", login=login, userdeets=userdeets, b=b, contactform=contactform, hostel_json=hostel_json)
    


@app.route('/contact/us', methods=['GET','POST'])
def contactus():
    if request.method == 'GET':
        contactform = ContactusForm()
        return render_template('user/layout.html', contactform=contactform)
    else:
        contact = ContactusForm()
        fullname = contact.fullname.data
        email = contact.email.data
        message = contact.message.data
        if contact.validate_on_submit():
            info = Contactus(contactus_fullname=fullname, contactus_email=email, contactus_message=message)
            db.session.add(info)
            db.session.commit()
            cid = info.contact_id

            if cid:
                return json.dumps({"id":cid, "msg":"Message Sent"})
            else:
                return "sorry please try again"


@app.route('/donations', methods=['GET', 'POST'] )
def donations():
    if request.method == 'GET':
        return render_template('user/donationform.html')
    else:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        amt = request.form.get('amount')
        status = 'pending'
        #generate a random number as transaction ref
        ref = int(random.random() * 1000000000) 
        #keep ref in session
        session['refno'] = ref
        #insert into db
        db.session.execute(f"INSERT INTO donation SET fullname='{fullname}', email='{email}', amount='{amt}', status='pending', ref='{ref}'")
        db.session.commit()
        return redirect ('/confirmpay')

@app.route('/confirmpay')
def confirm():
    ref = session.get('refno')
    if ref== None:
        return redirect('/donations')
    else:
        qry = db.session.execute(f"SELECT * FROM donation WHERE ref={ref}")
        data = qry.fetchone()
        return render_template('user/payconfirm.html', data=data)


@app.route('/breakoutpayment')
def breakoutpay():
    contactform = ContactusForm()
    id = session.get('loggedin')
    if id == None:
        return redirect ('/')
    else:
        userdeets = User.query.get(id)
        userskill = userdeets.user_skillid
        breakdeets = db.session.query(Breakout).filter(Breakout.break_skillid == userskill).all()
        return render_template('user/breakoutwithpayment.html', userdeets=userdeets, breakdeets=breakdeets, contactform = contactform,)





@app.route('/user/sendbreakout', methods = ['POST', 'GET'])
def send_breakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    if request.method=='POST':
        #retrieve form data, breakout ids
        bid = request.form.getlist('bid')

        #insert new recd into myorder,
        mo = Myorder(order_userid=loggedin)
        db.session.add(mo)
        db.session.commit()
        orderid = mo.order_id
        #generate a trans ref using random (save in session), insert into payment table
        ref = int(random.random() * 10000000)
        session['refno'] = ref
        #loop over the selected breakout ids and insert into
        #order_details, 
        totalamt = 0
        for b in bid:
            breakdeets = Breakout.query.get(b)
            break_amt = breakdeets.break_amt
            totalamt = totalamt + break_amt
            od = OrderDetails(det_orderid=orderid,det_breakid=b,det_breakamt=break_amt)
            db.session.add(od)

        db.session.commit()
        p = Payment(pay_userid=loggedin,pay_orderid=orderid,pay_ref=ref,pay_amt=totalamt)       
        db.session.add(p) 
        db.session.commit()
        return redirect("/user/confirm_breakout")    
    else:
        return redirect("/user/home")

#This route will show all chosen sessions and connect to paystack
@app.route("/user/confirm_breakout", methods=['POST', 'GET'])
def confirm_break():
    loggedin = session.get('loggedin')
    ref = session.get('refno')
    if loggedin == None or ref == None:
        return redirect("/")
    userdeets = User.query.get(loggedin) 
    deets = Payment.query.filter(Payment.pay_ref==ref).first() 

    if request.method == 'GET':          
        contactform = ContactusForm()                
        return render_template("user/show_breakout_confirm.html",deets = deets,userdeets=userdeets,contactform=contactform)
    else:
        url = "https://api.paystack.co/transaction/initialize"
        
        data = {"email":userdeets.user_email,"amount":deets.pay_amt}
        headers = {"Content-Type": "application/json", "Authorization":"Bearer sk_test_dadd9863193a1e432e4c765c77d4386f3e009646"}

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

        rspjson = json.loads(response.text)
        if rspjson.get('status') == True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            return 'Please try again'

@app.route('/user/payverify')
def paystack():
    return "JSON response from paystack will be sent here"


@app.route('/demo/available')
def available():
    return render_template('user/checkavailable.html')

@app.route('/check/result')
def result():
    user= request.args.get('us')
    deets = db.session.query.filter(User.user_email==user).all()
    if deets:
        return "username is taken"
    else:
        return f"{user} available"

@app.route('/check/lga')
def check():
    states = State.query.all()
    return render_template('user/load_lga.html', states=states)

@app.route('/demo/lga', methods=['POST'])
def show_lga():
    state = request.form.get('stateid')
    #TO DO: write a query that wll fetch from LGA table where state_id =state
    res = db.session.execute(f"SELECT * FROM lga WHERE state_id={state}")
    results = res.fetchmany(20)

    select_html = "<select>"
    for x,y,z in results:
        select_html = select_html + f"<option value='{x}'>{z}</option>"
    
    select_html = select_html + "</select>"

    return select_html




@app.route('/user/discussion')
def discussion():
    contactform = ContactusForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    else:
        userdeets = User.query.get(loggedin)
        postdeets = db.session.query(Posts).all()
        return render_template('user/discussions.html', contactform = contactform, userdeets = userdeets, postdeets = postdeets)

@app.route('/post/details/<id>')
def postdetails(id):
    contact = ContactusForm()
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    if loggedin == None:
        return redirect("/")
    else:
        postdeets = db.session.query(Posts).get(id)
        
        commentdeets = db.session.query(Comments).filter(Comments.c_postid==id).order_by(desc(Comments.c_date)).all()
        return render_template("user/postdetails.html", userdeets=userdeets, postdeets=postdeets, contact=contact, commentdeets=commentdeets)

@app.route('/post/comment', methods=['POST'])
def post_comments():
    loggedin = session.get('loggedin')
    postid = request.form.get('postid')
    comment = request.form.get('comment')

    #method 1
    #c = Comments()
    #db.session.add(c)
    #c.c_userid = loggedin
    #c.c_postid = postid
    #c.c_comment = comment
    #db.session.commit()

    #method 2
    c= Comments(c_userid=loggedin, c_postid=postid, c_comment=comment)
    db.session.add(c)
    db.session.commit()

    #method 3
    user = User.query.get(loggedin)
    dpost = Posts.query.get(postid)
    c= Comments()
    db.session.add(c)
    user.user_comments.append(c)
    dpost.post_comments.append(c)
    c.c_comment= comment
    db.session.commit()

    ddate = c.c_date
    return f"{comment} and {ddate}"


@app.route('/user/login', methods=['POST'])
def submit_login():
    login = LoginForm()
    contactform = ContactusForm()
    username = request.form.get('username') #method 1
    pwd = login.pwd.data #method 2
    #validate
    if login.validate_on_submit():
        #deets = User.query.filter(User.user_email==username, User.user_pass==pwd).all() #method1
        deets = User.query.filter(User.user_email==username).filter(User.user_pass==pwd).first()
        if deets:
            id = deets.user_id
            session['loggedin'] = id
            return redirect('/userhome')
        else:
            flash('Invalid Credentials')
            return redirect ('/')
    else:
        return render_template('user/index.html', login=login, contactform = contactform)


@app.route('/register/', methods=['GET','POST'])
def register():
    contactform = ContactusForm()
    id = session.get('loggedin')
    userdeets = User.query.get(id)
    if request.method == 'GET':
        skill = db.session.query(Skill).all()
        state = State.query.all()

        return render_template('user/register.html', skill=skill, state=state, userdeets=userdeets, contactform = contactform)
    else:
        email = request.form.get('email')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        state = request.form.get('state')
        skill = request.form.get('skill')
        #validate
        if email == '' or pwd1 =='' or fname == '' or lname == '' or state == '' or skill == '':
            flash('Registration failed, kindly fill the reqiured fields')
            return redirect ('/register')
        elif pwd1 != pwd2:
            flash('Kindly ensure that the passwords match')
            return redirect ('/register')
        else:
            flash('Registration sucessful')
            profile = User(user_email = email, user_pass = pwd1, user_fname = fname, user_lname = lname, user_stateid = state, user_skillid = skill)
            db.session.add(profile)
            db.session.commit()
            id = profile.user_id
            session['loggedin'] = id
            return redirect('/userhome')


@app.route('/userhome/')
def userhome():
    contactform = ContactusForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    else:
        userdeets = db.session.query(User).get(loggedin)
        return render_template ('user/userhome.html', loggedin = loggedin, userdeets = userdeets, contactform = contactform)


@app.route('/logout')
def logout():
    session.pop('loggedin')
    return redirect ('/')


@app.route('/breakout')
def breakout():
    contactform = ContactusForm()
    id = session.get('loggedin')
    if id == None:
        return redirect ('/')
    else:
        userdeets = User.query.get(id)
        userskill = userdeets.user_skillid
        breakdeets = db.session.query(Breakout).filter(Breakout.break_skillid == userskill).all()

        return render_template('user/breakout.html', userdeets=userdeets, breakdeets=breakdeets, contactform = contactform)


@app.route('/user/regbreakout', methods=['POST'])
def reg_breakout(): 
    #getlist() to retrieve multiple form elements with same name
    bid = request.form.getlist('bid') #example [1,2,3]
    loggedin = session.get('loggedin')

    user = User.query.get(loggedin)

    db.session.execute(f"DELETE FROM user_breakout WHERE user_id='{loggedin}'")
    db.session.commit()

##associate table insert
    for i in bid:
        #stat = user_sessions.insert().values(user_id= loggedin, breakout_id=i)
        #db.session.execute(stat)
        #db.session.commit()

        #method2 - Using SQLAlchemmy ORM
        item = Breakout.query.get(i)
        user.mybreakouts.append(item)
        db.session.commit()

    return redirect('/breakout')


@app.route('/user/editprofile')
def editprofile():
    contactform = ContactusForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    else:
        userdeets = db.session.query(User).get(loggedin)
        all_levels = Skill.query.all()
        state = State.query.all()
        return render_template('user/profile.html', userdeets = userdeets, all_levels = all_levels, state = state, contactform = contactform)



#@app.route('/user/update/<id>')
#def user_update(id):
  #  user = User.query.get(id)
  #  user.user_fname = 'Ademola'
  #  user.user_lname = 'Code'
  #  user.user_phone = '08098765432'
  #  db.session.commit()
  #  return 'Done'


@app.route('/user/update', methods=['GET','POST'])
def user_update():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    if request.method == 'GET':
        return redirect('/userhome')

    userdeets = User.query.get(loggedin)
        
    userdeets.user_fname = request.form.get('fname')
    userdeets.user_lname = request.form.get('lname')
    userdeets.user_address = request.form.get('address')
    userdeets.user_stateid = request.form.get('state')
    userdeets.user_skillid = request.form.get('skill')
    userdeets.user_phone = request.form.get('phone')
    db.session.commit()
    flash('Update sucessful')
    return redirect (url_for('editprofile'))


    '''
@app.route('/contact/us')
def contactus():
        contactform = ContactusForm()
        return render_template('user/layout.html', contactform=contactform)
        


@app.route('/contact/feedback', methods=['GET','POST'])
def feedback():
    contact = ContactusForm()
    fullname = contact.fullname.data
    email = contact.email.data
    message = contact.message.data
    if contact.validate_on_submit():
        info = Contactus(contactus_fullname=fullname, contactus_email=email, contactus_message=message)
        db.session.add(info)
        db.session.commit()
        return "This form is submitted"
    else:
        return "failed"
'''