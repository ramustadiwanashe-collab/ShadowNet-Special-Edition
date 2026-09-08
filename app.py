from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, time, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'shadownet.db')
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')

LANGUAGES = {
    'python': {
        'name':'Python','icon':'🐍','description':'Readable, versatile and widely used for automation, web, data and AI.',
        'topics': [
            ('Introduction to Python','Python is a high-level language focused on readable syntax and rapid development.',
             'Python uses indentation to group code. You can build scripts, web apps, APIs, automation tools and data programs.',
             'print("Hello, ShadowNet!")','Hello, ShadowNet!','Use meaningful variable names and keep functions small.'),
            ('Variables and Data Types','Variables store references to values.',
             'Common built-in types include int, float, str, bool, list, tuple, set and dict. Python determines the type at runtime.',
             'name = "ShadowNet"\nage = 18\nprint(name, age)','ShadowNet 18','Check your data types with type(value) before debugging unexpected behavior.'),
            ('Operators','Operators let you calculate, compare and combine values.',
             'Arithmetic handles calculations. Comparison operators return booleans. Logical operators combine conditions.',
             'x = 10\nif x > 5 and x < 20:\n    print("valid")','valid','Use parentheses when an expression becomes difficult to read.'),
            ('Control Flow','Control flow decides which code runs and how often.',
             'Use if, elif and else for branching. Use for and while loops for repetition.',
             'for n in range(3):\n    print(n)','0\n1\n2','Avoid deeply nested conditions. Extract complex logic into functions.'),
            ('Functions','Functions package reusable behavior.',
             'Use def to declare a function. Parameters accept input, and return sends a value to the caller.',
             'def add(a, b):\n    return a + b\n\nprint(add(2, 3))','5','Prefer functions that do one clear job.'),
            ('Lists','Lists store ordered, mutable collections.',
             'You can index, slice, append, remove and iterate through list elements.',
             'langs = ["Python", "HTML", "C++"]\nprint(langs[0])','Python','Use list comprehensions when they improve clarity, not when they make code harder to scan.')
        ]
    },
    'html': {
        'name':'HTML','icon':'🌐','description':'The structure and meaning of web pages.',
        'topics': [
            ('HTML Fundamentals','HTML defines the structure of a document with elements and attributes.',
             'Use semantic elements such as header, nav, main, section, article and footer to describe page structure.',
             '<h1>ShadowNet</h1>\n<p>Learn to code.</p>','ShadowNet / Learn to code.','Prefer semantic HTML instead of generic div elements.'),
            ('Links and Images','Links connect documents and images add visual content.',
             'Use anchor elements for navigation and img elements with meaningful alt text.',
             '<a href="/courses">Courses</a>\n<img src="logo.png" alt="ShadowNet logo">','A link and an accessible image','Write alt text that describes the purpose of the image.'),
            ('Forms','Forms collect user input.',
             'Labels improve accessibility. Input types provide browser-level validation and better mobile keyboards.',
             '<label>Email</label>\n<input type="email" name="email" required>','Email input','Always validate important data again on the server.')
        ]
    },
    'cpp': {
        'name':'C++','icon':'⚙️','description':'A compiled language used for systems, performance and applications.',
        'topics': [
            ('C++ Fundamentals','C++ programs commonly start execution from main().',
             'Include required headers, define main, then compile and run the resulting binary.',
             '#include <iostream>\nint main(){\n std::cout << "Hello ShadowNet";\n}','Hello ShadowNet','Compile with warnings enabled, such as -Wall -Wextra when using GCC or Clang.'),
            ('Variables and Types','C++ uses statically typed variables.',
             'Declare a type before the variable. Common types include int, double, char, bool and std::string.',
             'int age = 18;\ndouble score = 95.5;','Two typed variables','Choose the narrowest type that safely represents your data.'),
            ('Control Flow','Conditions and loops control execution.',
             'Use if and switch for branching. Use for and while for repetition.',
             'for(int i=0;i<3;i++){\n std::cout << i << "\\n";\n}','0\n1\n2','Keep ownership and lifetime rules in mind when working with dynamic memory.')
        ]
    },
    'javascript': {
        'name':'JavaScript','icon':'🟨','description':'The language that powers interactive web applications.',
        'topics': [
            ('JavaScript Basics','JavaScript executes logic in browsers and runtimes such as Node.js.',
             'Use const by default, let when reassignment is required, and avoid var in modern code.',
             'const greeting = "Hello";\nconsole.log(greeting);','Hello','Prefer const unless a value must change.'),
            ('Functions','Functions encapsulate reusable behavior.',
             'JavaScript supports function declarations, expressions and arrow functions.',
             'const add = (a,b) => a + b;\nconsole.log(add(2,3));','5','Keep callbacks small and name important business logic.'),
            ('DOM Basics','The Document Object Model lets JavaScript interact with a page.',
             'Select elements, update content and attach event listeners to create interactive interfaces.',
             'document.querySelector("button")\n  .addEventListener("click", () => alert("Hi"));','Browser alert: Hi','Check that DOM elements exist before accessing them.')
        ]
    },
    'css': {
        'name':'CSS','icon':'🎨','description':'Styling, layout, animation and responsive design.',
        'topics': [
            ('CSS Fundamentals','CSS controls presentation of HTML.',
             'Selectors target elements. Properties define visual behavior. Values control each property.',
             'body { background: #050816; color: white; }','Dark page background','Prefer classes for reusable styles and keep specificity manageable.'),
            ('Flexbox','Flexbox simplifies one-dimensional layouts.',
             'Use display:flex with gap, justify-content and align-items to position items cleanly.',
             '.row { display:flex; gap:16px; align-items:center; }','Horizontal row of items','Use gap instead of manual margins for consistent spacing.'),
            ('Responsive Design','Responsive layouts adapt to different screen sizes.',
             'Use flexible sizing, media queries and mobile-first rules to support phones, tablets and desktops.',
             '@media (max-width: 700px) { .sidebar { display:none; } }','Sidebar hidden on small screens','Test at multiple viewport widths, not only on desktop.')
        ]
    },
    'java': {
        'name':'Java','icon':'☕','description':'A strongly typed language used in enterprise, backend and Android ecosystems.',
        'topics': [
            ('Java Basics','Java applications are compiled to bytecode and executed by the JVM.',
             'A basic program declares a class and a main method.',
             'public class Main {\n public static void main(String[] args) {\n  System.out.println("Hello");\n }\n}','Hello','Use clear class responsibilities and avoid huge methods.'),
            ('Classes and Objects','Classes define object state and behavior.',
             'Fields store state. Methods expose behavior. Constructors initialize objects.',
             'class User { String name; User(String n){ name=n; } }','A User object with a name','Keep fields encapsulated and expose behavior through methods.')
        ]
    },
    'csharp': {
        'name':'C#','icon':'🟪','description':'Modern language for .NET applications, APIs, desktop and game development.',
        'topics': [
            ('C# Fundamentals','C# is a modern statically typed language in the .NET ecosystem.',
             'Console applications commonly start in Program and call Console.WriteLine.',
             'Console.WriteLine("Hello ShadowNet");','Hello ShadowNet','Use nullable reference types in modern .NET projects.'),
            ('Classes','Classes group data and behavior.',
             'Use properties for controlled access to object state and methods for behavior.',
             'public class User { public string Name { get; set; } }','A User class','Keep domain logic near the data it operates on.')
        ]
    },
    'sql': {
        'name':'SQL','icon':'🗄️','description':'Query and manage relational data.',
        'topics': [
            ('SELECT Queries','SELECT retrieves data from relational tables.',
             'Use SELECT to specify columns and FROM to specify the source table. Add WHERE for filtering.',
             'SELECT name, email FROM users WHERE active = 1;','Rows containing active users','Select only the columns you need when practical.'),
            ('INSERT and UPDATE','Write data with INSERT and modify it with UPDATE.',
             'Always control UPDATE scope with an appropriate WHERE clause.',
             'UPDATE users SET active = 1 WHERE id = 7;','One user updated','Test UPDATE and DELETE statements with a SELECT first.')
        ]
    },
    'bash': {
        'name':'Bash','icon':'🐚','description':'Shell scripting for Linux and Unix automation.',
        'topics': [
            ('Command Line Basics','Bash lets you control a system through commands.',
             'Use commands such as pwd, ls, cd, mkdir, cp and mv to navigate and manage files.',
             'pwd\nls -la\nmkdir projects','Working directory, file listing and a new folder','Quote paths that contain spaces.'),
            ('Variables and Scripts','Variables make shell scripts reusable.',
             'Assign values without spaces around =. Read variables with $.',
             'name="ShadowNet"\necho "Hello $name"','Hello ShadowNet','Use set -euo pipefail for stricter scripts when appropriate.')
        ]
    },
    'linux': {
        'name':'Linux','icon':'🐧','description':'Operating system fundamentals, commands and administration.',
        'topics': [
            ('Linux Fundamentals','Linux provides a Unix-like environment used across servers, desktops and embedded systems.',
             'Learn the filesystem hierarchy, users, permissions, processes and package management before moving to administration.',
             'whoami\nuname -a\nls /home','Current user, system information and home directory listing','Understand permissions before changing files owned by another user.'),
            ('Permissions','Linux permissions control who can read, write or execute a file.',
             'Permissions apply to owner, group and others. chmod changes permission bits.',
             'chmod u+x script.sh\n./script.sh','Executable script','Use least privilege. Avoid chmod 777 unless you have a specific reason.')
        ]
    }
}


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = db()
    con.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, premium INTEGER DEFAULT 0, xp INTEGER DEFAULT 0, streak INTEGER DEFAULT 0, last_active TEXT)''')
    cols = {r['name'] for r in con.execute('PRAGMA table_info(users)').fetchall()}
    if 'xp' not in cols: con.execute('ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0')
    if 'streak' not in cols: con.execute('ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0')
    if 'last_active' not in cols: con.execute('ALTER TABLE users ADD COLUMN last_active TEXT')
    con.execute('''CREATE TABLE IF NOT EXISTS progress (user_id INTEGER, language TEXT, topic_index INTEGER, completed INTEGER DEFAULT 0, completed_at TEXT, PRIMARY KEY(user_id, language, topic_index))''')
    pcols = {r['name'] for r in con.execute('PRAGMA table_info(progress)').fetchall()}
    if 'completed_at' not in pcols: con.execute('ALTER TABLE progress ADD COLUMN completed_at TEXT')
    con.execute('''CREATE TABLE IF NOT EXISTS achievements (user_id INTEGER, key TEXT, title TEXT, awarded_at TEXT, PRIMARY KEY(user_id, key))''')
    con.commit(); con.close()

init_db()

@app.context_processor
def inject():
    return {'current_user': session.get('user'), 'languages': LANGUAGES}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name=request.form.get('name','').strip(); username=request.form.get('username','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        if not name or not username or not email or len(password)<8:
            return render_template('auth.html', mode='signup', error='Complete all fields. Password must contain at least 8 characters.')
        con=db()
        try:
            con.execute('INSERT INTO users(name,username,email,password) VALUES(?,?,?,?)',(name,username,email,generate_password_hash(password))); con.commit()
        except sqlite3.IntegrityError:
            con.close(); return render_template('auth.html', mode='signup', error='Username or email already exists.')
        row=con.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone(); con.close()
        session['user']={'id':row['id'],'name':row['name'],'username':row['username'],'premium':bool(row['premium'])}
        session['welcome_until']=time.time()+5
        return redirect(url_for('welcome'))
    return render_template('auth.html', mode='signup')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        identity=request.form.get('identity','').strip(); password=request.form.get('password','')
        con=db(); row=con.execute('SELECT * FROM users WHERE username=? OR email=?',(identity,identity.lower())).fetchone(); con.close()
        if not row or not check_password_hash(row['password'], password):
            return render_template('auth.html', mode='login', error='Invalid username/email or password.')
        session['user']={'id':row['id'],'name':row['name'],'username':row['username'],'premium':bool(row['premium'])}
        session['welcome_until']=time.time()+5
        return redirect(url_for('welcome'))
    return render_template('auth.html', mode='login')

@app.route('/welcome')
def welcome():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('welcome.html', seconds=5)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    con=db()
    row=con.execute('SELECT xp, streak, last_active FROM users WHERE id=?',(session['user']['id'],)).fetchone()
    completed=con.execute('SELECT COUNT(*) c FROM progress WHERE user_id=? AND completed=1',(session['user']['id'],)).fetchone()['c']
    achievements=con.execute('SELECT title FROM achievements WHERE user_id=? ORDER BY awarded_at DESC',(session['user']['id'],)).fetchall()
    con.close()
    stats={'xp':row['xp'] or 0,'streak':row['streak'] or 0,'completed':completed,'achievements':[a['title'] for a in achievements]}
    return render_template('dashboard.html', stats=stats)

@app.route('/language/<language>')
def language(language):
    if 'user' not in session: return redirect(url_for('login'))
    course=LANGUAGES.get(language)
    if not course: return 'Language not found',404
    return render_template('language.html', language_key=language, course=course)

@app.route('/lesson/<language>/<int:index>')
def lesson(language,index):
    if 'user' not in session: return redirect(url_for('login'))
    course=LANGUAGES.get(language)
    if not course or index<0 or index>=len(course['topics']): return 'Topic not found',404
    topic=course['topics'][index]
    locked = (index >= 4) and not session['user']['premium']
    return render_template('lesson.html', language_key=language, course=course, index=index, topic=topic, locked=locked)

@app.post('/complete/<language>/<int:index>')
def complete(language,index):
    if 'user' not in session: return jsonify({'ok':False}),401
    course=LANGUAGES.get(language)
    if not course or index < 0 or index >= len(course['topics']): return jsonify({'ok':False,'error':'Invalid topic'}),400
    user_id=session['user']['id']
    now=datetime.date.today()
    today=now.isoformat()
    con=db()
    was_done=con.execute('SELECT completed FROM progress WHERE user_id=? AND language=? AND topic_index=?',(user_id,language,index)).fetchone()
    added_xp=0 if was_done and was_done['completed'] else 25
    con.execute('INSERT OR REPLACE INTO progress(user_id,language,topic_index,completed,completed_at) VALUES(?,?,?,?,?)',(user_id,language,index,1,today))
    row=con.execute('SELECT xp,streak,last_active FROM users WHERE id=?',(user_id,)).fetchone()
    streak=row['streak'] or 0
    last=row['last_active']
    if last != today:
        if last:
            try:
                prev=datetime.date.fromisoformat(last)
                streak=streak+1 if (now-prev).days==1 else 1
            except ValueError:
                streak=1
        else:
            streak=1
        con.execute('UPDATE users SET xp=xp+?, streak=?, last_active=? WHERE id=?',(added_xp,streak,today,user_id))
    else:
        con.execute('UPDATE users SET xp=xp+? WHERE id=?',(added_xp,user_id))
    total=con.execute('SELECT COUNT(*) c FROM progress WHERE user_id=? AND completed=1',(user_id,)).fetchone()['c']
    awards=[]
    checks=[('first-topic','First Code Step',total>=1),('ten-topics','10 Topic Streak',total>=10),('seven-day','7 Day Streak',streak>=7)]
    for key,title,ok in checks:
        if ok and not con.execute('SELECT 1 FROM achievements WHERE user_id=? AND key=?',(user_id,key)).fetchone():
            con.execute('INSERT INTO achievements(user_id,key,title,awarded_at) VALUES(?,?,?,?)',(user_id,key,title,today)); awards.append(title)
    con.commit(); con.close()
    return jsonify({'ok':True,'added_xp':added_xp,'streak':streak,'total_completed':total,'awards':awards})

@app.post('/api/challenge')
def challenge():
    if 'user' not in session: return jsonify({'ok':False}),401
    payload=request.get_json(silent=True) or {}
    lang=payload.get('language'); idx=int(payload.get('index',0))
    course=LANGUAGES.get(lang)
    if not course or idx<0 or idx>=len(course['topics']): return jsonify({'ok':False}),400
    title,summary,notes,code,output,tip=course['topics'][idx]
    templates={
        'python':f'Create a function related to: {title}. Test it with at least two inputs.',
        'javascript':f'Write a small JavaScript example that demonstrates: {title}.',
        'html':f'Build a small accessible HTML example that demonstrates: {title}.',
        'css':f'Create a responsive CSS snippet that demonstrates: {title}.',
        'cpp':f'Write a C++ example that demonstrates: {title}. Compile it with warnings enabled.',
        'java':f'Write a Java example that demonstrates: {title}.',
        'csharp':f'Write a C# example that demonstrates: {title}.',
        'sql':f'Write a safe SQL query that demonstrates: {title}.',
        'bash':f'Write a Bash command or script that demonstrates: {title}.',
        'linux':f'Use a Linux command sequence that demonstrates: {title}.'
    }
    task=templates.get(lang,f'Create a short practice task for: {title}.')
    return jsonify({'ok':True,'challenge':task,'xp':25,'topic':title})

@app.get('/api/ai')
def ai():
    q=request.args.get('q','').strip()
    if not q: return jsonify({'answer':'Ask me a programming question.'})
    return jsonify({'answer':f'ShadowAI demo: I received “{q}”. Connect your AI provider in the backend environment to enable live answers.'})

@app.route('/privacy')
def privacy(): return render_template('legal.html', title='Privacy Policy', body='ShadowNet stores account information required to authenticate users and track learning progress. Passwords are stored as secure hashes. Production deployments should add data retention controls, encryption at rest, access logging and a formal data deletion workflow.')

@app.route('/terms')
def terms(): return render_template('legal.html', title='Terms & Conditions', body='ShadowNet is an educational platform. You must provide accurate account information, keep your credentials private and use the platform lawfully. Premium access is governed by the payment and refund terms presented at checkout.')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT','5000')), debug=os.getenv('FLASK_DEBUG','0')=='1')
