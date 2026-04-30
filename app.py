from flask import Flask, render_template, request, redirect

app = Flask(__name__)

#Fake list of people 
profiles = [

    {"id" : 1, "name" : "Hannah", "bio" : "UTR: 4 Singles, 5 Doubles"},
    {"id" : 2, "name" : "Eva", "bio" : "UTR: 4 Singles, 5 Doubles"},
    {"id" : 3, "name" : "O", "bio" : "UTR: 5 Singles, 4 Doubles"}
]
#which profile youre on
current_index = 0
#stores who you liked 
likes = []

#homepage
@app.route("/")
#when user visits run index()
def index():
    global current_index
    #stops if user runs out of profiles
    if current_index >= len(profiles):
        return "No more profiles"
    
    #Trender_template("index.html") Go find a file called index.html in the templates folder and show it in the browser
    return render_template("index.html", profile = profiles[current_index])