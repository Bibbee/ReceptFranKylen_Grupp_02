# Grupp 02 – Recept från kylen

## Länk till koden:  
https://github.com/Bibbee/Grupp02

---

## Så här kör du programmet

### 1. Installera nödvändiga moduler  
Öppna terminalen och kör följande kommandon för att installera de moduler som behövs:

- pip install bottle  
- pip install requests  
- python -m pip install python-dotenv 
- python -m pip install bcrypt  

---

### 2. Skaffa en API-nyckel  
För att kunna använda API:et behöver du en nyckel:

- Gå till https://spoonacular.com/food-api  
- Skapa ett gratis konto  
- Kopiera din API-nyckel  

---

### 3. Skapa en `.env`-fil  
Gör följande:

- Skapa en fil i samma mapp som `program.py` och döp den till `.env`  
- Klistra in följande innehåll i filen:

  DB_HOST=xxxxxx  
  DB_PORT=xxxx  
  DB_NAME=xxxxxxxxx  
  DB_USER=xxxxxx  
  DB_PASSWORD=xxxxxxxx  
  SECRET_KEY=xxxxxxxxxxxxxxxxxxxx  
  API_KEY=Din_API_nyckel_här  

- Byt ut `Din_API_nyckel_här` mot din riktiga API-nyckel från https://spoonacular.com/food-api  
- Kontakta någon i gruppen om du behöver mer information  

---

### 4. Starta programmet  
Så här kör du programmet:

- Starta servern genom att köra programmet  
- Öppna http://localhost:8080/ i din webbläsare  
- Skriv in en ingrediens, till exempel `tomato`, i sökfältet  

**Obs!** Ingredienser måste skrivas på engelska
