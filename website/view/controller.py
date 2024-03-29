#Program by Ilusha Rathnayake, Rehmat Raju, Tejus Revi
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import Context

import pymongo

'''Stores all movies in DB'''
listOfMovies = []
'''Stores details like all possible genres, languages etc needed for filtering'''
metadata = {
    'genres': [],
    'languages': [],
    'maxYear': 0,
    'minYear': 0,
    'maxRuntime': 0
}

PASSWORD = "team20"
DATABASE_NAME = "testDB"
myclient = pymongo.MongoClient("mongodb+srv://tejus:"+PASSWORD+"@cluster0.ymzum.gcp.mongodb.net/"+DATABASE_NAME+"?retryWrites=true&w=majority")
mydb = myclient["testDB"]
mycol = mydb["testCollection"]

#cursorOfMovies is a cursor object that stores all movies from DB
cursorOfMovies = mycol.find() # select * from DB where Name = 1

for movie in cursorOfMovies:
    listOfMovies.append(movie)

    for genre in movie["Genre"]:
        if genre not in metadata.get('genres'):
            metadata['genres'].append(genre)
    for genre in movie["Language"]:
        if genre not in metadata.get('languages'):
            metadata['languages'].append(genre)
    if movie["Year"] > metadata["maxYear"]:
         metadata["maxYear"] = movie["Year"]
    if movie["Year"] < metadata["minYear"] or metadata["minYear"] == 0:
         metadata["minYear"] = movie["Year"]
    if movie["Runtime"] > metadata["maxRuntime"]:
         metadata["maxRuntime"] = movie["Runtime"]

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
    context = {"listOfMovies":listOfMovies, "metadata": metadata}
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

#<---------------------------------------TODO-------------------------------------------->
def filter_list(request):
    #Dictionary to store our database query
    myQuery = {}

    if request.GET.get('genre') != "":
        myQuery['Genre'] = request.GET.get('genre')
    if request.GET.get('minYear') != "" and request.GET.get('maxYear') != "":
        myQuery['Year'] = {"$gte": int(request.GET.get('minYear')), "$lte": int(request.GET.get('maxYear'))}
    elif request.GET.get('minYear') != "":
        myQuery['Year'] = {"$gte": int(request.GET.get('minYear'))}
    elif request.GET.get('maxYear') != "":
        myQuery['Year'] = {"$lte": int(request.GET.get('maxYear'))}
    if request.GET.get('maxRuntime') != "":
        myQuery['Runtime'] = {"$lte": int(request.GET.get('maxRuntime'))}
    if request.GET.get('language') != "":
        myQuery['Language'] = request.GET.get('language')
    print(myQuery)
    cursor = mycol.find(myQuery)

    #Convert cursor to list
    newList = [movie for movie in cursor]


    context = {"listOfMovies":newList, "metadata": metadata}
    response = render(request, 'index.html', context)
    return response
