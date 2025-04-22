# Grupp 02 – Recept från kylen

## Länk till koden:
https://github.com/Bibbee/Grupp02

# Så här kör du programmet:

1. Installera moduler (om du inte redan har dem), kör följande kommandon i terminalen:

- pip install bottle 
- pip install requests
- m pip install python-dotenv
- m pip install bcrypt

2. Skaffa en API-nyckel:

- Gå till https://spoonacular.com/food-api
- Skapa ett gratis konto
- Hämta din nyckel

3. Skapa en .env fil

- Skapa en fil i samma mapp som program.py som du döper till .env
- Filen ska innehålla följande:
    DB_HOST=xxxxxx
    DB_PORT=xxxx
    DB_NAME=xxxxxxxxx
    DB_USER=xxxxxx
    DB_PASSWORD=xxxxxxxx
    SECRET_KEY=xxxxxxxxxxxxxxxxxxxx
    API_KEY=Din_API_nyckel_här
- Skriv in din API-nyckel Där det står API_KEY i .env filen
- Kontakta någon av gruppmedlemmarna i Recept från kylen för att få mer information

4. Kör programmet:
 
- Klicka på http://localhost:8080/ i terminalen 
- Skriv in t.ex. tomato i textfältet (OBS! ingredienser skrivs på engelska)