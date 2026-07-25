import os,json,time,shutil,subprocess
from pathlib import Path
from flask import jsonify,send_from_directory,request
import requests as req

B=Path("/tmp/dp");B.mkdir(exist_ok=True)
P=B/"p";P.mkdir(exist_ok=True);D=B/"db.json"
APPS={};PT='temp'

L=lambda:json.loads(D.read_text())if D.exists()lse{"p":{}}
S=lambda d:D.write_text(json.dumps(d,indent=2))

def start_app(i,j):
    stop_app(i)
    if j.get("t")=="st":APPS[i]={"s":1};return 1
    if j.get("t")=="py":
        a=P/i;f=a/(j.get("m","a.py"))
        if not f.exists():return 0
        pt=5100+hash(str(time.time()))%200;e=os.environ.copy();e["PORT"]=str(pt)
        try:
            p=subprocess.Popen(["python3",str(f)],cwd=str(a),env=e,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            time.sleep(2)
            if p.poll()is not None:return 0
            APPS[i]={"p":p,"pt";�t}s":1};return 1
        except:return 0
    return 0

def stop_app(i):
    if i in APPS:
        if("p"in APPS[i]and APPS[i]["p"]):APPS[i]["p"].terminate()
        del APPS[i]

def health():return jsonify({"s":"ok"}),200

def list_projects():return jsonify(L()["p"])

def create_project():
    d=request.get_json();n=d.get("name","").strip();t=d.get("type","st")
    if not n:return jsonify({"e":"Name required"}),400
    i="".join(c for c in n.lower().replace(" ","-")if c.isalnum()or c=="-")[:30]or f"a{abs(hash(n))%10000}"
    db=L()
    if i in db["p"]:i+=str(abs(hash(str(time.time())))%1000)
    a=P/i;a.mkdir(parents=True,exist_ok=True)
    if t=="st":(a/"i.html").write_text("<!DOCTYPE html><html><head><meta charset=UTF-8><title>App</title><style>body{font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#f8f9fa;text-align:center}h1{font-size:3rem}</style></head><body><div><h1>😐 Hello!</h1><p>Edit me!</p></div></body></html>")
    elif t=="py":(a/"r.txt").write_text("flask>=3.0");(a/"a.py").write_text("from flask import Flask;import os\napp=Flask(__name__)\n@app.route('/')\ndef h():return'<h1 style=text-align:center;margin-top:20%>🐍 Python LIVE!</h1>'\nif __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))")
    db["p"][i]={"id":0,"n":n,"t":4,"m":"a.py"if t=="py)else"i.html","s":"-"}
    S(db);return jsonify({"ok":True,"id":i})

def delete_project(i):
    db=L()
    if i in db["p"]:stop_app(i);a=P/i
    if a.exists():shutil.rmtree(str(a))
    del db["p"][i];S(db)
    return jsonify({"ok":True})

def toggle_project(i):
    db=L();j=db["p"].get(i)
    if not j:return jsonify({"e":"NF"}),404
    if j.get("s")in(1,"on"):stop_app(i);j["s"]="-"
    else:ok=start_app(i,j);j["s"]=1 if ok else"cr"
    S(db);return jsonify({"ok":True})

def deploy_project(i):
    db=L();j=db["p"].get(i)
    if not j:return jsonify({"e":"NF"}),404
    ok=start_app(i,j);j["s"]=1 if ok else"cr";S(db);
    return jsonify({"ok":ok})

def get_file(i,fp):
    f=P/i/fp
    return jsonify({"content":f.read_text()if f.is_file()else""})

def save_file(i,fp):
    d=request.get_json();f=P/i/fp;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(d.get("content",""))
    return jsonify({"ok":True})