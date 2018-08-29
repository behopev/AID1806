from flask import Flask
from flask import render_template

app = Flask(__name__)

app.run()

@app.route('/index')
def index():
    title = '首页'
    return render_template('index.html')
    # return '这是首页'

app.run()