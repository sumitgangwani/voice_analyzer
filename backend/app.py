# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from models import db, Transcription
# from google.cloud import speech_v1p1beta1 as speech
# from google.cloud import translate_v2 as translate
# from collections import Counter
#
# app = Flask(__name__)
# CORS(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db.init_app(app)
#
# # Specify the path to your service account key file
# service_account_path = "E:/projects/json_key/voiceanalyzer-433407-a09812007bbd.json"
#
# # Initialize clients with the service account file
# client = speech.SpeechClient.from_service_account_file(service_account_path)
# translate_client = translate.Client.from_service_account_json(service_account_path)
#
#
# @app.route('/transcribe', methods=['POST'])
# def transcribe_audio():
#     try:
#         audio = request.files['audio']
#         user_id = request.form['user_id']
#         print(f"Received audio: {audio}, user_id: {user_id}")
#         audio_content = audio.read()
#
#         response = client.recognize(
#             config={"language_code": "en-US"},
#             audio={"content": audio_content},
#         )
#
#         transcription = response.results[0].alternatives[0].transcript
#         language_code = response.results[0].language_code
#
#         if language_code != 'en':
#             translation = translate_client.translate(transcription, target_language='en')
#             transcription = translation['translatedText']
#
#         new_transcription = Transcription(
#             user_id=user_id,
#             transcription=transcription
#         )
#
#         db.session.add(new_transcription)
#         db.session.commit()
#
#         return jsonify({"transcription": transcription})
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return jsonify({"error": str(e)}), 500
#
#
# @app.route('/history/<int:user_id>', methods=['GET'])
# def get_history(user_id):
#     transcriptions = Transcription.query.filter_by(user_id=user_id).all()
#     return jsonify([t.serialize() for t in transcriptions])
#
#
# @app.route('/statistics/<int:user_id>', methods=['GET'])
# def get_statistics(user_id):
#     transcriptions = Transcription.query.filter_by(user_id=user_id).all()
#     all_transcriptions = Transcription.query.all()
#
#     user_words = Counter(" ".join([t.transcription for t in transcriptions]).split())
#     global_words = Counter(" ".join([t.transcription for t in all_transcriptions]).split())
#
#     user_common = user_words.most_common(10)
#     global_common = global_words.most_common(10)
#
#     return jsonify({
#         "user_common": user_common,
#         "global_common": global_common,
#     })
#
#
# @app.route('/unique_phrases/<int:user_id>', methods=['GET'])
# def get_unique_phrases(user_id):
#     transcriptions = Transcription.query.filter_by(user_id=user_id).all()
#     user_phrases = [t.transcription for t in transcriptions]
#
#     phrases_counter = Counter(user_phrases)
#     top_phrases = phrases_counter.most_common(3)
#
#     return jsonify({
#         "top_phrases": top_phrases
#     })
#
#
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
#


# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from models import db, Transcription
# from google.cloud import speech_v1p1beta1 as speech
# from google.cloud import translate_v2 as translate
# from collections import Counter
# import os
#
# app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
# CORS(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db.init_app(app)
#
# # Adjust the path to the service account key file for deployment
# service_account_path = "/home/yourusername/path_to_your_json_key/voiceanalyzer-433407-a09812007bbd.json"
#
# # Initialize clients with the service account file
# client = speech.SpeechClient.from_service_account_file(service_account_path)
# translate_client = translate.Client.from_service_account_json(service_account_path)
#
# @app.route('/')
# def serve():
#     return send_from_directory(app.static_folder, 'index.html')
#
# @app.route('/transcribe', methods=['POST'])
# def transcribe_audio():
#     try:
#         audio = request.files['audio']
#         user_id = request.form['user_id']
#         print(f"Received audio: {audio}, user_id: {user_id}")
#         audio_content = audio.read()
#
#         response = client.recognize(
#             config={"language_code": "en-US"},
#             audio={"content": audio_content},
#         )
#
#         transcription = response.results[0].alternatives[0].transcript
#         language_code = response.results[0].language_code
#
#         if language_code != 'en':
#             translation = translate_client.translate(transcription, target_language='en')
#             transcription = translation['translatedText']
#
#         new_transcription = Transcription(
#             user_id=user_id,
#             transcription=transcription
#         )
#
#         db.session.add(new_transcription)
#         db.session.commit()
#
#         return jsonify({"transcription": transcription})
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return jsonify({"error": str(e)}), 500
#
# @app.route('/history/<int:user_id>', methods=['GET'])
# def get_history(user_id):
#     transcriptions = Transcription.query.filter_by(user_id=user_id).all()
#     return jsonify([t.serialize() for t in transcriptions])
#
# @app.route('/statistics/<int:user_id>', methods=['GET'])
# def get_statistics(user_id):
#     transcriptions = Transcription.query.filter_by(user_id=user_id).all()
#     all_transcriptions = Transcription.query.all()
#
#     user_words = Counter(" ".join([t.transcription for t in transcriptions]).split())
#     global_words = Counter(" ".join([t.transcription for t in all_transcriptions]).split())
#
#     user_common = user_words.most_common(10)
#     global_common = global_words.most_common(10)
#
#     return jsonify({
#         "user_common": user_common,
#         "global_common": global_common,
#     })
#
# @app.route('/unique_phrases/<int:user_id>', methods=['GET'])
# def get_unique_phrases(user_id):
#     transcriptions = Transcription.query.filter_by(user_id=user_id).all()
#     user_phrases = [t.transcription for t in transcriptions]
#
#     phrases_counter = Counter(user_phrases)
#     top_phrases = phrases_counter.most_common(3)
#
#     return jsonify({
#         "top_phrases": top_phrases
#     })
#
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)





