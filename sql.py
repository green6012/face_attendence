import sqlite3
from datetime import datetime
now = datetime.now()

current_time = now.strftime("%H:%M %d/%m/%Y")
print("Current Time =", current_time)

# conn = sqlite3.connect('btl.db')
# c = conn.cursor()
# c.execute("SELECT * FROM sinhvien")
# #print(c.fetchall())
# conn.commit()
# conn.close()