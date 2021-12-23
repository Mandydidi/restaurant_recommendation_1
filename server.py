import os
from sqlalchemy import *
from flask import Flask, request, render_template, g, redirect, Response
import asyncio

app = Flask(__name__)


HOST = 'database-1.cqcjuhcd4k1s.us-east-2.rds.amazonaws.com'
PORT = 3306
USERNAME = 'admin'
PASSWORD = 'Abc!1234567890'
DB = 'hw1_db'

# dialect + driver://username:passwor@host:port/database
DATABASEURI = "mysql+pymysql://{}:{}@{}:{}/{}".format(USERNAME, PASSWORD, HOST, PORT, DB)

engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def start():
  return render_template('login.html')

#login function
@app.route('/login', methods=['POST'])
def login():
  name = request.form['usn']
  pwd = request.form['pwd']
  sql = "SELECT * FROM users WHERE userName={} AND userPWD={};".format("'"+name+"'", "'"+pwd+"'")
  print(sql)
  cursor = g.conn.execute(sql)
  for result in cursor:
    if len(result) > 0:
      cursor.close()
      return render_template("firstpage.html")
  cursor.close()
  return render_template('users_create.html')

# search function
@app.route('/search', methods=['POST'])
def search():
  selected = request.form['search']
  print(selected)
  act = request.form['action']
  print(act)
  if selected == 'User':
    if act == 'Create':
      return render_template('users_create.html')
  elif selected == 'Schedule':
    if act == 'Create':
      return render_template('schedule_create.html')



@app.route('/CreateUser', methods=['POST'])
def createUser():
  # Users(userId: (primary key), userName, userEmail, pwd, Preference: json, links: json)
  name = request.form['username']
  id = request.form['userid']
  email = request.form['useremail']
  pwd = request.form["userpassword"]
  addr = request.form["useraddress"]
  pref = request.form["userpreferences"]
  sql = "INSERT INTO users VALUES " + "('{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(id, name, email, pwd, addr, pref, '{}')
  print(sql)
  cursor = g.conn.execute(sql)
  print('Inserted successfully!')
  rsp = Response('Inserted successfully!', status=200, content_type="application/json")
  cursor.close()
  return rsp

@app.route('/createSchedule', methods=['POST'])
def createSchedule():
  title = request.form['title']
  area = request.form['area']
  res_name = request.form['res_name']
  res_type = request.form['res_type']
  sql = 'SELECT * FROM schedule WHERE scheduledTitle={};'.format("'"+title+"'")
  print(sql)
  cursor = g.conn.execute(sql)
  s_id = '0'
  for result in cursor:
    if len(result) > 0:
      s_id = str(result[0])  # if schedule exists, get schedule id
      print(s_id)
    break
  sql = 'select rid, location from restaurants where name={} AND type={};'.format("'"+res_name+"'", "'"+res_type+"'")
  print(sql)
  cursor = g.conn.execute(sql)
  for result in cursor:
    rid, location = str(result[0]), str(result[1])
  print(rid, location)
  sql = "insert into content values('', {}, {},'', {},'',{},{},{});".format("'"+rid+"'", "'"+res_name+"'", "'"+res_type+"'", "'"+area+"'", '1111', '66')
  print(sql)
  cursor = g.conn.execute(sql)
  sql = 'select count(*) as c from content;'
  print(sql)
  cursor = g.conn.execute(sql)
  for result in cursor:
    c = str(result[0])
  sql = 'insert into schedule values('', {}, {}, {}, {}, {}, {});'.format("'"+c+"'", "'"+title+"'", "2021-12-22 20:41:27", "'"+area+"'", '1', '2')
  print(sql)
  rsp = Response('Created successfully!', status=200, content_type="application/json")
  cursor.close()
  return rsp

async def main():

  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=5000, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()

asyncio.run(main())