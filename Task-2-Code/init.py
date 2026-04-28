# python file to create databases and test them with sqlite3

conn = sqlite3.connect("enquiry.db")

cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS enquiry (name TEXT, email TEXT, message TEXT)')
cur.execute("INSERT INTO enquiry VALUES ('testname', 'test@email.com', 'testmessage')")
conn.commit()

cur.execute('SELECT * FROM enquiry')
result = cur.fetchone()
print(f'User: {result[0]}, Email: {result[1]}, Message: {result[2]}')

con = sqlite3.connect("users.db")

c = con.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL)')

con.commit()

con.close()