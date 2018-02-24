# Flask

## Flask is Fun

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'
```

## And Easy to Setup

```shell
$ pip install Flask
$ FlASK_APP=hello.py flask run
  * running on http://localhost:5000/
```