from routes import *
import routes
from flask import Flask, Response
app=Flask(__name__)

@app.route("/")
def home():
    d=L()
    cs=""
    for pid,pr in d["p"].items():
        s="running"if pr.get("s")in(1,"on")else"crashed"if pr.get("s")=="cr"else"stopped"
        tp=pr.get("t","st").upper()
        nm=pr.get("n",pid)
        cs+=f'<div class="c"><b>{nm}</b> [{s}] {tp} - <a href="/e/{pid}">Edit</a> | <a href="/s/{pid}/">Visit</a> | <button onclick="tg(\\'{pid}\\')">Toggle</button> | <button onclick="dl(\\'{pid}\\')">Del</button></div>'
    if not d["p"]:cs="<p>No apps yet. Create one!</p>"
    try:h=open("t/home.html").read()
    except:h="<html><h1>Deploy Platform</h1><div>{{cards}}</div></html>"
    return Response(h.replace("{{cards}}",cs),mimetype="text/html")

@app.route("/e/<i>")
def edit(i):
    d=L();pr=d["p"].get(i)
    if not pr:return"Not found",404
    m=pr.get("m","a.py"if pr.get("t")=="py"else"i.html")
    f=P/i/m;c=f.read_text()if f.exists()”se""
    try:h=open("t/edit.html").read()
    except:h="<html><textarea>{{content}}</textarea></html>"
    h=h.replace("{{id}}",i).replace("{{type}}",pr.get("t","")).replace("{{file}}",m).replace("{{content}}",c)
    return Response(h,mimetype="text/html")

@app.route("/s/<i>/",defaults={"sp":""})
@app.route("/s/<i>/<path:sp>")
def srv(i,sp):
    d=L();pr=d["p"].get(i)
    if not pr:return"Not found",404
    a=P/i
    if pr.get("t")=="st":
        if sp:return send_from_directory(str(a),sp)
        for mf in["i.html","index.html","index.htm"]:
            if(a/mf).is_file():return(a/mf).read_text()
        return"<h1>Welcome</h1>"
    if i in APPS and APPS[i].get("s"):
        try:return req.get(f"http://127.0.0.1:{APPS[i]['pt']}/{sp}",timeout=10).text
        except:return"<h1>Starting...</h1>"
    return"<h1>Stopped</h1>"

app.route("/api/p")(routes.list_projects)
app.route("/api/p",methods=["POST"])(routes.create_project)
app.route("/api/p/<i>",methods=["DELETE"])(routes.delete_project)
app.route("/api/p/<i>/tg",methods=["POST"])(routes.toggle_project)
app.route("/api/p/<i>/dp",methods=["POST"])(routes.deploy_project)
app.route("/api/p/<i>/f/<path:fp>")(routes.get_file)
app.route("/api/p/<i>/f/<path:fp>",methods=["PUT"])(routes.save_file)
app.route("/health")(routes.health)