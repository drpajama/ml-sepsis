
import psycopg2
import VisitOccurence
import CareSite

class OHDSIConnection:
    visits = None
    care_sites = None

    def __init__ (self, dbname, user, password):
        self.initialized = False
        self.dbname = dbname
        self.user = user
        self.password = password

    def initialize(self):
        conn_string = "dbname='" + self.dbname + "' user = '" + self.user + "' password = '" + self.password + "'"
        self.conn = psycopg2.connect(conn_string)
        print("Connecting to database -> %s " % (conn_string))
        self.care_sites = self.get_caresites()
        self.initialized = True

    def excuteSQL(self, query):
        cur = self.conn.cursor()
        cur.execute (query)
        return cur.fetchall()

    def get_visit_occurence_raw(self):
        if self.initialized == False:
            return []
        return self.excuteSQL("SELECT * from ohdsi.visit_occurrence")

    def get_caresites_raw(self):
        return self.excuteSQL("SELECT * from ohdsi.care_site")

    def get_caresites(self):
        if (self.care_sites != None):
            return self.care_sites

        data = self.get_caresites_raw()
        sites = []

        for single_site in data:

            #concept_id = single_site[2]
            site = CareSite.CareSite (
                site_id = single_site[0],
                site_name = single_site[1],
                site_concept_id = single_site[2],
                site_source_value = single_site[5]
            )
            sites.append (site)

        self.care_sites = sites
        return sites

    def get_visit_occurence(self):
        if (self.visits != None):
            return self.visits

        data = self.get_visit_occurence_raw()
        visits = []

        for single_visit_data in data:

            # single_visit_data[2] is concept_id for 'inpatient visit (9201), which is obvious when building an object for ICUVisit

            site = CareSite.get_site_by_name( self.care_sites, single_visit_data[9] )

            visit = VisitOccurence.ICUVisit (
                visit_id = single_visit_data[0],
                person_id = single_visit_data[1],
                start_date = single_visit_data[3],
                start_time = single_visit_data[4],
                end_date = single_visit_data[5],
                end_time = single_visit_data[6],
                care_site = site
            )
            visits.append(visit)

        self.visits = visits
        return visits

    def get_all_visits_by_patient_id(self, person_id):
        self.get_visit_occurence()
        visits_by_patient = []

        for visit in self.visits:
            if visit.person_id ==



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


