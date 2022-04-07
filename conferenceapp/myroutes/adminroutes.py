'''This file is the controller that determines the path when the user visits our routes'''
import math, random, os

from flask import render_template, request, abort, redirect, flash, make_response, session, url_for

from sqlalchemy import or_


from werkzeug.security import generate_password_hash, check_password_hash

from conferenceapp import app,db
from conferenceapp.mymodels import User, State, Skill, Breakout, Admin
from conferenceapp.forms import LoginForm

@app.route('/admin/login')
def adminlogin():
    return render_template("admin/login.html")


@app.route('/admin/reg')
def registrations():
    users = db.session.query(User,State,Skill).join(State).join(Skill).all()
    #users = User.query.join(State).join(Skill).add_column(State, Skill).all()
    #users = db.session.query(User).join(State).join(Skill).filter(Skill.skill_id==1).all()
    
    #syntax for like
    #users2 = db.session.query(User).filter(User.user_fname.like('%ola%'))
    #syntax for join
    #users = User.query.outerjoin(State, User.user_stateid==State.state.id).add_columns(State).all()

    return render_template("admin/allusers.html", users = users)


#@app.route("/admin/submit/login", methods=['POST'])
#def submit_adminlogin():
#    username = request.form.get('username')
#    password = request.form.get('password')
#    if username == '' or password == '':
#        flash('Login failed, kindly fill the reqiured fields')
#        return redirect ('/admin/login')
#    else:
#        admindeets = db.session.query(Admin).filter(Admin.admin_username == username).filter(Admin.admin_password == password).first()
#        if admindeets:
#            session['admin'] = admindeets.admin_id
#            return redirect(url_for('adminpage'))
#        else:
#            flash('Invalid login credentials')
#            return redirect(url_for('adminlogin'))

#method for hashed password
@app.route("/admin/submit/login", methods=['POST'])
def submit_adminlogin():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == '' or password == '':
        flash('Login failed, kindly fill the reqiured fields')
        return redirect ('/admin/login')
    else:
        admindeets = db.session.query(Admin).filter(Admin.admin_username == username).first()
        formated_pwd = admindeets.admin_password
        chk = check_password_hash(formated_pwd,password)

        if chk == True:
            session['admin'] = admindeets.admin_id
            return redirect(url_for('adminpage'))
        else:
            flash('Invalid login credentials')
            return redirect(url_for('adminlogin'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin')
    return redirect ('/admin/login')

@app.route('/admin/home')
def adminpage():
    return render_template('admin/index.html')


@app.route('/admin/upload', methods=['POST', 'GET'])
def admin_upload():
    if request.method == 'GET':
        return render_template('admin/test.html')
    else:
        file = request.files.get('image') 
        original_name= file.filename
        
        #generate random string
        fn = math.ceil(random.random() * 10000000)

        #ext = original_name.split('.') #ext[-1]
        ext =os.path.splitext(original_name)
        save_as = str(fn)+ext[1]

        #specify allowed files
        allowed = ['.jpg', '.png', '.gif']
        if ext[1].lower() in allowed:
            #save statement below
            file.save(f'conferenceapp/static/assets/img/{save_as}')
            return f"Submitted and saved as {save_as}"
        else:
            return 'File type not allowed'

@app.route('/admin/breakouts/')
def breakouts():
    break_deets = Breakout.query.all()
    #db.session.query(Breakout).all()
    return render_template('admin/breakout.html', break_deets=break_deets )


@app.route('/admin/addbreakout', methods=['GET','POST'])
def addbreakout():
    if request.method =='GET':
        skill = Skill.query.all()
        return render_template('admin/addbreakouts.html', skill=skill)
    else:
        #Retrieve form data (request.form....)
        title = request.form.get('title')
        level = request.form.get('level')
        #request file
        pic_object = request.files.get('image')
        original_file =  pic_object.filename
        if title =='' or level =='':
            flash("Title and Level cannot be empty")
            return('/admin/addbreakout')
        if original_file !='': #check if file is not empty
            extension = os.path.splitext(original_file)
            if extension[1].lower() in ['.jpg','.png']:
                fn = math.ceil(random.random() * 100000000)  
                save_as = str(fn)+extension[1] 
                pic_object.save(f"conferenceapp/static/assets/img/{save_as}")
                #insert other details into db
                b = Breakout(break_title=title,break_picture=save_as,break_skillid=level)
                db.session.add(b)
                db.session.commit()            
                return redirect("/admin/breakouts")
            else:
                flash('File Not Allowed')
                return redirect("/admin/addbreakout")

        else:
            save_as =""
            b = Breakout(break_title=title,break_picture=save_as,break_skillid=level)
            db.session.add(b)
            db.session.commit() 
            return redirect("/admin/breakouts")  




@app.route('/admin/breakout/delete/<int:id>')
def admin_delete(id):
    b = db.session.query(Breakout).get(id)
    db.session.delete(b)
    db.session.commit()
    flash(f'Breakout session {id} deleted')
    return redirect('/admin/breakouts')

@app.route('/admin/signup', methods=['POST','GET'])
def admin_signup():
    if request.method == 'GET':
        return render_template('admin/signup.html')
    else:
        username = request.form.get('username')
        pwd1 = request.form.get('password')
        pwd2 = request.form.get('password2')

        if pwd1 == pwd2:
            formated = generate_password_hash(pwd1)
            ad = Admin(admin_username=username, admin_password=formated)
            db.session.add(ad)
            db.session.commit()
            flash('New User Signed Up')
            return redirect('/admin/login')
        else:
            flash("The two passwprds do not match")
            return redirect('/admin/signup')
