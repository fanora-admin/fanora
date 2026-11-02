# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request, redirect, session
import os, json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fanora_v15_color"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)

ADMINS = ["Admin"]
posts=[]; profiles={}; follows={}; users={}; blocks={}; messages=[]; notifications={}

def time_ago(s):
    try:
        dt=datetime.fromisoformat(s)
        diff=int((datetime.now()-dt).total_seconds())
        if diff<60: return "şimdi"
        if diff<3600: return f"{diff//60} dk"
        if diff<86400: return f"{diff//3600} saat"
        return f"{diff//86400} gün"
    except: return ""

def is_admin(u): return u in ADMINS
def get_followers(u): return sum(1 for x in follows.values() if u in x)
def get_following(u): return len(follows.get(u, set()))
def add_notif(to_user, text):
    if to_user not in notifications: notifications[to_user]=[]
    notifications[to_user].insert(0, {"text":text, "created_at":datetime.now().isoformat(), "read":False})

def save_all():
    with open("data/profiles.json","w",encoding="utf-8") as f:
        json.dump({k:{"avatar":v.avatar,"banner":v.banner,"bio":v.bio,"color":v.color,"effect":getattr(v,'effect','normal'),"username":v.username} for k,v in profiles.items()},f,ensure_ascii=False)
    with open("data/follows.json","w",encoding="utf-8") as f: json.dump({k:list(v) for k,v in follows.items()},f,ensure_ascii=False)
    with open("data/posts.json","w",encoding="utf-8") as f: json.dump([{**p,"likes":list(p["likes"])} for p in posts],f,ensure_ascii=False)
    with open("data/users.json","w",encoding="utf-8") as f: json.dump(users,f,ensure_ascii=False)
    with open("data/messages.json","w",encoding="utf-8") as f: json.dump(messages,f,ensure_ascii=False)
    with open("data/notifs.json","w",encoding="utf-8") as f: json.dump(notifications,f,ensure_ascii=False)

def load_all():
    global posts, users, messages, notifications
    if os.path.exists("data/profiles.json"):
        try:
            with open("data/profiles.json","r",encoding="utf-8") as f:
                for k,v in json.load(f).items():
                    profiles[k]=type('obj',(object,),{'avatar':v.get("avatar"),'banner':v.get("banner"),'bio':v.get("bio",""),'color':v.get("color","#a855f7"),'effect':v.get("effect","normal"),'username':v.get("username",k)})()
        except: pass
    if os.path.exists("data/follows.json"):
        try:
            with open("data/follows.json","r",encoding="utf-8") as f:
                for k,v in json.load(f).items(): follows[k]=set(v)
        except: pass
    if os.path.exists("data/posts.json"):
        try:
            with open("data/posts.json","r",encoding="utf-8") as f:
                for p in json.load(f): p["likes"]=set(p.get("likes",[])); posts.append(p)
        except: pass
    if os.path.exists("data/users.json"):
        try:
            with open("data/users.json","r",encoding="utf-8") as f: users.update(json.load(f))
        except: pass
    if os.path.exists("data/messages.json"):
        try:
            with open("data/messages.json","r",encoding="utf-8") as f: messages=json.load(f)
        except: pass
    if os.path.exists("data/notifs.json"):
        try:
            with open("data/notifs.json","r",encoding="utf-8") as f: notifications=json.load(f)
        except: pass
    if "Admin" not in users: users["Admin"]="Admin"
    if "Admin" not in profiles: profiles["Admin"]=type('obj',(object,),{'avatar':None,'banner':None,'bio':"Fanora kurucusu",'color':"#a855f7",'effect':"glow",'username':"Admin"})()
    if "Admin" not in follows: follows["Admin"]=set()
    save_all()
load_all()

