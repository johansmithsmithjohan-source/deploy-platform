"""Deploy Platform"""
import os,json,time,shutil,subprocess
from pathlib import Path
from flask import Flask,request,jsonify,Response,send_from_directory
import requests as req

B=Path("/tmp/dp");B.mkdir(exist_ok=True)
P=B/"p";P.mkdir(exist_ok=True);D=B/"db.json"
APPS={}
L=lambda:json.loads(D.read_text())if D.exists()else{"p":{}}
S=lambda d:D.write_text(json.dumps(d,indent=2))

def sta(i,j):
    stp(i)
    if j.get("t")=="st":APPS[i]={"s":1};return 1
    if j.get("t")=="py":
        a=P/i;f=a/(j.get("m","a.py"))
        if not f.exists():return 0
        pt=5100+hash(str(time.time()))%200;e=os.environ.copy();e["PORT"]=str(pt)
        try:
            p=subprocess.Popen(["python3",str(f)],cwd=str(a),env=e,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            time.sleep(2)
            if p.poll()is not None:return 0
            APPS[i]={"p":p,"pt":pt,"s":1};return 1
        except:return 0
    return 0

def stp(i):
    if i in APPS:
        if"p"in APPS[i]and APPS[i]["p"]:APPS[i]["p"].terminate()
        del APPS[i]

app=Flask(__name__)

@app.route("/health")
def hh():return jsonify({"s":"ok"}),200

@app.route("/")
def home():
    d=L();cs=""
    for i,j in d["p"].items():
        s="on"if j.get("s")in(1,"on")else"cr"if j.get("s")=="cr"else"-"
        cs+=f'<div class=c><b>{j.get("n",i)}</b> [{s}] {j.get("t","st").upper()} <a href=/e/{i}>Edit</a> <a href=/s/{i}/>Visit</a> <button onclick=fetch("/api/p/{i}/tg",{method:"POST"}).then(()=>location.reload())>Toggle</button> <button onclick=fetch("/api/p/{i}",{method:"DELETE"}).then(()=>location.reload())>Del</button></div>'
    if not d["p"]:cs="<p>No apps yet. Create one!</p>"
    try:h=open("t/home.html").read()
    except:h="<html><h1>Deploy Platform</h1><div>{cards}</div></html>"
    h=h.replace("{{cards}}",cs)
    return Response(h,mimetype="text/html")

@app.route("/e/<i>")
def edit(i):
    d=L();j=d["p"].get(i)
    if not j:return"Not found",404
    m=j.get("m","a.py"if j.get("t")=="py"else"i.html");f=P/i/m;c=f.read_text()if f.exists()”se""
    try:h=open("t/edit.html").read()
    except:h="<html><textarea>{content}</textarea></html>"
    h=h.replace("{{id}}",i).replace("{{type}}",j.get("t","")).replace("{{file}}",m).replace("{{content}}",c)
    return Response(h,mimetype="text/html")

@app.route("/s/<i>/",defaults={"sp":""})
@app.route("/s/<i>/<path:sp>")
def srv(i,sp):
    d=L();j=d["p"].get(i)
    if not j:return"Not found",404
    a=P/i
    if j.get("t")=="st":
        if sp:return send_from_directory(str(a),sp)if(a/sp).is_file()else"Not Found",404
        for mf in["i.html","index.html","index.htm"]:
            if(a/mf).is_file():return(a/mf).read_text()
        return"<h1>Welcome</h1>"
    if i in APPS and APPS[i].get("s"):
        try:return req.get(f"http://127.0.0.1:{APPS[i]['pt']}/{sp}",timeout=10).text
        except:return"<h1>Starting...</h1>"
    return"<h1>Stopped</h1>"

@app.route("/api/p")
def al():return jsonify(L()["p"])

@app.route("/api/p",methods=["POST"])
def ac():
    d=request.get_json();n=d.get("name","").strip();t=d.get("type","st")
    if not n:return jsonify({"e":"Name required"}),400
    i="".join(c for c in n.lower().replace(" ","-")if c.isalnum()or c=="-")[:30]or f"a{abs(hash(n))%10000}"
    db=L()
    if i in db["p"]:i+=str(abs(hash(str(time.time())))%1000)
    a=P/i;a.mkdir(parents=True,exist_ok=True)
    if t=="st":(a/"i.html").write_text("<!DOCTYPE html><html><head><meta charset=UTF-8><title>App</title><style>body{font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#f8f9fa;text-align:center}h1{font-size:3rem}</style></head><body><div><h1>Hello!</h1><p>Edit me!</p></div></body></html>")
    elif t=="py":(a/"r.txt").write_text("flask>=3.0");(a/"a.py").write_text("from flask import Flask;import os\napp=Flask(__name__)\n@app.route('/')\ndef h():return'<h1 style=text-align:center;margin-top:20%>Python LIVE!</h1>'\nif __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))")
    db["p"][i]={"n":n,"t":4,"m":"a.py"if t=="py)else"i.html","s":"-"}
    S(db);return jsonify({"ok":True,"id":i})

@app.route("/api/p/<i>",methods=["DELETE"])
def ad(i):
    db=L()
    if i in db["p"]:stp(i);a=P/i
    if a.exists():shutil.rmtree(str(a))
    del db["p"][i];S(db)
    return jsonify({"ok":True})

@app.route("/api/p/<i>/tg",methods=["POST"])
def at(i):
    db=L();j=db["p"].get(i)
    if not j:return jsonify({"e":"NF"}),404
    if j.get("s")in(1,"on"):stp(i);j["s"]="-"
    else:ok=sta(i,j);j["s"]="on"if ok else"cr"
    S(db);return jsonify({"ok":True})

@app.route("/api/p/<i>/dp",methods=["POST"])
def ap(i):
    db=L();j=db["p"].get(i)
    if not j:return jsonify({"e":"NF"}),404
    ok=sta(i,j);j["s"]="on"if ok else"cr";S(db);
    return jsonify({"ok":ok})

@app.route("/api/p/<i>/f/<path:fp>")
def gf(i,fp):f=P/i/fp;return jsonify({"content":f.read_text()if f.is_file()else""})

@app.route("/api/p/<i>/f/<path:fp>",methods=["PUT"])
def sf(i,fp):
    d=request.get_json();f=P/i/fp;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(d.get("content",""))
    return jsonify({"ok":True})
