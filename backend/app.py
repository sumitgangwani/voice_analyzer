import os
import json
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from collections import Counter
from google.cloud import translate_v2 as translate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # Ensures the cookie is only sent over HTTPS

jwt = JWTManager(app)
db = SQLAlchemy(app)

# Load Google Cloud credentials from environment variable
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if not credentials_json:
    raise EnvironmentError("Google Cloud credentials not found in environment variables")

# Create a temporary file to store the credentials
temp_json_file = "/tmp/google_credentials.json"

# Write the JSON content to the temporary file
with open(temp_json_file, "w") as f:
    f.write(credentials_json)

# Initialize Google Cloud Translate client using the temporary credentials file
translate_client = translate.Client.from_service_account_json(temp_json_file)

# Define the Transcription model
class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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


# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Store the password directly (not recommended)
    new_user = User(username=username, email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201



# Signin route
@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Fetch the user based on the email
    user = User.query.filter_by(email=email).first()

    # Directly compare the plain-text password
    if not user or user.password != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Store the user ID in the session instead of creating a JWT token
    session['user_id'] = user.id
    session['username'] = user.username

    return jsonify({'message': 'Logged in successfully', 'username': user.username, 'user_id': user.id}), 200


@app.route('/signout', methods=['POST'])
def signout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


# Route to handle transcription text submission
@app.route('/transcribe', methods=['POST'])
def transcribe_text():
    try:
        # Ensure that the user is authenticated via session
        if 'user_id' not in session:
            return jsonify({"error": "User not authenticated"}), 401

        user_id = session['user_id']  # Get the user ID from the session

        # Retrieve the transcription text from the form data
        transcription = request.form.get('transcription')
        if not transcription:
            return jsonify({"error": "Transcription text is missing"}), 422

        print(f"Received transcription: {transcription}, user_id: {user_id}")

        # Detect the language of the transcription
        result = translate_client.detect_language(transcription)
        detected_language = result['language']

        # Translate to English if the detected language is not English
        if detected_language != 'en':
            translation_result = translate_client.translate(transcription, target_language='en')
            translated_text = translation_result['translatedText']
        else:
            translated_text = transcription

        # Save the transcription to the database
        new_transcription = Transcription(
            user_id=user_id,
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

# Route to find similar users based on their transcriptions
@app.route('/similar_users/<int:user_id>', methods=['GET'])
def similar_users(user_id):
    try:
        # Get transcriptions for the current user
        current_user_transcriptions = Transcription.query.filter_by(user_id=user_id).all()
        current_user_text = " ".join([t.transcription for t in current_user_transcriptions])

        if not current_user_text:
            return jsonify({"error": "No transcriptions found for the current user."}), 404

        # Get transcriptions for all other users
        other_users = User.query.filter(User.id != user_id).all()

        if not other_users:
            return jsonify({"error": "No other users found."}), 404

        other_users_texts = []
        user_mapping = []

        for user in other_users:
            user_transcriptions = Transcription.query.filter_by(user_id=user.id).all()
            user_text = " ".join([t.transcription for t in user_transcriptions])

            if user_text:
                other_users_texts.append(user_text)
                user_mapping.append(user)

        if not other_users_texts:
            return jsonify({"error": "No transcriptions found for other users."}), 404

        # Combine texts and compute similarity
        all_texts = [current_user_text] + other_users_texts
        vectorizer = TfidfVectorizer().fit_transform(all_texts)
        vectors = vectorizer.toarray()
        cosine_similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

        # Pair each user with their similarity score and sort by score
        similarity_scores = sorted(
            list(zip(user_mapping, cosine_similarities)),
            key=lambda x: x[1], reverse=True
        )

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
        print(f"Error occurred while processing similar_users: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

# Main block to create the database tables
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