BASE = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{font-family:Inter,sans-serif;box-sizing:border-box}
body{background:#0a0a0f;color:white;margin:0}
.nav{background:#14141c;border:1px solid #222;padding:12px 16px;border-radius:14px;display:flex;justify-content:space-between;align-items:center;max-width:1100px;margin:10px auto;position:sticky;top:10px;z-index:20}
.logo{font-weight:900;color:white;text-decoration:none}
.btn{background:#a855f7;border:none;padding:10px 16px;border-radius:10px;color:white;font-weight:700;cursor:pointer;width:100%}
input,textarea,select{width:100%;padding:12px;margin:6px 0;border-radius:10px;border:1px solid #222;background:#0f0f13;color:white;font-size:13px}
textarea{resize:none !important; height:80px;}
.card{background:#14141c;border:1px solid #222;padding:16px;border-radius:14px;margin-bottom:14px}
.post{background:#14141c;padding:12px;border-radius:14px;margin:10px 0;border:1px solid #222}
.post-img{width:100%;border-radius:12px;margin-top:8px;max-height:380px;object-fit:cover}
.time{color:#666;font-size:11px}
.avatar{width:90px;height:90px;border-radius:50%;object-fit:cover;background:#222;box-shadow: 0 0 0 4px #0a0a0f;}
.avatar.mini{width:36px;height:36px;box-shadow:none}
.banner-box{width:100%;height:180px;border-radius:18px;overflow:hidden;background:linear-gradient(135deg,#a855f7,#222)}
.banner-box img{width:100%;height:100%;object-fit:cover}
.label{font-size:11px;color:#888;margin-top:10px;display:block;font-weight:700}
.admin-badge{background:#ff0000;color:white;font-size:10px;padding:2px 6px;border-radius:6px;margin-left:6px}
input[type="file"]{background:#1a1a1e !important;border:1px solid #000 !important;padding:8px !important;}
input[type="file"]::file-selector-button{background:#2d2d33 !important;color:#e0e0e0 !important;border:1px solid #000 !important;border-radius:8px !important;padding:6px 14px !important;margin-right:12px !important;cursor:pointer;}
input[type="color"]{height:50px;padding:4px;cursor:pointer}
.follow-stats{display:flex;gap:14px;margin-top:8px;color:#aaa;font-size:13px}
.follow-stats b{color:white}
.follow-stats span{cursor:pointer}
.action-row{display:flex;gap:10px;margin-top:10px}
.btn-follow{background:#2a2a30;border:1px solid #333;padding:8px 18px;border-radius:20px;color:white;font-weight:700;cursor:pointer;font-size:13px}
.btn-msg{background:#a855f7;border:none;padding:8px 18px;border-radius:20px;color:white;font-weight:700;cursor:pointer;font-size:13px}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(6px);display:none;justify-content:center;align-items:center;z-index:100;padding:16px}
.modal-bg.active{display:flex}
.modal-box{background:#18181f;border:1px solid #2a2a30;border-radius:18px;width:100%;max-width:420px;padding:18px}
.modal-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.modal-close{background:#222;border:none;color:white;width:32px;height:32px;border-radius:50%;cursor:pointer}
.notif-dot{width:8px;height:8px;background:red;border-radius:50%;display:inline-block;margin-left:4px}
.chat-bubble{padding:10px 14px;border-radius:18px;max-width:70%;font-size:13px;margin:6px 0}
.chat-bubble.me{background:#a855f7;color:white;margin-left:auto;border-bottom-right-radius:4px}
.chat-bubble.other{background:#222;color:white;margin-right:auto;border-bottom-left-radius:4px}
.tag{display:inline-block;background:#1e1e26;border:1px solid #333;padding:6px 12px;border-radius:20px;font-size:12px;margin:4px;color:#aaa;text-decoration:none}
.tag:hover{color:white;border-color:#a855f7}
/* İSİM EFEKTLERİ */
.name-glow{ text-shadow: 0 0 12px currentColor, 0 0 20px currentColor; }
.name-neon{ text-shadow: 0 0 5px #fff, 0 0 10px currentColor, 0 0 20px currentColor, 0 0 35px currentColor; font-weight:900; letter-spacing:0.5px; }
.name-shadow{ text-shadow: 4px 4px 0px #000, 0 0 12px currentColor; }
</style>
"""

MAIN = BASE + """
<div class="nav">
  <a href="/" class="logo">Fanora</a>
  <div style="display:flex;gap:14px;margin-left:auto;align-items:center">
    <a href="/" style="color:white;text-decoration:none;font-size:13px">Akış</a>
    <a href="/explore" style="color:#888;text-decoration:none;font-size:13px">Keşfet</a>
    <a href="/inbox" style="color:#888;text-decoration:none;font-size:13px">Mesajlar</a>
    <a href="/notifications" style="color:#888;text-decoration:none;font-size:13px">Bildirimler {% if unread %}<span class="notif-dot"></span>{% endif %}</a>
    <a href="/profile/{{session.user}}" style="color:#888;text-decoration:none;font-size:13px">Profil</a>
    <a href="/logout" style="color:#ff5555;text-decoration:none;font-size:13px">Çıkış</a>
  </div>
</div>

<div style="max-width:640px;margin:0 auto;padding:0 14px">
  {% if page=='home' %}
  <div class="card" style="display:flex;gap:10px;align-items:center">
    {% set me = profiles.get(session.user) %}
    <img class="avatar mini" src="/{{me.avatar if me and me.avatar else ''}}">
    <form method="POST" enctype="multipart/form-data" style="display:flex;gap:6px;flex:1;margin:0"><input name="fandom" placeholder="#etiket" style="width:90px;height:40px;margin:0"><input name="text" placeholder="Ne düşünüyorsun?" style="flex:1;height:40px;margin:0" required><label style="background:#222;padding:10px;border-radius:10px;cursor:pointer">📎<input type="file" name="image" accept="image/*" style="display:none"></label><button class="btn" style="width:90px;height:40px;margin:0">Paylaş</button></form>
  </div>
  {% endif %}

  {% if page=='explore' %}
    <div class="card"><b>Keşfet</b><div style="margin-top:10px">{% for t in tags %}<a href="/explore?tag={{t}}" class="tag">#{{t}}</a>{% endfor %}{% if not tags %}<span style="color:#666">Henüz etiket yok</span>{% endif %}</div></div>
    {% if current_tag %}<div class="card" style="background:#1e1e26">#{{current_tag}} - <a href="/explore" style="color:#a855f7">Temizle</a></div>{% endif %}
  {% endif %}

  {% if page=='profile' %}
    {% set pu = profiles.get(user) %}
    <div class="banner-box">{% if pu and pu.banner %}<img src="/{{pu.banner}}">{% endif %}</div>
    <div style="display:flex;gap:14px;margin-top:-45px;padding-left:20px;position:relative;z-index:5;align-items:flex-start">
      <img class="avatar" src="/{{pu.avatar if pu and pu.avatar else ''}}">
      <div style="margin-top:50px; background:rgba(10,10,15,0.92); padding:10px 14px; border-radius:12px; border:1px solid #222; min-width:180px;">
        <h3 style="margin:0; color:{{pu.color if pu else '#fff'}}" class="name-{{pu.effect if pu else 'normal'}}">{{pu.username if pu else user}} {% if is_admin(user) %}<span class="admin-badge">ADMIN</span>{% endif %}</h3>
        <p style="color:#888;font-size:12px;margin:4px 0">@{{user}}</p>
        <div class="follow-stats">
          <span onclick="openFollow('following','{{user}}')"><b>{{ get_following(user) }}</b> Takip</span>
          <span onclick="openFollow('followers','{{user}}')"><b>{{ get_followers(user) }}</b> Takipçi</span>
        </div>
        {% if session.user != user %}
        <div class="action-row">
          <a href="/follow/{{user}}" style="text-decoration:none"><button class="btn-follow">{% if user in follows.get(session.user, []) %}Takipten Çık{% else %}Takip Et{% endif %}</button></a>
          <a href="/chat/{{user}}" style="text-decoration:none"><button class="btn-msg">Mesaj</button></a>
        </div>
        {% endif %}
      </div>
    </div>
    <div class="card" style="margin-top:16px"><p style="color:#ccc;font-size:14px;margin:0">{{pu.bio if pu and pu.bio else 'Henüz biyografi yok.'}}</p></div>
    {% if session.user==user %}
    <div style="margin-bottom:14px">
      <button id="editToggle" onclick="toggleEdit()" style="background:#1e1e24; border:1px solid #2a2a30; padding:12px; border-radius:12px; color:white; font-weight:700; cursor:pointer; width:100%;">Profili Düzenle + İsim Rengi</button>
      <div id="editBox" style="display:none; margin-top:12px;"><div class="card"><form method="POST" enctype="multipart/form-data">
        <label class="label">GÖRÜNEN İSİM</label><input name="username_display" value="{{pu.username if pu else user}}">
        <label class="label">İSİM RENGİ</label><input type="color" name="name_color" value="{{pu.color if pu else '#a855f7'}}">
        <label class="label">İSİM EFEKTİ</label><select name="name_effect">
          <option value="normal" {% if pu and pu.effect=='normal' %}selected{% endif %}>Normal</option>
          <option value="glow" {% if pu and pu.effect=='glow' %}selected{% endif %}>Parıltı - Glow</option>
          <option value="neon" {% if pu and pu.effect=='neon' %}selected{% endif %}>Neon Işık</option>
          <option value="shadow" {% if pu and pu.effect=='shadow' %}selected{% endif %}>Gölgeli</option>
        </select>
        <label class="label">BİYOGRAFİ</label><textarea name="bio">{{pu.bio if pu else ''}}</textarea>
        <label class="label">PROFİL FOTOĞRAFI</label><input type="file" name="avatar" accept="image/*">
        <label class="label">BANNER</label><input type="file" name="banner" accept="image/*">
        <button class="btn" style="margin-top:16px">Kaydet</button>
      </form></div></div>
    </div>
    <script>function toggleEdit(){var b=document.getElementById('editBox'),t=document.getElementById('editToggle');if(b.style.display==='none'){b.style.display='block';t.innerText='Kapat ✕'}else{b.style.display='none';t.innerText='Profili Düzenle + İsim Rengi'}}</script>
    {% endif %}
  {% endif %}

  {% if page=='chat' %}
    <div class="card" style="display:flex;gap:10px;align-items:center"><a href="/profile/{{chat_user}}" style="text-decoration:none;color:white"><b>@{{chat_user}}</b></a></div>
    <div style="height:60vh;overflow-y:auto;padding:10px 0" id="chatBox">
      {% for m in chat_messages %}<div class="chat-bubble {{'me' if m.from==session.user else 'other'}}">{{m.text}}<div style="font-size:10px;opacity:0.6;margin-top:4px">{{ time_ago(m.created_at) }}</div></div>{% endfor %}
    </div>
    <form method="POST" action="/send_message/{{chat_user}}" style="display:flex;gap:8px;position:sticky;bottom:10px;background:#0a0a0f;padding:10px 0"><input name="text" placeholder="Mesaj yaz..." required style="flex:1;margin:0"><button class="btn" style="width:80px;margin:0">Gönder</button></form>
    <script>var cb=document.getElementById('chatBox');cb.scrollTop=cb.scrollHeight;</script>
  {% endif %}

  {% if page=='inbox' %}
    <div class="card"><b>Mesajlar</b></div>
    {% for u in inbox_users %}<a href="/chat/{{u}}" style="text-decoration:none"><div class="card" style="display:flex;gap:10px;align-items:center"><img class="avatar mini" src="/{{profiles.get(u).avatar if profiles.get(u) and profiles.get(u).avatar else ''}}"><b style="color:white;font-size:13px">@{{u}}</b><span style="margin-left:auto;color:#666;font-size:11px">→</span></div></a>{% endfor %}
    {% if not inbox_users %}<p style="color:#666;text-align:center">Henüz mesaj yok</p>{% endif %}
  {% endif %}

  {% if page=='notifications' %}
    <div class="card"><b>Bildirimler</b></div>
    {% for n in notifs %}<div class="card" style="font-size:13px">{{n.text}}<div class="time" style="margin-top:6px">{{ time_ago(n.created_at) }}</div></div>{% endfor %}
    {% if not notifs %}<p style="color:#666;text-align:center">Bildirim yok</p>{% endif %}
  {% endif %}

  {% for p in posts %}
    {% set pa = profiles.get(p.author) %}
    {% set global_i = all_posts.index(p) if p in all_posts else loop.index0 %}
    <div class="post"><div style="display:flex;gap:10px;align-items:center"><img class="avatar mini" src="/{{pa.avatar if pa and pa.avatar else ''}}"><b style="font-size:13px; color:{{pa.color if pa else '#fff'}}" class="name-{{pa.effect if pa else 'normal'}}"><a href="/profile/{{p.author}}" style="color:inherit;text-decoration:none">@{{pa.username if pa else p.author}}</a>{% if is_admin(p.author) %}<span class="admin-badge">ADMIN</span>{% endif %}</b><span class="time"> - {{ time_ago(p.created_at) }}</span></div><div style="margin:10px 0 0 46px;font-size:14px">{{p.text}} {% if p.fandom %}<a href="/explore?tag={{p.fandom}}" style="color:#a855f7;text-decoration:none;font-size:12px">#{{p.fandom}}</a>{% endif %}</div>{% if p.image %}<img src="/{{p.image}}" class="post-img" style="margin-left:46px;width:calc(100% - 46px)">{% endif %}<div style="margin:10px 0 0 46px;font-size:12px"><a href="/like/{{global_i}}?next={{request.path}}" style="color:#ff4d6d;text-decoration:none">❤️ {{p.likes|length}}</a> <a href="/delete/{{global_i}}" style="color:#555;text-decoration:none;margin-left:14px">Sil</a></div></div>
  {% endfor %}
</div>

<div id="followModal" class="modal-bg" onclick="if(event.target==this)closeFollow()"><div class="modal-box"><div class="modal-head"><b id="followTitle">Takipçiler</b><button class="modal-close" onclick="closeFollow()">✕</button></div><div id="followList"></div></div></div>
<script>
var followsData = {{ follows_json|safe }};
function openFollow(type, username){
  var listDiv=document.getElementById('followList');var title=document.getElementById('followTitle');listDiv.innerHTML='';
  if(type=='followers'){title.innerText=username+' - Takipçiler';var followers=[];for(var u in followsData){if(followsData[u].includes(username))followers.push(u);}if(followers.length==0)listDiv.innerHTML='<p style="color:#666">Kimse yok</p>';else followers.forEach(f=>{listDiv.innerHTML+='<div style="padding:8px 0;border-bottom:1px solid #222"><a href="/profile/'+f+'" style="color:white;text-decoration:none"><b>@'+f+'</b></a></div>';});}
  else{title.innerText=username+' - Takip';var following=followsData[username]||[];if(following.length==0)listDiv.innerHTML='<p style="color:#666">Kimse yok</p>';else following.forEach(f=>{listDiv.innerHTML+='<div style="padding:8px 0;border-bottom:1px solid #222"><a href="/profile/'+f+'" style="color:white;text-decoration:none"><b>@'+f+'</b></a></div>';});}
  document.getElementById('followModal').classList.add('active');
}
function closeFollow(){document.getElementById('followModal').classList.remove('active');}
</script>
"""

LOGIN_HTML = """<style>body{background:#0a0a0f;color:white;font-family:sans-serif}.card{background:#14141c;border:1px solid #222;padding:24px;border-radius:16px;max-width:400px;margin:60px auto}input{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:1px solid #222;background:#0f0f13;color:white}.btn{background:#a855f7;border:none;padding:12px;border-radius:10px;color:white;width:100%;font-weight:700;cursor:pointer}</style><div class="card"><h2 style="text-align:center">Fanora</h2><form method="POST"><input name="username" placeholder="Kullanıcı adı" required><input name="password" type="password" placeholder="Şifre" required><button class="btn">Giriş Yap</button></form>{% if error %}<p style="color:#ff5555">{{error}}</p>{% endif %}<a href="/register" style="color:#888;font-size:12px;display:block;text-align:center;margin-top:12px">Kayıt Ol</a></div>"""

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form.get("username","").strip(); p=request.form.get("password","").strip()
        if u in users: return render_template_string(LOGIN_HTML, error="Bu kullanıcı adı zaten var")
        users[u]=p; profiles[u]=type('obj',(object,),{'avatar':None,'banner':None,'bio':"",'color':"#a855f7",'effect':"normal",'username':u})(); follows[u]=set(); blocks[u]=set(); notifications[u]=[]; save_all(); session["user"]=u; return redirect("/")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form.get("username","").strip(); p=request.form.get("password","").strip()
        if u in users and users[u]==p: session["user"]=u; return redirect("/")
        return render_template_string(LOGIN_HTML, error="Hatalı")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/logout")
def logout(): session.pop("user",None); return redirect("/login")

@app.route("/", methods=["GET","POST"])
def home():
    if "user" not in session: return redirect("/login")
    me=session["user"]
    if request.method=="POST":
        fandom=request.form["fandom"].replace("#","").strip().lower(); text=request.form["text"]
        file=request.files.get("image"); fn=None
        if file and file.filename:
            f=secure_filename(f"{me}_{datetime.now().timestamp()}_{file.filename}"); path=os.path.join(app.config['UPLOAD_FOLDER'], f); file.save(path); fn=path
        posts.insert(0,{"fandom":fandom,"text":text,"author":me,"likes":set(),"image":fn,"comments":[],"created_at":datetime.now().isoformat()}); save_all()
    unread = any(not n.get("read",True) for n in notifications.get(me,[]))
    return render_template_string(MAIN, page="home", posts=posts, all_posts=posts, profiles=profiles, time_ago=time_ago, get_followers=get_followers, get_following=get_following, is_admin=is_admin, follows=follows, follows_json=json.dumps({k:list(v) for k,v in follows.items()}), unread=unread)

@app.route("/explore")
def explore():
    if "user" not in session: return redirect("/login")
    me=session["user"]
    tag=request.args.get("tag","").lower()
    all_tags=list(set(p["fandom"] for p in posts if p.get("fandom")))
    filtered=[p for p in posts if tag in p.get("fandom","").lower()] if tag else posts
    unread = any(not n.get("read",True) for n in notifications.get(me,[]))
    return render_template_string(MAIN, page="explore", posts=filtered, all_posts=posts, profiles=profiles, time_ago=time_ago, get_followers=get_followers, get_following=get_following, is_admin=is_admin, follows=follows, tags=all_tags, current_tag=tag, follows_json=json.dumps({k:list(v) for k,v in follows.items()}), unread=unread)

@app.route("/profile/<username>", methods=["GET","POST"])
def profile(username):
    if "user" not in session: return redirect("/login")
    me=session["user"]
    if request.method=="POST" and me==username:
        bio=request.form.get("bio",""); disp=request.form.get("username_display",username)
        name_color=request.form.get("name_color","#a855f7")
        name_effect=request.form.get("name_effect","normal")
        av_path=profiles[username].avatar if profiles.get(username) else None; bn_path=profiles[username].banner if profiles.get(username) else None
        av=request.files.get("avatar")
        if av and av.filename:
            f=secure_filename(f"avatar_{username}_{av.filename}"); path=os.path.join(app.config['UPLOAD_FOLDER'], f); av.save(path); av_path=path
        bn=request.files.get("banner")
        if bn and bn.filename:
            f=secure_filename(f"banner_{username}_{bn.filename}"); path=os.path.join(app.config['UPLOAD_FOLDER'], f); bn.save(path); bn_path=path
        profiles[username]=type('obj',(object,),{'avatar':av_path,'banner':bn_path,'bio':bio,'color':name_color,'effect':name_effect,'username':disp})()
        save_all()
    user_posts=[p for p in posts if p["author"]==username]
    unread = any(not n.get("read",True) for n in notifications.get(me,[]))
    return render_template_string(MAIN, page="profile", posts=user_posts, all_posts=posts, profiles=profiles, user=username, get_followers=get_followers, get_following=get_following, is_admin=is_admin, time_ago=time_ago, follows=follows, follows_json=json.dumps({k:list(v) for k,v in follows.items()}), unread=unread)

@app.route("/chat/<username>", methods=["GET"])
def chat(username):
    if "user" not in session: return redirect("/login")
    me=session["user"]
    chat_msgs=[m for m in messages if (m["from"]==me and m["to"]==username) or (m["from"]==username and m["to"]==me)]
    unread = any(not n.get("read",True) for n in notifications.get(me,[]))
    return render_template_string(MAIN, page="chat", posts=[], all_posts=posts, profiles=profiles, time_ago=time_ago, get_followers=get_followers, get_following=get_following, is_admin=is_admin, follows=follows, chat_user=username, chat_messages=chat_msgs, follows_json=json.dumps({k:list(v) for k,v in follows.items()}), unread=unread)

@app.route("/send_message/<to_user>", methods=["POST"])
def send_message(to_user):
    if "user" not in session: return redirect("/login")
    text=request.form.get("text","").strip()
    if text:
        messages.append({"from":session["user"],"to":to_user,"text":text,"created_at":datetime.now().isoformat()})
        add_notif(to_user, f"{session['user']} sana mesaj gönderdi: {text[:30]}")
        save_all()
    if request.referrer and "/chat/" in request.referrer: return redirect(f"/chat/{to_user}")
    return redirect(f"/profile/{to_user}")

@app.route("/inbox")
def inbox():
    if "user" not in session: return redirect("/login")
    me=session["user"]
    users_set=set()
    for m in messages:
        if m["to"]==me: users_set.add(m["from"])
        if m["from"]==me: users_set.add(m["to"])
    unread = any(not n.get("read",True) for n in notifications.get(me,[]))
    return render_template_string(MAIN, page="inbox", posts=[], all_posts=posts, profiles=profiles, time_ago=time_ago, get_followers=get_followers, get_following=get_following, is_admin=is_admin, follows=follows, inbox_users=list(users_set), follows_json=json.dumps({k:list(v) for k,v in follows.items()}), unread=unread)

@app.route("/notifications")
def notifs_page():
    if "user" not in session: return redirect("/login")
    me=session["user"]
    notifs=notifications.get(me,[])
    for n in notifs: n["read"]=True
    save_all()
    return render_template_string(MAIN, page="notifications", posts=[], all_posts=posts, profiles=profiles, time_ago=time_ago, get_followers=get_followers, get_following=get_following, is_admin=is_admin, follows=follows, notifs=notifs, follows_json=json.dumps({k:list(v) for k,v in follows.items()}), unread=False)

@app.route("/follow/<username>")
def follow_user(username):
    if "user" not in session: return redirect("/login")
    me=session["user"]
    if me not in follows: follows[me]=set()
    if username in follows[me]: follows[me].remove(username)
    else: 
        follows[me].add(username)
        add_notif(username, f"{me} seni takip etmeye başladı")
    save_all()
    return redirect(f"/profile/{username}")

@app.route("/like/<int:id>")
def like(id):
    if "user" not in session: return redirect("/login")
    if 0 <= id < len(posts):
        if session["user"] in posts[id]["likes"]: posts[id]["likes"].remove(session["user"])
        else: 
            posts[id]["likes"].add(session["user"])
            if posts[id]["author"]!=session["user"]:
                add_notif(posts[id]["author"], f"{session['user']} gönderini beğendi")
        save_all()
    return redirect(request.args.get("next","/"))

@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session: return redirect("/login")
    if 0 <= id < len(posts) and (posts[id]["author"]==session["user"] or is_admin(session["user"])): posts.pop(id); save_all()
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)