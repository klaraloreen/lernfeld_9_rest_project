from flask import Flask, request, jsonify, abort

# init Flask server
app = Flask(__name__)

# create ids for lists, users and entries
user_id_annika = 1
user_id_chris = 2
user_id_klara = 3

todo_list_1_id = 1
todo_list_2_id = 2
todo_list_3_id = 3

entry_1_id = 1
entry_2_id = 2
entry_3_id = 3
entry_4_id = 4

# user list with internal data. changes will not be saved permanently.
user_list = [
    {'id': user_id_annika, 'name': 'Annika'},
    {'id': user_id_chris, 'name': 'Chris'},
    {'id': user_id_klara, 'name': 'Klara'}
]

# todo lists with internal data. changes will not be saved permanently.
todo_lists = [
    {'id': todo_list_1_id, 'name': 'Schule'},
    {'id': todo_list_2_id, 'name': 'Einkaufsliste'},
    {'id': todo_list_3_id, 'name': 'Haushalt'}
]

# entries with internal data. changes will not be saved permanently.
entries = [
    {
        'id': entry_1_id,
        'name': 'Hausaufgabe Deutsch',
        'description': 'Der Aufsatz muss zu Ende geschrieben werden',
        'list': todo_list_1_id,
        'user': user_id_annika
    },
    {
        'id': entry_2_id,
        'name': 'Vokabeln Englisch',
        'description': 'Die Vokabeln auf Seite 7 - 10 müssen gelernt werden',
        'list': todo_list_1_id,
        'user': user_id_annika
    },
    {
        'id': entry_3_id,
        'name': 'Kekse',
        'description': '',
        'list': todo_list_2_id,
        'user': user_id_chris
    },
    {
        'id': entry_4_id,
        'name': 'Badezimmer putzen',
        'description': 'Bitte auch den Mülleimer leeren',
        'list': todo_list_3_id,
        'user': user_id_klara
    }
]

## endpoint definitions - start ##

@app.route('/list/<list_id>', methods=['GET', 'DELETE'])
""" Handles the server endpoint /list/<list_id> which expects a list id to be passed in the URL.
    Will either return all entries of a specific list (GET) oder delete a specific list (DELETE).
    Returns 404 status if error occurs. """
def handleList(list_id):
    # find list by passed id
    chosen_list = findListById(int(list_id))        
    if not chosen_list:
        abort(404)
        
    if request.method == 'GET':
        # return all entries of found list in json format
        return jsonify([
            i for i in entries if i['list'] == int(list_id)
        ])
    elif request.method == 'DELETE':
        # remove aka delete the specific list
        todo_lists.remove(chosen_list)
        return 'Löschen der Liste erfolgreich', 200

    return '', 404

""" Handles the server endpoint /list which will add a new list.
    Config for the new list must be passed as JSON.
    Returns the added list. """
@app.route('/list', methods=['POST'])
def addList():
    # get list configuration by accessing the passed JSON object
    new_list = request.get_json(force=True)
    # generate and add new list id
    new_list_id = getHighestListId() + 1
    new_list['id'] = new_list_id
    # add new list to list of todo lists
    todo_lists.append(new_list)
    return jsonify(new_list), 200

""" Handles the server endpoint /list/<list_id>/entry which will append an entry to an existing list.
    The entry is expected to be passed as a JSON object. The desired list id must be passed in the URL.
    Returns status code 500 if error occurs. """
@app.route('/list/<list_id>/entry', methods=['POST'])
def addEntryToList(list_id):
    # find list by the given list id
    chosen_list = findListById(int(list_id))        
    if not chosen_list:
        abort(500)

    # get entry configuration by accessing the passed JSON object
    new_entry = request.get_json(force=True)
    # generate and add new entry id
    try:
        new_entry['id'] = getHighestEntryId() + 1
        new_entry['list'] = chosen_list['id']
        entries.append(new_entry)
    except:
        abort(500)
    return jsonify(new_entry), 200

""" Handles the server endpoint /list/<list_id>/entry/<entry_id> which will update an existing entry.
    The list id and entry id are expected to be passed as URL parameters. Update data must be passed as a JSON object.
    Returns status code 404 if error occurs. """
@app.route('/list/<list_id>/entry/<entry_id>', methods=['POST', 'DELETE'])
def updateOrDeleteExistingEntry(list_id, entry_id):
    entry_to_handle = None
    # find the entry that needs to be handled (either updated or deleted)
    for e in entries:
        if e['list'] == int(list_id) and e['id'] == int(entry_id):
            entry_to_handle = e
            break

    # if no entry is found, abort operation
    if not entry_to_handle:
        abort(404)

    if request.method == 'POST':
        # case: update entry
        # get new entry configuration by accessing the passed JSON object
        update_data = request.get_json(force=True)
        # entry id and list need to stay the same
        update_data['id'] = entry_to_handle['id']
        update_data['list'] = entry_to_handle['list']
        
        # remove old entry and add updated entry
        entries.remove(entry_to_handle)
        entries.append(update_data)
        return jsonify(update_data), 200
    elif request.method == 'DELETE':
        # case: delete entry
        entries.remove(entry_to_handle)
        return 'Löschen des Eintrags erfolgreich', 200

    return '', 404

""" Handles the server endpoint /users that will return a list of all users.
    No parameters needed. """
@app.route('/users', methods=['GET'])
def getAllUsers():
    return jsonify(user_list)

""" Handles the server endpoint /user which will add a new user.
    The configuration for the new user needs to passed as a JSON parameter. """
@app.route('/user', methods=['POST'])
def addNewUser():
    # get new user configuration by accessing the passed JSON object
    new_user = request.get_json(force=True)
    # get new user id
    new_user['id'] = getHighestUserId() + 1
    user_list.append(new_user)
    return jsonify(new_user), 200

""" Handles the server endpoint /user/<user_id> which will delete an existing user.
    The user id for the user to be deleted needs to passed as an URL parameter.
    Returns status code 404 if error occurs. """
@app.route('/user/<user_id>', methods=['DELETE'])
def deleteUser(user_id):
    user_to_delete = None
    # find user to delete
    for u in user_list:
        if u['id'] == int(user_id):
            user_to_delete = u
            break

    # if no matching user exists, abort operation
    if not user_to_delete:
        abort(404)

    user_list.remove(user_to_delete)
    return 'Löschen des Nutzers erfolgreich', 200

## endpoint definitions - end ##

## helper functions - start ##

""" Helper function for getting the highest list id. """
def getHighestListId():
    max = todo_lists[0]['id']
    for l in todo_lists:
        if l['id'] > max:
            max = l['id']
    return max

""" Helper function for getting the highest entry id. """
def getHighestEntryId():
    max = entries[0]['id']
    for e in entries:
        if e['id'] > max:
            max = e['id']
    return max

""" Helper function for getting the highest user id. """
def getHighestUserId():
    max = user_list[0]['id']
    for u in user_list:
        if u['id'] > max:
            max = u['id']
    return max

""" Helper function for finding a list by a given id. """
def findListById(id):
    retval = None
    for l in todo_lists:
        if l['id'] == id:
            retval = l
            break
    return retval

## helper functions - end ##
            	    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
