from flask import Flask, request, make_response
import json
from metaswitch.ellis.lines import PrimaryLine
from metaswitch.ellis.homestead_client import HomesteadClient
app = Flask(__name__)

class User:
    def __init__(self, email, password):
        self.password = password
        self.email = email
        self.lines = []


@app.route('/session/', methods=['POST'])
def new_session():
    db = app.config['DATABASE']
    provided_data = json.loads(request.get_data(as_text=True))
    username = provided_data.get('username')
    if username is None:
        return "", 401, []

    user = db.get_user(username)
    if user is None:
        return "", 403, []
        
    if provided_data.get('password') != user.password:
        return "", 403, []
    
    resp = make_response("")
    resp.set_cookie('username', username)
    return resp

@app.route('/accounts/', methods=['POST'])
def new_account():
    db = app.config['DATABASE']
    provided_data = json.loads(request.get_data(as_text=True))
    username = provided_data.get('username')
    password = provided_data.get('password')
    full_name = provided_data.get('full_name')
    email = provided_data.get('email')

    if db.get_user(email) is not None:
        return "", 409, []

    db.save_user(User(email, password))
    return "", 201, []

@app.route('/accounts/<username>', methods=['DELETE'])
def delete_account():
    pass

@app.route('/accounts/<username>/password', methods=['POST'])
def reset_password():
    pass

def get_user_if_authorized(db, username, request):
    # Check user is authorised
    rusername = request.cookies.get('username')
    if username != rusername:
        return None

    user = db.get_user(rusername)

    return user

@app.route('/accounts/<username>/numbers', methods=['GET'])
def list_numbers(username):
    db = app.config['DATABASE']
    user = get_user_if_authorized(db, username, request)

    if user is None:
        return "", 403, []

    # get numbers for that user
    list_of_numbers = json.dumps({"numbers": [l.to_json() for l in user.lines if l.deletion_begun is False]})
    return list_of_numbers

@app.route('/accounts/<username>/numbers', methods=['POST'])
def allocate_number(username):
    db = app.config['DATABASE']
    user = get_user_if_authorized(db, username, request)

    if user is None:
        return "", 403, []

    user.lines.append(new_line(username))
    db.save_user(user)
    return ""

@app.route('/accounts/<username>/numbers/<uri>', methods=['POST'])
def allocate_specific_number(username, uri):
    #  check user is authorised
    line = new_line(username, uri)
    if line is None:
        # return 502
        pass

@app.route('/accounts/<username>/numbers/<uri>/password', methods=['POST'])
def change_line_password(username, uri):
    pass

def new_line(owner_id, specific_line = None):
    homestead = app.config['HOMESTEAD_CLIENT']
    db = app.config['DATABASE']

    if specific_line is None:
        specific_line = db.get_next_free_line()

    new_line = PrimaryLine(owner_id, specific_line)
    success = new_line.create_elsewhere(homestead)
    if success:
        # save new line
        # return appropriate info
        return new_line
    else:
        # return line to pool
        return None

if __name__ == '__main__':
    app.config['HOMESTEAD_CLIENT'] = HomesteadClient("127.0.0.1")
    app.run(debug=True)

