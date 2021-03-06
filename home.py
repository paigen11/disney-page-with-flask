from flask import Flask, render_template, request, redirect, session
from flaskext.mysql import MySQL 

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'disney'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

#Make one connection and use it over, and over, and over...
conn = mysql.connect()
# set up a cursor object whihc is what the sql object uses to connect and run queries
cursor = conn.cursor()

app.secret_key = "FHNOGVOIWHWNQFQW(FHGNRUOGEWOUGHEW"

@app.route("/")
def index():
    # execute our query
	cursor.execute("SELECT content FROM page_content WHERE page= 'home' AND location= 'header' AND status = 1")
	header_text = cursor.fetchall()

	#write /run query that will pull three main fields for all three needed rows
	cursor.execute("SELECT content, image_link, header_text, id FROM page_content WHERE page= 'home' AND location= 'left-block' AND status =1")
	left_block = cursor.fetchall()

	return render_template('index.html', header_text = header_text, left_block = left_block)

@app.route('/pages/<id>')
def pages(id):
	query = "SELECT content, big_image, header_text FROM page_content WHERE id="+id
	cursor.execute(query)
	data = cursor.fetchone()
	return render_template('pages.html', data = data)

@app.route('/admin')
def admin():
	# return request.args.get('message')
	if request.args.get('message'):
		return render_template('admin.html',
			message = 'Login Failed'
		)
	elif request.args.get('message1'):
		return render_template('admin.html', 
			message = 'Logged Out'
		)	
	else: 
		return render_template('admin.html')	

@app.route('/logout')
def logout():
	# nuke their session vars. this will end the session which is what we use to let them into the portal
	session.clear()
	return redirect('/admin?message1=LoggedOut')

# make a new route called admin_submit. Add method post so that form can get here
@app.route('/admin_submit', methods=['GET', 'POST'])
#define the method for the new route admin_submit
def admin_submit():
	# print request.form
	if request.form['username'] == 'admin' and request.form['password'] == 'admin':
		# you may proceed
		session['username'] = request.form['username']
		return redirect('/admin_portal')
	else:
		return redirect('/admin?message=login_failed')	

@app.route('/admin_portal')
def admin_portal():
	# session variable 'username' exists ... proceed
	# make sure to check if it's in the dictionary rather than just 'if'
	if 'username' in session and request.args.get('success'):
		home_page_query = "SELECT content, image_link, header_text, location, id, big_image FROM page_content WHERE page= 'home' AND status =1"
		cursor.execute(home_page_query)
		data = cursor.fetchall()
		return render_template('/admin_portal.html', success='Content Added', home_page_content = data)

	elif 'username' in session and request.args.get('success1'):
		home_page_query = "SELECT content, image_link, header_text, location, id, big_image FROM page_content WHERE page= 'home' AND status =1"
		cursor.execute(home_page_query)
		data = cursor.fetchall()
		return render_template('admin_portal.html', success='Content Updated',			home_page_content = data)

	elif 'username' in session and request.args.get('success2'):
		home_page_query = "SELECT content, image_link, header_text, location, id, big_image FROM page_content WHERE page= 'home' AND status =1"
		cursor.execute(home_page_query)
		data = cursor.fetchall()
		return render_template('/admin_portal.html', success='Content Deleted', home_page_content = data)

	elif 'username' in session:
		home_page_query = "SELECT content, image_link, header_text, location, id, big_image FROM page_content WHERE page= 'home' AND status =1"
		cursor.execute(home_page_query)
		data = cursor.fetchall()
		return render_template('admin_portal.html', 
			#data is what it is here, home_page_content is what it is to the template
			home_page_content = data)
	
	# you have no ticket. no soup for you
	else:	
		return redirect('/admin?message=You_must_log_in')

@app.route('/admin_update', methods=['GET', 'POST'])
def admin_update():
	# First... do you belong here?
	if 'username' in session:
	# ok, they are logged in, I will insert your stuff
		body = request.form['body_text']
		header = request.form['header']
		# if 'image' in request.files['image']:
		image = request.files['image']
		image.save('static/images/' + image.filename)
		image_path = image.filename
		
		# if 'image2' in request.files['image2']:
		big_image = request.files['big_image']
		big_image.save('static/images/' + big_image.filename)
		image_path2 = big_image.filename

# execute our query
		query = ("INSERT INTO page_content VALUES (DEFAULT, 'home', '"+body+"', 1, 1, 'left_block', NULL, '"+header+"', '"+image_path+"', '"+image_path2+"')")
		cursor.execute(query)
		conn.commit()
		return redirect('/admin_portal?success=Added')			

# you have no ticket. no soup for you
	else:	
		return redirect('/admin?message=YouMustLogIn')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
	if request.method == 'GET':
		query = "SELECT content, image_link, header_text, id, status, priority, big_image FROM page_content WHERE id="+id
		cursor.execute(query)
		data = cursor.fetchone()
		# return id
		return render_template('edit.html', data = data)
	else:
		#do the post stuff
		content=request.form['body_text']
		image_link = request.form['image']
		header_text= request.form['header']
		status = request.form['status']
		priority = request.form['priority']
		big_image = request.form['big_image']

		query = "UPDATE page_content SET content=%s, image_link=%s, header_text=%s, status=%s, priority=%s, big_image=%s WHERE id =%s"
		cursor.execute(query, (content, image_link, header_text, status, priority, big_image, id))
		conn.commit()
		return redirect('/admin_portal?success1=ContentUpdated')

@app.route('/delete/<id>')
def delete(id):
	cursor.execute("DELETE FROM page_content WHERE id="+id)
	conn.commit()
	return redirect('/admin_portal?success2=ContentDeleted')		

if __name__ == "__main__":
	app.run(debug=True)
