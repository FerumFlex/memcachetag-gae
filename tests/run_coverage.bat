coverage.exe run --branch --source ..\memcachetag.py ..\runner.py "c:\Program Files (x86)\Google\google_appengine" ..\tests\
coverage.exe html
del .coverage