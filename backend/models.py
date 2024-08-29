# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask, request, jsonify, session, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_cors import CORS
# db = SQLAlchemy()
#
#
# class Transcription(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, nullable=False)
#     transcription = db.Column(db.Text, nullable=False)
#
#     def serialize(self):
#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'transcription': self.transcription,
#         }
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
