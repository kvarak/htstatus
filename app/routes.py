from app import app

@app.route('/')
@app.route('/index')
def index():
  return "Hello, World!" + app.config['REQUEST_TOKEN_PATH']
