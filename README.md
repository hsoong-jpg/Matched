# Matched🎾 
Tennis Player Matching Platform

A full-stack web application that connects tennis players based on skill level, preferences, and location. Built with Flask and SQLite, the platform includes real-time messaging, mutual matching, and secure authentication.

Features:

User Authentication
Secure signup/login system
Password hashing using Werkzeug
Session-based login persistence


User Profiles
Create and edit tennis player profiles
Store bio, location, UTR rating, and preferences


Swipe-Based Matching System
Like/Pass user discovery system
Prevents duplicate recommendations
Mutual match detection via SQL logic

Real-Time Chat
Flask-SocketIO powered messaging
Instant communication between matched users
Room-based chat architecture


Inbox & Matches
Displays mutual matches
Shows last message preview
Clean chat entry system


Frontend UI
Jinja2 templating system
Responsive card-based layout
Clean navigation bar and mobile-friendly design


Tech Stack
Backend: Flask, Flask-SocketIO
Database: SQLite
Frontend: HTML, CSS, JavaScript, Jinja2
Security: Werkzeug password hashing
Architecture: Flask Blueprints (modular design)


System Design Overview
Session-based authentication controls access to all core features
Mutual matching implemented using relational SQL queries
Real-time messaging handled via SocketIO rooms per match
Modular blueprint structure for scalable backend design