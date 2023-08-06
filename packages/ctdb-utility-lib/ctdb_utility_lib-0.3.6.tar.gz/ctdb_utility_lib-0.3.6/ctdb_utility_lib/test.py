from datetime import date, datetime
import utility
import admin_utility

conn = utility.connect_to_db()

email1 = "ahmed@fake.com"
email2 = "ahmed2@fake.com"
room = "room1"

print(admin_utility.get_contacts(email1,datetime.now(),conn))
#cur.close()
conn.close()
