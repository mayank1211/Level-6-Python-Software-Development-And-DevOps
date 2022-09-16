# Level-6-Python-Software-Development-And-DevOps
Software Development and DevOps University Module.

## To run flask appllication without Docker
```
python3 -m venv venv && . venv/bin/activate

export FLASK_APP=application/application.py 

export FLASK_ENV=development

flaks run
```

## To run flask application using Docker
```
docker build -t python . --build-arg port=5000
docker run -p 5000:5000 python
```

## To run application tests:
- Default test `pytest`
- With coverage report `pytest --cov-report term --cov=application .`
- Coverage Report with HTML `coverage run --source=application -m pytest && coverage html && open htmlcov/index.html`

## Default application login:

Standard User:
User: mayank.patel@standard.com
Password: standard

Admin User:
User: mayank.patel@admin.com
Password: admin
