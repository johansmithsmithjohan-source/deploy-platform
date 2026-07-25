from flask import Flask
app=Flask(__name__)
@app.route("/")
def home():return"<h1>Deploy Platform LIVE!</h1>",{"Content-Type":"text/html"}
@app.route("/health")
def hh():return{"s":"ok"},200
