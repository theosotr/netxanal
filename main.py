__author__ = 'Thodoris Sotiropoulos'


from flask import Flask

app = Flask(__name__)
app.secret_key = "rd"
current_user = None
project = None

import mvc.view.navigator
import mvc.view.registration
import mvc.view.graph
import mvc.view.diagram
import mvc.view.project
import mvc.view.download

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
