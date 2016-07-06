
import psycopg2

#def patient_loader:

class OHDSILoader:

    def __init__ (self, dbname, user, password):
        self.dbname = dbname
        self.user = user
        self.password = password


    def load(self):
        conn_string = "dbname='" + self.dbname + "' user = '" + self.user + "' password = '" + self.password + "'"
        self.conn = psycopg2.connect(conn_string)
        print("Connecting to database -> %s " % (conn_string))

    def excuteSQL(self, query):
        cur = self.conn.cursor()
        cur.execute (query)
        return cur.fetchall()


'''
visits = []
for record in records:
    visit = ICUVisit( record.subje )
    visits.append( )
    print(record)


class ICUVisit:
    def __init__( self, visit_id ):
        self.visit_id = visit_id

'''


