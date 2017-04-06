
from yflask import Flask


def log(args, **kwarg):
    print(args, **kwarg)

DEBUG = True




app = Flask(__name__)
app.debug = DEBUG

@app.route('/')
def show_entries():
    return 'hello world yflask'

@app.route('/index')
def index():
    return 'index'

app.run()


log(app.root_path)
log(app.view_function)
