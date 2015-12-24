# --- Flask Hello World --- #

# import the Flask class from the flask package
from flask import Flask
# create the application object
app = Flask(__name__)


# use decorators to link the function to the URL
@app.route("/")
@app.route("/hello")
@app.route("/renefroger")
# define the view using a function which returns a string
def hello_world():
    return "Hello, world!"

if __name__ == "__main__":
    app.run()
