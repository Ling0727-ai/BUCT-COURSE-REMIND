import ast, sys
files = [
    'app/blacklist.py',
    'app/__init__.py',
    'app/assignments.py',
    'app/scraper.py',
    'app/background_tasks.py',
    'app/scheduler.py',
    'app/course_data.py',
]
ok = True
for f in files:
    try:
        ast.parse(open(f, encoding='utf-8').read())
        print(f, 'OK')
    except SyntaxError as e:
        print(f, 'FAIL:', e)
        ok = False
sys.exit(0 if ok else 1)

