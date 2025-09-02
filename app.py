from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dyslexia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tests = db.relationship('TestResult', backref='user', lazy=True)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer)  # in seconds
    errors = db.Column(db.Text)  # JSON string of error types
    risk_level = db.Column(db.String(20))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        username=data['username'],
        email=data['email'],
        age=data.get('age')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created', 'user_id': new_user.id}), 201

@app.route('/api/test-results', methods=['POST'])
def save_test_result():
    data = request.json
    new_result = TestResult(
        user_id=data['user_id'],
        test_type=data['test_type'],
        score=data['score'],
        time_taken=data['time_taken'],
        errors=json.dumps(data['errors']),
        risk_level=data['risk_level']
    )
    db.session.add(new_result)
    db.session.commit()
    return jsonify({'message': 'Test result saved', 'result_id': new_result.id}), 201

@app.route('/api/users/<int:user_id>/results', methods=['GET'])
def get_user_results(user_id):
    results = TestResult.query.filter_by(user_id=user_id).all()
    output = []
    for result in results:
        output.append({
            'id': result.id,
            'test_type': result.test_type,
            'score': result.score,
            'time_taken': result.time_taken,
            'risk_level': result.risk_level,
            'completed_at': result.completed_at
        })
    return jsonify(output)

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    total_tests = TestResult.query.count()
    low_risk = TestResult.query.filter_by(risk_level='low').count()
    medium_risk = TestResult.query.filter_by(risk_level='medium').count()
    high_risk = TestResult.query.filter_by(risk_level='high').count()
    
    return jsonify({
        'total_tests': total_tests,
        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)