from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from collections import Counter
from google.cloud import translate_v2 as translate
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import translate_v2 as translate
from flask import request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity



app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
jwt = JWTManager(app)# Replace with a strong secret key
db = SQLAlchemy(app)

# Initialize Google Cloud Translate client
translate_client = translate.Client.from_service_account_json("E:/projects/json_key/voiceanalyzer-433407-a09812007bbd.json")

# Define the Transcription model
class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 'user.id' refers to the 'id' column in the User table
    transcription = db.Column(db.Text, nullable=False)
    original_language = db.Column(db.String(10), nullable=False, default='en')

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transcription': self.transcription,
            'original_language': self.original_language,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


@app.route('/similar_users/<int:user_id>', methods=['GET'])
def similar_users(user_id):
    try:
        # Fetch the current user's transcriptions
        current_user_transcriptions = Transcription.query.filter_by(user_id=user_id).all()
        current_user_text = " ".join([t.transcription for t in current_user_transcriptions])

        if not current_user_text:
            return jsonify({"error": "No transcriptions found for the current user."}), 400

        all_users = User.query.all()
        other_users = [user for user in all_users if user.id != user_id]

        if not other_users:
            return jsonify({"error": "No other users found."}), 400

        other_users_texts = []
        user_mapping = []

        for user in other_users:
            user_transcriptions = Transcription.query.filter_by(user_id=user.id).all()
            user_text = " ".join([t.transcription for t in user_transcriptions])

            if user_text:
                other_users_texts.append(user_text)
                user_mapping.append(user)

        if not other_users_texts:
            return jsonify({"error": "No transcriptions found for other users."}), 400

        # Combine the current user text with the other users' texts
        all_texts = [current_user_text] + other_users_texts

        # Vectorize the texts and compute cosine similarity
        vectorizer = TfidfVectorizer().fit_transform(all_texts)
        vectors = vectorizer.toarray()
        cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

        # Pair each other user with their similarity score
        similarity_scores = list(zip(user_mapping, cosine_similarities))

        # Sort users by similarity score (highest first)
        similarity_scores.sort(key=lambda x: x[1], reverse=True)

        # Prepare the result to return
        result = [
            {
                "user_id": user.id,
                "username": user.username,
                "similarity_score": score
            }
            for user, score in similarity_scores
        ]

        return jsonify(result)

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

# Signin route
@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'message': 'Logged in successfully', 'username': user.username}), 200


# Signout route
@app.route('/signout', methods=['POST'])
def signout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Route to handle transcription text submission
@app.route('/transcribe', methods=['POST'])
@jwt_required()  # Require the user to be authenticated
def transcribe_text():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()

        transcription = request.form['transcription']
        print(f"Received transcription: {transcription}, user_id: {user_id}")

        # Detect the language of the transcription
        result = translate_client.detect_language(transcription)
        detected_language = result['language']

        # If the language is not English, translate it to English
        if detected_language != 'en':
            translation_result = translate_client.translate(transcription, target_language='en')
            translated_text = translation_result['translatedText']
        else:
            translated_text = transcription

        # Save the transcription to the database with the user_id
        new_transcription = Transcription(
            user_id=user_id,  # Use the user_id from the token
            transcription=translated_text,
            original_language=detected_language
        )

        db.session.add(new_transcription)
        db.session.commit()

        return jsonify({
            "message": "Transcription saved successfully!",
            "transcription": translated_text,
            "original_language": detected_language
        })
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

# Route to get transcription history for a user
@app.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    transcriptions = Transcription.query.filter_by(user_id=user_id).all()
    return jsonify([t.serialize() for t in transcriptions])

# Route to get word frequency statistics for a user
@app.route('/statistics/<int:user_id>', methods=['GET'])
def get_statistics(user_id):
    transcriptions = Transcription.query.filter_by(user_id=user_id).all()
    all_transcriptions = Transcription.query.all()

    user_words = Counter(" ".join([t.transcription for t in transcriptions]).split())
    global_words = Counter(" ".join([t.transcription for t in all_transcriptions]).split())

    user_common = user_words.most_common(10)
    global_common = global_words.most_common(10)

    return jsonify({
        "user_common": user_common,
        "global_common": global_common,
    })

# Route to get unique phrases for a user
@app.route('/unique_phrases/<int:user_id>', methods=['GET'])
def get_unique_phrases(user_id):
    transcriptions = Transcription.query.filter_by(user_id=user_id).all()
    user_phrases = [t.transcription for t in transcriptions]

    phrases_counter = Counter(user_phrases)
    top_phrases = phrases_counter.most_common(3)

    return jsonify({
        "top_phrases": top_phrases
    })

# Main block to create the database tables
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
