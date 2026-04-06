from flask import Flask, jsonify, request, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__, static_folder='.')
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/tododb')
client = MongoClient(MONGO_URI)
db = client['tododb']

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = list(db.todos.find())
    for t in todos:
        t['_id'] = str(t['_id'])
    return jsonify(todos)

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    result = db.todos.insert_one({
        'task': data['task'],
        'priority': data.get('priority', 'low'),
        'done': False
    })
    return jsonify({'_id': str(result.inserted_id)})

@app.route('/todos/<id>/toggle', methods=['PATCH'])
def toggle_todo(id):
    todo = db.todos.find_one({'_id': ObjectId(id)})
    db.todos.update_one({'_id': ObjectId(id)}, {'$set': {'done': not todo['done']}})
    return jsonify({'ok': True})

@app.route('/todos/<id>', methods=['DELETE'])
def delete_todo(id):
    db.todos.delete_one({'_id': ObjectId(id)})
    return jsonify({'ok': True})

@app.route('/todos/clear-done', methods=['DELETE'])
def clear_done():
    db.todos.delete_many({'done': True})
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)