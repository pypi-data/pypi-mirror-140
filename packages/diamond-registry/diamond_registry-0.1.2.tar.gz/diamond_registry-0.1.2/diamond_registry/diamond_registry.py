import urllib.request
import mysql.connector as connector
from typing import List, Optional, Any
import csv


#-----------------------------------------OBJECT CLASSES--------------------------------------------

#STORE CLASS
class store:

    def __init__(self, city, country) -> None:
        self._city = city
        self._country = country

    def getCity(self):
        return self._city

    def getCountry(self):
        return self._country
#potential to add more store-specific info like hired staff etc.


#DIAMOND CLASS
class diamond:
    
    def __init__(
        self,
        carat: float,
        cut: str,
        color: str,
        clarity: str,
        depth: float,
        table: float,
        price: int,
        x: float,
        y: float,
        z: float,
        certificates: List[str],
        store: store,
        id: int
    ) -> None:
        self._carat = carat
        self._cut = cut
        self._color = color
        self._clarity = clarity
        self._depth = depth
        self._table = table
        self._price = price
        self._x = x
        self._y = y
        self._z = z
        self._certificates = certificates
        self._store = store
        self._id = id

    def getCarat(self):
        return self._carat

    def getCut(self):
        return self._cut

    def getColor(self):
        return self._color

    def getClarity(self):
        return self._clarity

    def getDepth(self):
        return self._depth

    def getTable(self):
        return self._table

    def getPrice(self):
        return self._price

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def getZ(self):
        return self._z

    def getCertificates(self):
        output = ""
        for certificate in self._certificates:
            output+=f"{certificate},"
        output=output[:-1]
        return output

    def getStore(self):
        return self._store

    def getId(self):
        return self._id



#--------------------------------------------FUNCTIONS-----------------------------------------------

#ATTEMPT CONNECTION WITH PROVIDED CONFIGURATION.
#IF SUCCESSFUL, STORE CONFIGURATION IN CONFIG.TXT FILE.
def configure(
    rdb_host: str,
    rdb_port: int,
    rdb_database: str,
    rdb_username: str,
    rdb_password: str,
) -> None:
    try: 
        #Connect to MySQL database
        connection = connector.connect(
            host=rdb_host,
            database=rdb_database,
            user=rdb_username,
            password=rdb_password) 
            #port is unneccesary for this connection and so no check is made to ensure a valid port is given

        #Store configuration details
        lines = [ 
            f'Host: {rdb_host}\n',
            f'Port: {rdb_port}\n',
            f'Database: {rdb_database}\n',
            f'Username: {rdb_username}\n',
            f'Password: {rdb_password}\n'
        ]
        configFile = open('config.txt','w')
        configFile.writelines(lines)
        configFile.close()
        
        cursor = connection.cursor()

        #Check tables exist and if not, create them
        if _tableNotExist(cursor,rdb_database,'stores'):#checking and creating stores table
            sqlCommand = """CREATE TABLE stores (
                ID INT(11) NOT NULL AUTO_INCREMENT,
                city VARCHAR(80) NOT NULL,
                country VARCHAR(80) NOT NULL,
                PRIMARY KEY (ID)
                );""" #even though there is only 1 store per city (and so city could be used as the primary key), there could be 2 cities with the same name in different countries. I could combine city and country to make a primary key, but doing an ID made things easier and didn't increase the database size by much.
            cursor.execute(sqlCommand)

        if _tableNotExist(cursor,rdb_database,'diamonds'):#checking and creating diamonds table
            sqlCommand = """CREATE TABLE diamonds (
                ID INT(11) NOT NULL AUTO_INCREMENT,
                price SMALLINT,
                carat FLOAT(3,2) NOT NULL,
                cut ENUM('Fair','Good','Very Good','Premium','Ideal') NOT NULL,
                color ENUM('J','I','H','G','F','E','D') NOT NULL,
                clarity ENUM('I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF') NOT NULL,
                x FLOAT(4,2) NOT NULL,
                y FLOAT(4,2) NOT NULL,
                z FLOAT(4,2) NOT NULL,
                depth FLOAT(4,1) NOT NULL,
                table_ FLOAT(4,1) NOT NULL,
                certificates SET('GIA','AGS','GCAL','IGI','EGL'),
                storeID INT(11),
                PRIMARY KEY (ID),
                FOREIGN KEY (storeID) REFERENCES stores(ID)
            );"""
            cursor.execute(sqlCommand)

    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    
#CHECK THAT THE TABLE DOESN'T ALREADY EXIST
def _tableNotExist(cursor, db:str, tableName:str) -> bool:
    sqlCommand = f"""SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = '{db}' 
    AND table_name = '{tableName}';""" #count all tables with the inputted name
    try:
        cursor.execute(sqlCommand)
        foundTable = cursor.fetchone()
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    return foundTable[0]==0 #return true if 0 tables have the inputted name, else false



