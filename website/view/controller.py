#Program by Tejus Revi
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import Context
import pymongo


listOfMovies = []
PASSWORD = "team20"
DATABASE_NAME = "testDB"
myclient = pymongo.MongoClient("mongodb+srv://tejus:"+PASSWORD+"@cluster0.ymzum.gcp.mongodb.net/"+DATABASE_NAME+"?retryWrites=true&w=majority")
mydb = myclient["testDB"]
mycol = mydb["testCollection"]

#cursorOfMovies is a cursor object that stores all movies from DB
cursorOfMovies = mycol.find()

for movie in cursorOfMovies:
    listOfMovies.append(movie)

def getSimiliarMovies(genres, countries, imdbid):
    eligibleMovies = {}
    for genre in genres:
        moviesMatchingGenre = mycol.find({"Genre":genre})
        for cursor in moviesMatchingGenre:
            if cursor["imdbID"] != imdbid:
                if cursor["imdbID"] in eligibleMovies.keys():
                    eligibleMovies[cursor["imdbID"]] += 1
                else:
                    eligibleMovies[cursor["imdbID"]] = 1
    for country in countries:
        moviesMatchingCountry = mycol.find({"Country":country})
        for cursor in moviesMatchingCountry:
            if cursor["imdbID"] != imdbid:
                if cursor["imdbID"] in eligibleMovies.keys():
                    eligibleMovies[cursor["imdbID"]] += 2
                else:
                    eligibleMovies[cursor["imdbID"]] = 2        
    ls = [ i[0] for i in sorted([(k,v) for k,v in eligibleMovies.items()], key= lambda x: x[1], reverse=True)][0:7]
    returnCursor = mycol.find({"imdbID":{'$in':ls}})
    returnList = []
    for id in returnCursor:
        returnList.append(id)
    return returnList




def View(request):
    context = {"listOfMovies":listOfMovies}
    response = render(request, 'index.html', context)
    return response

def navigate_to_movie(request):
    imdbid = request.GET.get('key', '')
    movie = mycol.find_one({ "imdbID": imdbid })
    listOfSimiliarMovies = getSimiliarMovies(movie["Genre"], movie["Country"], imdbid)
    context = {"movie":movie, "similiarMovies":listOfSimiliarMovies}
    response = render(request, 'movie.html', context)
    return response

def view_database(request):
    context = {"listOfMovies":listOfMovies}
    response = render(request, 'database.html', context)
    return response
