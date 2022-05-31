import requests
import requests.exceptions
import mysql.connector
from mysql.connector import errorcode
from bs4 import BeautifulSoup
import re

try:
    cnx = mysql.connector.connect(user = 'root',
                                  password = '',
                                  host = '127.0.0.1',
                                  database = 'cars')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit(1)

cursor = cnx.cursor()

count = 0
pagenum = 1

brand = input("please insert car brand:\n")
model = input("please insert car model:\n")

tablename = brand+'_'+model
try:
    print('creating table:')
    cursor.execute('CREATE TABLE %s (milage VARCHAR(50) , price VARCHAR(50))' %tablename)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
        print("table already exists. it will be upgraded:")
        cursor.execute("TRUNCATE %s" %tablename)
    else:
        print(err.msg)
        exit(1)

while count < 20:
    url = 'https://bama.ir/car/'+brand+'/'+model+'/all-trims?instalment=0&page='+str(pagenum)

    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as ece:
        print("Connection Error:", ece)
        exit(1)
    except requests.exceptions.Timeout as et:
        print("Timeout Error:", et)
        exit(1)
    except requests.exceptions.RequestException as e:
        print("Some Ambiguous Exception:", e)
        exit(1)

    print("\npage %i:" %pagenum)
    soup = BeautifulSoup(response.text, "html.parser")
    allCars = soup.find_all("li", attrs={"itemtype": "http://schema.org/Car"})
    for car in allCars:
        if (car.find("p", attrs={"class":"cost", "content":"0"}) or car.find('span', attrs={'itemprop':"price", "content":"0"})) \
            or (('در توضیحات' in car.text) or ('تماس بگیرید' in car.text)):
            pass
        else:
            milage = car.find("p" ,attrs={"class":"price milage-text-mobile visible-xs price-milage-mobile"})
            if milage is None :
                pass
            else:
                milage = re.sub(r'\s+',' ',milage.text).strip()
                price = car.find("p", attrs={"class":"cost"})
                price = re.sub(r'\s+',' ',price.text).strip()
                print('inserting valuse %s , %s into tabel %s' %(milage,price,tablename))
                cursor.execute('INSERT INTO %s VALUES (\'%s\',\'%s\')' %(tablename,milage,price))
                cnx.commit()
                count+=1
                if count >= 20:
                    break
    pagenum+=1

cursor.close()
cnx.close()