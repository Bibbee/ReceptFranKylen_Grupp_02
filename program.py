from bottle import route, run, template, request, static_file 
import requests

API_KEY = '' # 1. fyll i din unika API-nyckel här. 
             # 2. Skaffa gratis nyckel genom att skapa ett konto på:
             # 3. https://spoonacular.com/food-api
             # 4. gör inte för många anrop, du har ca 150pts/dag (gratisplan)
             # 5. lek runt lite, stylea (css) sidan.
             

@route('/')
def index():
    """Returnerar startsidan med ett textfält där användaren kan mata in
    ingredienser."""
    return template('index', recipes=[])

@route('/', method='POST')
def get_recipes():
    
    """Skickar en förfrågan till Spoonacular API för att hämta recept som matchar
    användarens ingredienser."""
    
    ingredients = request.forms.get('ingredients')
    url = 'https://api.spoonacular.com/recipes/findByIngredients'
    params = {
        'ingredients': ingredients,
        'number': 5,
        'apiKey': API_KEY
    }
    """parms är en dictionary i python som innehåller alla frågeparametrar
    som skickas med i ett API-anrop via URL:en"""

    response = requests.get(url, params=params)
    recipes = response.json() if response.status_code == 200 else []
    return template('index', recipes=recipes)

@route('/static/<filename>')
def serve_static(filename):
    return static_file(filename, root='./static')

run(host='localhost', port=8080, debug=True)