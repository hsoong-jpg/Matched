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
#when user visits page run index()
def index():
    #global bc you arent creating a new index 
    global current_index
    #stops if user runs out of profiles
    if current_index >= len(profiles):
        return "No more profiles"
    
    #Trender_template("index.html") Go find a file called index.html in the templates folder and show it in the browser
    return render_template("index.html", profile = profiles[current_index])

#When someone visits the like page (POST = hits the like button)
@app.route("/like", methods=["POST"])
def like():
    global current_index
    #gets current user 
    profile = profiles[current_index]
    #adds user to like lsit 
    likes.append(profile)
    #move to next profile 
    current_index += 1
    #redirects back to home page 
    return redirect("/")

#When someone vists the pass page (POST = hits pass button)
@app.route("/pass", methods=["POST"])
def skip():
    global current_index
    current_index += 1
    return redirect("/")

#When someone visits the likes page (No Post bc just viewing data)
@app.route("/likes")
def show_likes():
    #return data in JSON format 
    return {"liked_profiles": likes}

if __name__ == "__main__":
    app.run(debug=True)