import requests
from bs4 import BeautifulSoup

BASE_URL = "http://185.244.219.162/phpmyadmin"
LOGIN_URL = f"{BASE_URL}/index.php"
DB_NAME = "testDB"
TABLE_NAME = "users"

USERNAME = "test"
PASSWORD = "JHFBdsyf2eg8*"
session = requests.Session()

def get_token_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    token_input = soup.find("input", {"name": "token"})
    return token_input["value"] if token_input else None

#Получаем страницу логина
resp = session.get(LOGIN_URL)
token = get_token_from_html(resp.text)

# Логинимся
payload = {
    "pma_username": USERNAME,
    "pma_password": PASSWORD,
    "server": 1,
    "target": "index.php",
    "token": token,
}
resp = session.post(LOGIN_URL, data=payload)

if "phpMyAdmin" not in resp.text:
    raise Exception("Ошибка авторизации!")

print("Авторизация успешна")

# Переходим в базу testDB
db_url = f"{BASE_URL}/index.php?route=/database/structure&server=1&db={DB_NAME}"
resp = session.get(db_url)
token = get_token_from_html(resp.text)

# Делаем SQL-запрос на таблицу users
sql_url = f"{BASE_URL}/index.php"
params = {
    "route": "/sql",
    "server": 1,
    "db": DB_NAME,
    "table": TABLE_NAME,
    "pos": 0,
}
data = {
    "token": token,
    "sql_query": f"SELECT * FROM `{TABLE_NAME}`;",
}

resp = session.post(sql_url, params=params, data=data)
soup = BeautifulSoup(resp.text, "html.parser")

table = soup.find("table", {"class": "table_results"})
if not table:
    raise Exception("Не удалось получить данные из таблицы")


# Парсим заголовки
rows = table.find_all("tr")
headers = [th.text.strip() for th in rows[0].find_all("th")]

# Выводим результат
print("\nДанные таблицы users:")

# Парсим заголовки
headers = []
for th in table.find_all("th", {"data-column": True}):
    headers.append(th["data-column"])

print(headers)
for row in rows[1:]:
    # Берем только ячейки, где есть атрибут data-type (это реальные данные)
    data_cells = row.find_all("td", {"data-type": True})
    values = [td.text.strip() for td in data_cells]
    print(values)


