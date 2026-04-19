import http.server
import socketserver
import webbrowser
import os
import sys
import json
import subprocess
import shutil
from urllib import parse

PORT = int(os.environ.get('PORT', '8001'))
# The repository uses a sibling `docs` folder located next to this script's
# directory (project layout on your machine: ...\pythone_src\ and a sibling
# ...\docs\). Prefer the parent `docs` if present so the server serves the
# same folder you publish to GitHub Pages. Fallback to a local `docs` inside
# the script directory if needed.
_SCRIPT_DIR = os.path.dirname(__file__)
# Prefer the docs folder located next to the workspace parent directory.
_PARENT_DOCS = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', 'docs'))
_LOCAL_DOCS = os.path.join(_SCRIPT_DIR, 'docs')

# Choose ROOT_DIR: parent docs if exists, else local docs. Do not create new
# unexpected folders — log chosen path so it's easy to debug.
if os.path.isdir(_PARENT_DOCS):
    ROOT_DIR = _PARENT_DOCS
    print(f"[Server] Using parent docs: {ROOT_DIR}")
elif os.path.isdir(_LOCAL_DOCS):
    ROOT_DIR = _LOCAL_DOCS
    print(f"[Server] Using local docs: {ROOT_DIR}")
else:
    # If neither exists, default to parent docs (will be created when needed).
    ROOT_DIR = _PARENT_DOCS
    print(f"[Server] Neither parent nor local docs exist. Will create: {ROOT_DIR}")

USERS_FILE = os.path.join(ROOT_DIR, 'data', 'users.json')

def ensure_site():
    # Ensure `docs` folder exists. If a legacy `www` folder is present and
    # `docs` is missing, migrate files from `www` to `docs` so the project
    # can be published via GitHub Pages.
    script_dir = os.path.dirname(__file__)
    legacy_dir = os.path.join(script_dir, 'www')
    if not os.path.isdir(ROOT_DIR):
        if os.path.isdir(legacy_dir):
            try:
                print(f"Migrating site from '{legacy_dir}' to '{ROOT_DIR}'...")
                shutil.copytree(legacy_dir, ROOT_DIR)
            except Exception as ex:
                print(f"Migration failed: {ex}. Creating empty '{ROOT_DIR}' folder.")
                os.makedirs(ROOT_DIR, exist_ok=True)
        else:
            os.makedirs(ROOT_DIR, exist_ok=True)

    # create index.html only if missing (main content edited separately)
    index_path = os.path.join(ROOT_DIR, 'index.html')
    if not os.path.isfile(index_path):
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('<!doctype html>\n<html lang="ru">\n<head>\n  <meta charset="utf-8">\n  <title>Вагонное депо Самара</title>\n  <link rel="stylesheet" href="styles.css">\n</head>\n<body>\n  <h1>Вагонное депо Самара</h1>\n  <p>Добро пожаловать — страница создаётся автоматически.</p>\n</body>\n</html>')

    # create other sections/pages (placeholders)
    team_path = os.path.join(ROOT_DIR, 'team.html')
    if not os.path.isfile(team_path):
        with open(team_path, 'w', encoding='utf-8') as f:
            f.write('''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Сотрудники — Вагонное депо Самара</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <h1 class="logo">Вагонное депо <span>Самара</span></h1>
      <nav class="nav">
        <a href="index.html">Главная</a>
        <a href="team.html">Сотрудники</a>
        <a href="scheme.html">Схема депо</a>
        <a href="profile.html">Личный кабинет</a>
      </nav>
    </div>
  </header>
  <main class="container">
    <h2>Сотрудники</h2>
  </main>
</body>
</html>
''')

    instr_path = os.path.join(ROOT_DIR, 'instructions.html')
    if not os.path.isfile(instr_path):
        with open(instr_path, 'w', encoding='utf-8') as f:
            f.write('''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Инструктаж — Вагонное депо Самара</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <h1 class="logo">Вагонное депо <span>Самара</span></h1>
      <nav class="nav">
        <a href="index.html">Главная</a>
        <a href="team.html">Сотрудники</a>
        <a href="scheme.html">Схема депо</a>
        <a href="profile.html">Личный кабинет</a>
      </nav>
    </div>
  </header>
  <main class="container">
    <h2>Инструктаж и тестирование</h2>
  </main>
</body>
</html>
''')

    scheme_path = os.path.join(ROOT_DIR, 'scheme.html')
    if not os.path.isfile(scheme_path):
        with open(scheme_path, 'w', encoding='utf-8') as f:
            f.write('''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Схема депо — Вагонное депо Самара</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <h1 class="logo">Вагонное депо <span>Самара</span></h1>
      <nav class="nav">
        <a href="index.html">Главная</a>
        <a href="team.html">Сотрудники</a>
        <a href="scheme.html">Схема депо</a>
        <a href="profile.html">Личный кабинет</a>
      </nav>
    </div>
  </header>
  <main class="container">
    <h2>Схема депо</h2>
  </main>
</body>
</html>
''')

    # ensure styles.css exists (do not overwrite)
    styles_path = os.path.join(ROOT_DIR, 'styles.css')
    if not os.path.isfile(styles_path):
        with open(styles_path, 'w', encoding='utf-8') as f:
            f.write('/* basic styles */\nbody{font-family:Arial,Helvetica,sans-serif;margin:0;padding:20px}')

    # ensure data/users.json exists with a default test user
    data_dir = os.path.join(ROOT_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.isfile(USERS_FILE):
        default = {
            "users": {
                "test": {
                    "password": "test",
                    "full_name": "Тестовый пользователь",
                    "photo": "images/avatar1.svg",
                    "position": "Инженер",
                    "mentor": "Иванов",
                    "hire_date": "2020-01-01",
                    "onboarding": [
                        {"id": 1, "title": "Пройти инструктаж", "completed": False},
                        {"id": 2, "title": "Знакомство с депо", "completed": False},
                        {"id": 3, "title": "Пройти тесты", "completed": False}
                    ],
                    "stats": [],
                    "payroll_requests": []
                }
            }
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

def _load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"users": {}}

def _save_users(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class APIHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS: allow cross-origin requests (frontend may be hosted separately)
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        # Handle preflight CORS
        self.send_response(200)
        self.end_headers()

    def send_json(self, obj, status=200):
        s = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(s)))
        self.end_headers()
        self.wfile.write(s)

    def do_GET(self):
        parsed = parse.urlparse(self.path)
        if parsed.path == '/api/profile/get':
            qs = parse.parse_qs(parsed.query)
            username = qs.get('username', [''])[0]
            try:
                data = _load_users()
                user = data.get('users', {}).get(username)
                if not user:
                    self.send_json({'ok': False}, status=404)
                    return
                # do not expose password
                user_copy = {k: v for k, v in user.items() if k != 'password'}
                self.send_json({'ok': True, 'user': user_copy})
            except Exception:
                self.send_json({'ok': False}, status=500)
            return
        # default to serving static files
        return super().do_GET()

    def do_POST(self):
        parsed = parse.urlparse(self.path)
        if parsed.path == '/api/login':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length else ''
            try:
                payload = json.loads(body or '{}')
                username = payload.get('username')
                password = payload.get('password')
                data = _load_users()
                user = data.get('users', {}).get(username)
                if user and user.get('password') == password:
                    self.send_json({'ok': True})
                else:
                    self.send_json({'ok': False})
            except Exception:
                self.send_json({'ok': False}, status=500)
            return

        if parsed.path == '/api/profile/update':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length else ''
            try:
                payload = json.loads(body or '{}')
                username = payload.get('username')
                update = payload.get('update', {})
                data = _load_users()
                users = data.setdefault('users', {})
                user = users.setdefault(username, {})
                # merge update fields (do not overwrite password unless provided)
                for k, v in update.items():
                    user[k] = v
                users[username] = user
                data['users'] = users
                _save_users(data)
                self.send_json({'ok': True})
            except Exception:
                self.send_json({'ok': False}, status=500)
            return

        return super().do_POST()


