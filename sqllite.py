import sqlite3

connection = sqlite3.connect('student.db')

cursor = connection.cursor()

table_info="""
CREATE TABLE STUDENT(NAME VARCHAR(20),CLASS VARCHAR(20),SECTION VARCHAR(20),MARKS INTEGER)
"""
cursor.execute(table_info)

cursor.execute("INSERT INTO STUDENT VALUES('JOHN','10','A',85)")
cursor.execute("INSERT INTO STUDENT VALUES('MARY','10','B',90)")
cursor.execute("INSERT INTO STUDENT VALUES('DAVID','10','A',78)")
cursor.execute("INSERT INTO STUDENT VALUES('SARA','10','B',92)")
cursor.execute("INSERT INTO STUDENT VALUES('MIKE','10','A',80)")

print("Data inserted successfully")
data = cursor.execute("SELECT * FROM STUDENT")
for row in data:
    print(row)
    
connection.commit()
connection.close()