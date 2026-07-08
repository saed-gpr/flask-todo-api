from flask import Blueprint, jsonify, request
from app.models import db, User
from app.models import Todo

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({'message' : 'Welcome to Flask Todo API!'})

@main_bp.route('/users', methods=['POST'])
def create_user():


    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify(
            {
                "error" : "Missing required fields"
            }
        ), 400
    user_by_username = User.query.filter_by(username=username).first()
    user_by_email = User.query.filter_by(email=email).first()

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({
            "error" : "Username or Email already exists"
        }), 400
    new_user = User(
        username = username,
        email = email,
    )

    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message" : "User created successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify ({
            "error" : "Database error", "details": str(e)
        }), 500
    
@main_bp.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()

    print('--- recived todo data: ---', data)

    title = data.get('title')
    description = data.get('description')
    user_id = data.get('user_id')

    if not title or not user_id:
        return jsonify({
            "error" : "Title and User ID are required"
        }), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "error" : "User not found"
        }), 404
    
    new_todo = Todo(
        title = title,
        description=description,
        user_id=user_id
    )

    try:
        db.session.add(new_todo)
        db.session.commit()

        return jsonify({
            "message": "Todo created successfully",
            "todo": {
                "id": new_todo.id,
                "title": new_todo.title,
                "description": new_todo.description,
                "is_completed": new_todo.is_completed,
                "user_id": new_todo.user_id
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    
@main_bp.route('/users/<int:user_id>/todos', methods=['GET'])
def get_user_todos(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_todos = Todo.query.filter_by(user_id=user_id).all()

    todos_list = []
    for todo in user_todos:
        todos_list.append({
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "is_completed": todo.is_completed
        })

    return jsonify({
        "username": user.username,
        "total_todos": len(todos_list),
        "todos": todos_list
    }), 200

@main_bp.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):

    todo = Todo.query.get(todo_id)

    if not todo:
        return jsonify({
            "error" : "Todo not found"
        }), 404
    
    data = request.get_json() or {}

    if 'title' in data:
        todo.title = data.get('title')
    if 'description' in data:
        todo.description = data.get('description')

    if 'is_completed' in data:
        todo.is_completed = data.get('is_completed')
    else:
        todo.is_completed = not todo.is_completed

    try:
        db.session.commit()

        return jsonify({
            "message": "Todo updated successfully",
            "todo": {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "is_completed": todo.is_completed
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error", "details": str(e)
        }), 500
    
@main_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):

    todo = Todo.query.get(todo_id)

    if not todo:
        return jsonify ({
            "error": "Todo not found"
        }), 404
    
    try:
        db.session.delete(todo)

        db.session.commit()

        return jsonify({
            "message": f"Todo with ID {todo_id} has been deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Database error", "details": str(e)
            }), 500
    
@main_bp.route('/test-users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        output.append({
            "id": user.id,
            "username": user.username,
            "password_in_database": user.password_hash # دیدن چیزی که در دیتابیس ذخیره شده
        })
    return jsonify({"users": output}), 200