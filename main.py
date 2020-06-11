from flask import Flask, render_template, url_for, flash, redirect
import play_scraper
import os
import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

app = Flask(__name__)

def app_fetcher():
  arr=play_scraper.search('top apps', page=1)
  length=min(10,len(arr))
  dict=[]
  for i in range(0,length):
    dict.append(arr[i]['app_id'])
  return dict




@app.route("/")
def home():
  if os.environ.get('GAE_ENV') == 'standard':
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    db = pymysql.connect(user=db_user, password=db_password,unix_socket=unix_socket, db=db_name)
  else:
    host = '127.0.0.1'
    db = pymysql.connect(user=db_user, password=db_password,unix_socket=unix_socket, db=db_name)

  top10app=app_fetcher()
  top10appshow=[]
  cursor = db.cursor()
  for myapp in top10app:
    cursor.execute("SELECT app_id from myapp where app_id= '%s'" % myapp)
    result = cursor.fetchall()   
    dict=play_scraper.details(myapp)
    for key,val in dict.items():
      if(val==None):
        if(key=='video'):
          dict[key]='https://www.youtube.com/watch?v=B-3yZwaGD_k'
        else:
          dict[key]="OPPS!"

    top10appshow.append(dict)
    if(len(result)==0):
      try:
        cursor.execute("INSERT INTO myapp(app_id,category,description,developer,developer_address,developer_email,icon,installs,reviews,score,title,url,video) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(dict['app_id'],dict['category'],dict['description'],dict['developer'],dict['developer_address'],dict['developer_email'],dict['icon'],dict['installs'],dict['reviews'],dict['score'],dict['title'],dict['url'],dict['video']))
        db.commit()
      except:
        db.rollback()
  db.close()
  return render_template('startup_page.html', data=top10appshow)

	
  	
@app.route('/app_details/<app_id>')
def app_details(app_id):
	dict=play_scraper.details(app_id)
	return render_template('details_page.html', data=dict)
	

    


if __name__ == '__main__':
    app.run(debug=True)