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
	cursor = conn.cursor()
    # execute our query
	cursor.execute("SELECT content FROM page_content WHERE page= 'home' AND location= 'header' AND status = 1")
	header_text = cursor.fetchall()

	cursor2 = conn.cursor()
	cursor2.execute("SELECT content, image_link, header_text FROM page_content WHERE page= 'home' AND location= 'left-block' AND status =1")
	left_block = cursor2.fetchall()

	return render_template('index.html', header_text = header_text, left_block = left_block)

@app.route('/admin')
def admin():
	# return request.args.get('message')
	if request.args.get('message'):
		return render_template('admin.html',
			message = 'Login Failed'
		)
	else: 
		return render_template('admin.html')	


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
	if 'username' in session:
		return render_template('admin_portal.html')
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
		image = request.form['image']

# execute our query
		query = ("INSERT INTO page_content VALUES (DEFAULT, 'home', '"+body+"', 1, 1, 'left_block', NULL, '"+header+"', '"+image+"')")
		print query
		cursor = mysql.connect().cursor()
		cursor.execute(query)
		conn.commit()
		return redirect('/admin_portal?success=Added')

# you have no ticket. no soup for you
	else:	
		return redirect('/admin?message=YouMustLogIn')		

if __name__ == "__main__":
	app.run(debug=True)