#ADD A NEW DIAMOND TO THE REGISTRY/DATABASE
def add_diamond(
    carat: float,
    cut: str,
    color: str,
    clarity: str,
    depth: float,
    table: float,
    price: int,
    x: float,
    y: float,
    z: float,
    certificates: List[str],
    store_city: str,
    store_country: str,
    id: Optional[int] = None,
) -> int:
    connection = _connectToDatabase()#connect to database
    cursor = connection.cursor()

    #INPUT CHECKS:
    cut = cut.capitalize()#capitalize first letter, lower case the rest
    if cut not in ['Fair','Good','Very Good','Premium','Ideal']: #check if valid cut
        raise ValueError('Invalid cut entered - only Fair, Good, Very Good, Premium or Ideal accepted')
    color = color.capitalize()#capitalize the letter
    if color not in ['J','I','H','G','F','E','D']:
        raise ValueError('Invalid color entered - only J, I, H, G, F, E or D accepted')
    clarity = clarity.upper()#capitalize the input
    if clarity not in ['I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF']:
        raise ValueError('Invalid clarity entered - only I1, SI2, SI1, VS2, VS1, VVS2, VVS1 or IF accepted')
    for i in range(len(certificates)):
        certificates[i]=certificates[i].upper()#capitalize the input
        if certificates[i] not in ['GIA','AGS','GCAL','IGI','EGL']:
            raise ValueError('Invalid certificate entered - only GIA, AGS, GCAL, IGI or EGL accepted')
    store_city=store_city.capitalize()#capitalize first letter, lower case the rest
    store_country=store_country.capitalize()#capitalize first letter, lower case the rest

    currentStore = store(store_city,store_country)#create a store with given info
    diamondToAdd = diamond(carat,cut,color,clarity,depth,table,price,x,y,z,certificates,currentStore, id)#create a diamond with given info
    
    if id != None: #if the ID was provided
        if _isIdUnique(cursor,id):#and the ID doesn't already exist in the database
            _addDiamondToDatabase(cursor, diamondToAdd,id)#add the diamond to the database
            connection.commit()
            connection.close()
        else:#if the ID already exists in the database
            raise ValueError('ID already exists in database')#throw a ValueError
    else:#if the ID was not provided
        _addDiamondToDatabase(cursor, diamondToAdd)#add the diamond to the database with an autogenerated ID
        connection.commit()
        sqlCommand = """SELECT LAST_INSERT_ID();"""#get the ID of the last added entry
        try:
            cursor.execute(sqlCommand)
            id = cursor.fetchone()[0]
        except connector.Error as e:
            print('Error while connecting to MySQL: ', e)
        connection.close()
    return id

#ADD GIVEN DIAMOND TO THE DATABASE
def _addDiamondToDatabase(cursor, diamond:diamond, id=None):
    storeId = _getStoreID(cursor,diamond.getStore().getCity(),diamond.getStore().getCountry())#retrieve the ID of the store from the database
    
    if storeId == None:#if the store doesn't exist in the database, add it
        sqlCommand = f"""INSERT INTO stores (city,country)
        VALUES ('{_fixApostrophe(diamond.getStore().getCity())}',
        '{_fixApostrophe(diamond.getStore().getCountry())}');"""#insert the store into the database with an autogenerated ID
        try:
            cursor.execute(sqlCommand)
            sqlCommand = """SELECT LAST_INSERT_ID();"""#get the ID of the last added entry
            cursor.execute(sqlCommand)
            storeId = cursor.fetchone()
        except connector.Error as e:
            print('Error while connecting to MySQL: ', e)

    if id==None:#If no diamond ID was specified
        sqlCommand = f"""INSERT INTO diamonds (price, carat, cut, color, clarity, x, y, z, depth, table_, certificates, storeID)
        VALUES ({diamond.getPrice()},
        {diamond.getCarat()},
        '{diamond.getCut()}',
        '{diamond.getColor()}',
        '{diamond.getClarity()}',
        {diamond.getX()},
        {diamond.getY()},
        {diamond.getZ()},
        {diamond.getDepth()},
        {diamond.getTable()},
        '{diamond.getCertificates()}',
        '{storeId[0]}');"""#insert diamond into the database with an autogenerated ID
    else:#If a diamond ID was specified
        sqlCommand = f"""INSERT INTO diamonds
            VALUES ({diamond.getId()},
            {diamond.getPrice()},
            {diamond.getCarat()},
            '{diamond.getCut()}',
            '{diamond.getColor()}',
            '{diamond.getClarity()}',
            {diamond.getX()},
            {diamond.getY()},
            {diamond.getZ()},
            {diamond.getDepth()},
            {diamond.getTable()},
            '{diamond.getCertificates()}',
            '{storeId[0]}');"""#insert diamond into database
    try:
        cursor.execute(sqlCommand)
    except connector.Error as e:
            print('Error while connecting to MySQL: ', e)

