from pprint import pprint
import requests

# SET YOUR OWN TOKEN. Instructions are here - https://the-one-api.dev/documentation
token = ""
my_headers = ""
#----------------------------------------------------------------------------------

#An example of how to use the code.
def main():
    set_token(open("token.txt", 'r').readline())
    pprint(get_quotes(1)[0])
    pprint(get_characters(race = "Elf"))

#Get a character's info. Can use filters - name, race, gender.
def get_characters(name="", race="", gender=""):
    additions = "/character"
    if(name):
        additions += f"?name={name}"
    if(race):
        additions += f"?race={race}"
    if(gender):
        additions += f"?gender={gender}"
    response = requests.get('https://the-one-api.dev/v2' +
                            additions, headers=my_headers).json()["docs"]
    return response

#Get a book's info. Can use filters - book number, ie - "1" for The Fellowship.
def get_books(num=0):
    additions = "/book"
    response = requests.get('https://the-one-api.dev/v2' +
                            additions, headers=my_headers).json()["docs"]
    if(num > 0 and num < 4):
        response = response[num-1]
    return response


def get_quotes(movie_num = 0):
    additions = "/quote"
    t = ""
    if(movie_num):
        if(movie_num == 1):
            t= "Fellowship"
        elif(movie_num == 2):
            t= "Towers"
        elif(movie_num == 3):
            t= "King"
        movie_id = requests.get('https://the-one-api.dev/v2' +
                                "/movie", headers=my_headers).json()["docs"]
        for a in movie_id:
            if(t in a["name"]):
                movie_id = a["_id"]
        additions = f"/movie/{movie_id}/quote"
        response = requests.get('https://the-one-api.dev/v2' +
                                additions, headers=my_headers).json()["docs"]
    else:
        response = requests.get('https://the-one-api.dev/v2' +
                                additions, headers=my_headers).json()["docs"]
    return response


def set_token(t):
    global token, my_headers
    token = t
    my_headers = {'Authorization': f'Bearer {token}'}


if __name__ == "__main__":
    main()
