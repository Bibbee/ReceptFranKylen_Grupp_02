from bottle import route, run, template, request, static_file, response, redirect, HTTPResponse, TEMPLATE_PATH
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
import requests
import os
from dotenv import load_dotenv
import psycopg2
import bcrypt
import json

# Configure template directory and environment variables
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH.insert(0, os.path.join(BASE_DIR, 'views'))
load_dotenv()

API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')


def get_db_connection():
    """
    Create a new database connection using environment settings.

    :return: psycopg2 connection with RealDictCursor factory
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )


@route('/')
def index():
    """
    Render the home page with optional login/logout messages.

    Query parameters:
    - login=1 to show login success
    - logout=1 to show logout success

    :return: rendered index template
    """
    recipes = []
    login_success = request.query.login == '1'
    logout_success = request.query.logout == '1'

    return template(
        'index',
        recipes=recipes,
        login_success=login_success,
        logout_success=logout_success,
        login_error=None
    )


@route('/', method='POST')
def get_recipes():
    """
    Fetch recipes from Spoonacular API based on user‐provided ingredients.
    """
    ingredients = request.forms.get('ingredients')
    url = 'https://api.spoonacular.com/recipes/findByIngredients'
    params = {
        'ingredients': ingredients,
        'number': 20,
        'apiKey': API_KEY
    }

    resp = requests.get(url, params=params)
    recipes = resp.json() if resp.status_code == 200 else []

    # pass the same four variables that index() does
    return template(
        'index',
        recipes=recipes,
        login_success=False,
        logout_success=False,
        login_error=None
    )



@route('/register', method=['GET', 'POST'])
def register():
    """
    Handle user registration, hashing passwords and storing new users.

    :GET: render registration form
    :POST: create a new user with hashed password
    :return: rendered register template with success or error message
    """
    error = None
    success = None

    if request.method == 'POST':
        username = request.forms.get('username', '').strip()
        password = request.forms.get('password', '')

        # Enforce minimum password length
        if len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        else:
            pw_hash = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')

            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                            (username, pw_hash)
                        )
                        conn.commit()
                        success = 'Registration successful! You can now log in.'
            except errors.UniqueViolation:
                error = 'Username is already taken.'
            except Exception as exc:
                error = f'Registration error: {exc}'

    return template('register', error=error, success=success)


@route('/login', method='POST')
def login():
    """
    Authenticate user credentials and set secure cookie.

    Supports AJAX and standard form submissions.

    :form username: user's username
    :form password: user's password
    :return: JSON or redirect/template response
    """
    username = request.forms.get('username', '').strip()
    password = request.forms.get('password', '').encode('utf-8')

    # Retrieve stored password hash
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM users WHERE username = %s", (username,)
            )
            user = cur.fetchone()

    valid = bool(user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')))

    # AJAX login
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if valid:
            response.set_cookie('account', username, secret=SECRET_KEY, path='/')
            return HTTPResponse(status=200, body=json.dumps({'ok': True}))
        return HTTPResponse(status=401, body=json.dumps({'ok': False, 'error': 'Invalid credentials'}))

    # Standard form login
    if valid:
        response.set_cookie('account', username, secret=SECRET_KEY, path='/')
        return redirect('/')

    return template('index', recipes=[], login_error='Incorrect username or password.')


@route('/logout')
def logout():
    """
    Clear the user session cookie and redirect to home.

    :return: redirect to index with logout confirmation
    """
    response.delete_cookie('account', path='/')
    return redirect('/?logout=1')


@route('/static/<filepath:path>')
def serve_static(filepath):
    """
    Serve static files from the ./static directory.

    :param filepath: relative path to the static asset
    :return: File response
    """
    return static_file(filepath, root='./static')


if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True)