#CHECKS THAT THE GIVEN DIAMOND ID NUMBER DOESN'T ALREADY EXIST IN THE DATABASE
def _isIdUnique(cursor,id:int) -> bool:
    sqlCommand = f"SELECT COUNT(*) FROM diamonds WHERE ID={id}"#count all the entries with the given ID number
    try:
        cursor.execute(sqlCommand)
        result = cursor.fetchone()
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    return result[0]==0 #if the count os 0, return True

#GETS THE ID THAT MATCHES THE GIVEN STORE INFO
def _getStoreID(cursor, city:str, country:str):
    sqlCommand = f"""SELECT ID FROM stores WHERE 
    city='{_fixApostrophe(city)}' AND 
    country='{_fixApostrophe(country)}';"""
    result = None
    try:
        cursor.execute(sqlCommand)
        result = cursor.fetchone()
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    return result

#CONNECT TO THE CONFIGURED DATABASE AND RETURN THE CONNECTION
def _connectToDatabase() -> connector:
    #Get configuration data from file
    file = open('config.txt','r') 
    lines = file.readlines()
    file.close()

    rdb_host = lines[0].split(': ')[1].rstrip()
    rdb_port = lines[1].split(': ')[1]#port information not neccessary for this connection
    rdb_database = lines[2].split(': ')[1].rstrip()
    rdb_username = lines[3].split(': ')[1].rstrip()
    rdb_password = lines[4].split(': ')[1].rstrip()

    #Attempt connection
    try:
        connection = connector.connect(
                host=rdb_host,
                database=rdb_database,
                user=rdb_username,
                password=rdb_password)

        cursor = connection.cursor()
        #Check if tables exist and if not, create them
        if _tableNotExist(cursor,rdb_database,'stores'):#checking and creating stores table
            sqlCommand = """CREATE TABLE stores (
                ID INT(11) NOT NULL AUTO_INCREMENT,
                city VARCHAR(80) NOT NULL,
                country VARCHAR(80) NOT NULL,
                PRIMARY KEY (ID)
                );"""
            cursor.execute(sqlCommand)

        if _tableNotExist(cursor,rdb_database,'diamonds'):#checking and creating diamonds table
            sqlCommand = """CREATE TABLE diamonds (
                ID INT(11) NOT NULL AUTO_INCREMENT,
                price SMALLINT,
                carat FLOAT(3,2) NOT NULL,
                cut ENUM('Fair','Good','Very Good','Premium','Ideal') NOT NULL,
                color ENUM('J','I','H','G','F','E','D') NOT NULL,
                clarity ENUM('I1','SI2','SI1','VS2','VS1','VVS2','VVS1','IF') NOT NULL,
                x FLOAT(4,2) NOT NULL,
                y FLOAT(4,2) NOT NULL,
                z FLOAT(4,2) NOT NULL,
                depth FLOAT(4,1) NOT NULL,
                table_ FLOAT(4,1) NOT NULL,
                certificates SET('GIA','AGS','GCAL','IGI','EGL'),
                storeID INT(11),
                PRIMARY KEY (ID),
                FOREIGN KEY (storeID) REFERENCES stores(ID)
            );"""
            cursor.execute(sqlCommand)

        return connection
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)


