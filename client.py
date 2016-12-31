
from yflask import Flask

def log(args, **kwarg):
    print(args, **kwarg)

app = Flask(__name__)


@app.route('/')
def show_entries():
    return 'hello'


app.run()


log(app.root_path)
log(app.view_function)

