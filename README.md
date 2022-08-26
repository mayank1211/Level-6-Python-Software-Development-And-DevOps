# Level-6-Python-Software-Development-And-DevOps
Software Development and DevOps University Module.

## To run flask appllication without Docker
```
python3 -m venv venv && . venv/bin/activate
export FLASK_APP=application/application.py && export FLASK_ENV=development
```

## To run flask application using Docker
```
docker build -t python .
docker run -p 5000:5000 python
```

## TODOS
 - [ ] REFACTOR APPLICATION CODE
 - [ ] ADD UNIT TESTS - TO RUN BEFORE APPLICATION DEPLOYMENT IN THE HEROKU PIPELINE
 - [ ] EMAIL NOTIFICATION SENDER

 ## TO FIX
 - [ ] IMPLEMENT OWASP SCANNING
 - [ ] FLAKE 8