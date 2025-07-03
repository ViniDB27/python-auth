from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager(app)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username or password:
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({'message':'Logado com sucesso'}), 200
    return jsonify({'message':'Credenciais inválidas'}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message':'Deslogado com sucesso'})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if username and email and password:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message':'Usuário criado com sucesso'}), 201
    return jsonify({'message':'Dados incompletos'}), 400


@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    output = {
        'users': [user.to_dict() for user in users],
        'totla': len(users)
    } 
    return jsonify(output)

@app.route('/users/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'message':'Usuário não encontrado'}), 404

@app.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message':'Usuário não encontrado'}), 404
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if email:
        user.email = email
    if password:
        user.password = password
    db.session.commit()
    return jsonify({'message':'Usuário atualizado com sucesso'})

@app.route('/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'message':'Usuário não encontrado'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'Usuário deletado com sucesso'})

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)