#GETS ALL MATCHING DIAMONDS FROM THE DATABASE.
# If only country is provided, matching diamonds from all stores within that country is returned.
def get_diamonds(
    store_city: Optional[str] = None,
    store_country: Optional[str] = None,
    required_certificates: Optional[List[str]] = None,
) -> List[Any]:
    connection = _connectToDatabase()#connect to the database
    cursor = connection.cursor()

    if store_city!=None: store_city=store_city.capitalize()#capitalize first letter, lower case the rest
    if store_country!=None: store_country=store_country.capitalize()#capitalize first letter, lower case the rest
    for i in range(len(required_certificates)):
        required_certificates[i]=required_certificates[i].upper()#capitalize the input

    if (store_city == None and store_country == None): #if no store was given or found in the database
        if required_certificates == None: #and no certificates given
            sqlCommand = """SELECT * FROM diamonds;""" #get all diamonds from the database
        else:#if only certificates were provided
            sqlCommand = """SELECT * FROM diamonds WHERE"""
            for cert in required_certificates:
                sqlCommand += f" certificates LIKE '%{cert}%' AND"
            sqlCommand = sqlCommand[:-3] + ";" #get all diamonds that have all the listed certificates
    elif  _getAllMatchingStoreIDs(cursor, store_city, store_country)==[]:#if store info was provided but the store doesn't exist in the database
        return []
    else:#if store info was provided and the store exists
        storeIDs = _getAllMatchingStoreIDs(cursor, store_city, store_country)#get the IDs of the stores that match (multiple IDs if only country was provided)
        sqlCommand = """SELECT * FROM diamonds WHERE ("""
        for store in storeIDs: #loop through all the storeID options
            sqlCommand+=f" storeID={store[0]} OR"
        sqlCommand = sqlCommand[:-2] + ")"
        if required_certificates != None:#if certificates were also provided
            sqlCommand+=" AND "
            for cert in required_certificates:
                sqlCommand += f" certificates LIKE '%{cert}%' AND"
            sqlCommand = sqlCommand[:-3]
        sqlCommand += ";"#match all certificates listed
    
    cursor.execute(sqlCommand)
    results = cursor.fetchall()

    fields = ['id','diamond'] #set up lables, 'id' was requested as a lable
    allDiamonds = []

    for entry in results:#for each result, store the diamond object and it's id in a dictionary format
        (id,price,carat,cut,color,clarity,x,y,z,depth,table,certificates,storeID) = entry
        currentDiamond = diamond(carat,cut,color,clarity,depth,table,price,x,y,z,certificates,_getStore(cursor,storeID),id)
        diamondWithID = dict(zip(fields,[id,currentDiamond]))
        allDiamonds.append(diamondWithID)
    connection.close()

    return allDiamonds

#RETURN STOREIDS FOR ALL STORES THAT MATCH THE CITY/COUNTRY INFO PROVIDED
def _getAllMatchingStoreIDs(cursor, city : str, country : str) -> List[int]:
    sqlCommand = """SELECT ID FROM stores WHERE """
    if city != None:
        sqlCommand += f"city='{_fixApostrophe(city)}'"
    if city != None and country != None:
        sqlCommand += " AND "
    if country != None:
        sqlCommand += f"country='{_fixApostrophe(country)}'"
    sqlCommand+=";"
    results = []
    try:
        cursor.execute(sqlCommand)
        results = cursor.fetchall()
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    return results

#RETURN STORE OBJECT FROM GIVEN STORE ID
def _getStore(cursor, id : int) -> store:
    sqlCommand = f"""SELECT city, country FROM stores WHERE ID={id}"""
    try:
        cursor.execute(sqlCommand)
        (city,country) = cursor.fetchone()
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    return store(city,country)


#DELETES ALL TABLES AND DATA FROM THE SYSTEM
def delete_all() -> None: 
    connection = _connectToDatabase()
    cursor = connection.cursor()
    sqlCommand1 = """DROP TABLE diamonds;"""
    sqlCommand2 = """DROP TABLE stores;"""
    try:
        cursor.execute(sqlCommand1)
        cursor.execute(sqlCommand2)
    except connector.Error as e:
        print('Error while connecting to MySQL: ', e)
    connection.close()


#IMPORT DATA FROM REMOTE URL
def batch_import(
    url: str
) -> None:
    response = urllib.request.urlopen(url)#connect to the given url
    lines = [l.decode('utf-8') for l in response.readlines()]
    cr = csv.reader(lines)#read the csv file
    iterCr = iter(cr)
    fields = next(iterCr)
    connection = _connectToDatabase()#connect to database
    cursor = connection.cursor()
    for row in cr:#for each row in the file
        certificates = row[11].split(',')#split the line up into data pieces
        currentStore = store(row[12],row[13])#create a store object
        diamondToAdd = diamond(float(row[1]),row[2],row[3],row[4],float(row[5]),float(row[6]),int(row[7]),float(row[8]),float(row[9]),float(row[10]),certificates,currentStore,int(row[0]))#create a diamond object
        _addDiamondToDatabase(cursor, diamondToAdd)#add diamond to database
        connection.commit()
    connection.close()

#CHANGES SINGLE APOSTROPHES INTO DOUBLE APOSTROPHES TO ABIDE WITH SQL TEXT FORMAT (AND PREVENT SQL INJECTION)
def _fixApostrophe(word: str) -> str:
    if "'" in word:#if there is at least one apostrophy
        parts = word.split("'")#split on the apostrophies
        word = parts[0]
        for section in parts[1:]:
            word = word+"''"+section#and rejoin with double apostrophies instead of a single apostrophy
    return word

print(get_diamonds(store_city="Tol'yatti", required_certificates=['IGI','GIA'])[0]['id'])