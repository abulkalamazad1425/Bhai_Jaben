#!/usr/bin/env fish

if not test -d venv
    python -m venv venv
end

. venv/bin/activate.fish

#./bookvenv/bin/python -m  pip install --upgrade pip
pip install -r requirements.txt

uvicorn main:app --host 127.0.0.1 --port 8002 --reload