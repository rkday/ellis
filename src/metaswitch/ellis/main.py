from flask import Flask, request, make_response
import json
from metaswitch.ellis.lines import LinePool, PrimaryLine
from metaswitch.ellis.homestead_client import HomesteadClient
app = Flask(__name__)

class User:
    def __init__(self, name, password):
        self.password = password

global_homestead = HomesteadClient("example.com")
global_linepool = LinePool()

users = {"system.test@rkd.cw-ngv.com": User("rkd", "Please enter your details")}
        
@app.route('/session/', methods=['POST'])
def new_session():
    db = app.config['DATABASE']
    provided_data = json.loads(request.get_data(as_text=True))
    username = provided_data.get('username')
    if (username == None):
        return ("", 401, [])        

    user = db.get_user(username)
    if (user == None):
        return ("", 403, [])        
        
    if (provided_data.get('password') != user.password):
        return ("", 403, [])
    
    resp = make_response("")
    resp.set_cookie('username', username)
    return resp

@app.route('/accounts/', methods=['POST'])
def new_account():
    provided_data = json.loads(request.get_data(as_text=True))
    username = provided_data.get('username')
    password = provided_data.get('password')
    full_name = provided_data.get('full_name')
    email = provided_data.get('email')

    if users.get(username) is not None:
        return ("", 409, [])

    users[username] = User(full_name, password)
    return ("", 201, [])

@app.route('/accounts/<username>', methods=['DELETE'])
def delete_account():
    pass

@app.route('/accounts/<username>/password', methods=['POST'])
def reset_password():
    pass

@app.route('/accounts/<username>/numbers', methods=['DELETE'])
def list_numbers(username):
    #  check user is authorised

    # get numbers for that user
    list_of_numbers = json.dumps({"numbers": []})
    return list_of_numbers

@app.route('/accounts/<username>/numbers', methods=['POST'])
def allocate_number(username):
    #  check user is authorised
    line = new_line(username)

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

    if specific_line is None:
        specific_line = global_linepool.get_next()

    new_line = PrimaryLine(owner_id, specific_line)
    success = new_line.create_elsewhere(global_homestead)
    if success:
        # save new line
        # return appropriate info
        return new_line
    else:
        # return line to pool
        return None

if __name__ == '__main__':
    app.run(debug=True)