def _get_local_ip():
    """Определяем IP адрес в локальной сети (WiFi / Ethernet)."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())


def _ensure_firewall_rule(port):
    """Добавляем правило в Брандмауэр Windows, чтобы другие устройства
    в локальной сети могли подключиться к серверу."""
    import subprocess
    rule_name = f"VagonnoeDepo_TCP_{port}"
    try:
        # Проверяем, существует ли уже правило
        check = subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', f'name={rule_name}'],
            capture_output=True, text=True
        )
        if check.returncode == 0 and rule_name in check.stdout:
            return  # правило уже есть
        # Создаём правило (требуются права администратора)
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            f'name={rule_name}',
            'dir=in', 'action=allow', 'protocol=TCP',
            f'localport={port}',
            'profile=private,public',
        ], capture_output=True, text=True)
        print(f"[Firewall] Правило «{rule_name}» добавлено.")
    except Exception:
        print(f"[Firewall] Не удалось добавить правило. Запустите от имени Администратора")
        print(f"           или выполните вручную:")
        print(f'           netsh advfirewall firewall add rule name="{rule_name}" '
              f'dir=in action=allow protocol=TCP localport={port}')


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def run_server(port=PORT):
    ensure_site()
    os.chdir(ROOT_DIR)
    # Only attempt to modify Windows firewall when running on Windows
    # and the user hasn't disabled this behaviour via NO_FIREWALL=1.
    try:
        if os.name == 'nt' and os.environ.get('NO_FIREWALL') != '1':
            _ensure_firewall_rule(port)
    except Exception:
        pass
    handler = APIHandler
    with ReusableTCPServer(("0.0.0.0", port), handler) as httpd:
        local_ip = _get_local_ip()
        url = f"http://127.0.0.1:{port}/"
        print(f"\nServing at {url} (press Ctrl-C to stop)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  Для других устройств в сети (WiFi):")
        print(f"  → http://{local_ip}:{port}/")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        # Try to open browser only on local interactive runs (skip in CI/hosted)
        try:
            if not os.environ.get('CI') and os.environ.get('NO_BROWSER') != '1':
                webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped')

if __name__ == '__main__':
    # allow optional port override: python PythonApplication2.py 8080
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    except Exception:
        port = PORT
    run_server(port)
    