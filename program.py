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
        if request.method == 'POST':
            username = request.forms.get('username', '').strip()
            email    = request.forms.get('email', '').strip().lower()
            password = request.forms.get('password', '')

        # Enkel e‑postvalidering
        if not email or '@' not in email:
            error = 'Ogiltig e‑postadress.'
        elif len(password) < 8:
            error = 'Lösenord måste vara minst 8 tecken.'
        else:
            pw_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO users (username, email, password_hash)
                            VALUES (%s, %s, %s)
                            """,
                            (username, email, pw_hash)
                        )
                        conn.commit()
                        success = 'Registrering lyckades! Du kan nu logga in.'
            except errors.UniqueViolation as e:
                # Avgör om det är username eller email som krockar
                constraint = e.diag.constraint_name or ''
                if 'email' in constraint:
                    error = 'E‑postadressen är redan registrerad.'
                else:
                    error = 'Användarnamnet är upptaget.'
            except Exception as exc:
                error = f'Något gick fel: {exc}'

    return template('register', error=error, success=success)


@route('/login', method='POST')
def login():
    """
    Authenticate user credentials using e-post and set secure cookie.

    Supports AJAX and standard form submissions.

    :form email: user's email
    :form password: user's password
    :return: JSON or redirect/template response
    """
    # Hämta formdata
    email = request.forms.get('email', '').strip().lower()
    password = request.forms.get('password', '').encode('utf-8')

    # Hämta lagrat lösenordsha och användarnamn baserat på e-post
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT username, password_hash
                  FROM users
                 WHERE email = %s
                """,
                (email,)
            )
            user = cur.fetchone()

    # Kontrollera lösenordet
    valid = bool(user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')))

    # AJAX-inloggning
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if valid:
            # Spara username i cookie för att kunna hälsa användaren
            response.set_cookie('account', user['username'], secret=SECRET_KEY, path='/')
            return HTTPResponse(status=200, body=json.dumps({'ok': True}))
        return HTTPResponse(
            status=401,
            body=json.dumps({'ok': False, 'error': 'Fel e-post eller lösenord'})
        )

    # Vanlig form-inloggning
    if valid:
        response.set_cookie('account', user['username'], secret=SECRET_KEY, path='/')
        return redirect('/')
    
    # Ogiltiga uppgifter
    return template(
        'index',
        recipes=[],
        login_error='Fel e-post eller lösenord.',
        login_success=False,
        logout_success=False
    )



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
