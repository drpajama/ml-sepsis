
import psycopg2
from VisitOccurence import ICUVisit
import CareSite
from datetime import timedelta
from datetime import datetime
from datetime import date

SINGLE_VISIT, VISIT, PATIENTS, VISITS = range(4)

class Echo:

    talking = True

    care_sites = None
    focus = None
    visits_interested = None
    patients_interested = None
    cursors_interested = None
    db_connect = None

    def __init__ (self, db_connect):
        self.db_connect = db_connect
        self.care_sites = self.get_caresites()
        self.focus = Focus()

    def hello_echo(self):

        if ( self.talking == False ):
            print("\n-------")
            print('You: "Hello Echo!"')
            print("Echo: ...... \n")
        else:
            print("\n-------")
            print('"You: Hello Echo!"')
            print('"Echo: Hello Echo!"\n')

    def shutup(self):
        print('Echo: Okay. No more talking.')
        self.talking = False

        if (self.focus != None):
            self.focus.talking = False

    def excuteSQL(self, query):
        cur = self.db_connect.cursor()
        cur.execute (query)
        return cur.fetchall()

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


    def get_all_visit_occurence_raw(self):
        return self.excuteSQL("SELECT * from ohdsi.visit_occurrence")

    def get_random_visits(self, number = 1):
        data = self.excuteSQL("SELECT * from ohdsi.visit_occurrence WHERE random () < 0.01 LIMIT " + str(number))
        return self.get_visit_occurence_with_data(data)

    def get_visit_occurence_with_data(self, data):
        visits = []

        for single_visit_data in data:
            # single_visit_data[2] is concept_id for 'inpatient visit (9201), which is obvious when building an object for ICUVisit

            site = CareSite.get_site_by_name(self.care_sites, single_visit_data[9])

            visit = ICUVisit(
                visit_id=single_visit_data[0],
                person_id=single_visit_data[1],
                start_date=single_visit_data[3],
                start_time=single_visit_data[4],
                end_date=single_visit_data[5],
                end_time=single_visit_data[6],
                care_site=site
            )
            visits.append(visit)
        return visits


    def get_all_visit_occurence(self):
        data = self.get_all_visit_occurence_raw()
        return self.get_visit_occurence_with_data(data)


    def set_focus(self, target):
        self.focus.set_focus(target)

    def ask_if_patient_died_focused_period(self):
        if (self.focus.type == SINGLE_VISIT):
            visit = self.focus.target
            subject_id = visit.person_id

            data = self.excuteSQL("SELECT * from ohdsi.death WHERE person_id = " + str(subject_id))
            if (len(data) == 0):
                if (self.talking == True):
                    print ('\nEcho: "We have no record that the patient died in the hospital."\n')
            else:
                death_date = data[0][1]
                death_datetime = datetime(year=death_date.year, day=death_date.day, month=death_date.month )
                start_datetime = self.focus.start_datetime
                end_datetime = self.focus.end_datetime

                if (start_datetime <= death_datetime and death_datetime <= end_datetime):
                    if (self.talking == True):
                        print (
                    '\nEcho: "We have a record that the patient died in the hospital during the period as the patient died on ' + str(
                        death_date) + ', which is between ' + str(start_datetime) + ' and ' + str(
                        end_datetime) + '.\n')
                    return (True, dict(death_date=death_date))
                else:
                    if (self.talking == True):
                        print ('\nEcho: "We have a record that the patient died in the hospital, but it was not during the period specified. The patient died on ' + str(
                            death_date) + ', which IS NOT between ' + str(start_datetime) + ' and ' + str(
                        end_datetime) + '.\n')
                    return (False, dict(death_date=death_date))


    def ask_if_patient_died_during_the_visit(self):
        if (self.focus == None or self.focus.target == None):
            if (self.talking == True):
                print ('\nEcho: "You said you want to know whether a patient died? but.... which patient(s)?"')
            return None

        if (self.focus.type == SINGLE_VISIT):
            visit = self.focus.target
            subject_id = visit.person_id

            data = self.excuteSQL("SELECT * from ohdsi.death WHERE person_id = " + str(subject_id))
            if ( len(data) == 0 ):
                if (self.talking == True):
                    print ('\nEcho: "We have no record that the patient died in the hospital."\n')
                return (False, dict())

            else:
                death_date = data[0][1]
                visit_start_date = visit.start_date
                visit_end_date = visit.end_date

                if ( visit_start_date <= death_date and death_date <= visit_end_date  ):
                    if (self.talking == True):
                        print ('\nEcho: "We have a record that the patient died in the hospital during the visit. The patient died on ' + str(death_date) + ', which is between ' + str(visit_start_date) + ' and ' + str(visit_end_date) + ' (the duration of the target ICU visit.)\n')
                    return (True, dict(death_date=death_date))
                else:
                    if (self.talking == True):
                        print (
                    '\nEcho: "We have a record that the patient died in the hospital, but it was not during the visit. The patient died on ' + str(
                        death_date) + ', which IS NOT between ' + str(visit_start_date) + ' and ' + str(
                        visit_end_date) + ' (the duration of the target ICU visit.)\n')
                    return (False, dict(death_date=death_date))


        return None


class Focus:

    visit = None
    type = None
    time_point = None
    duration = None
    start_datetime = None
    end_datetime = None
    target = None
    talking = True

    def __init__(self):
        return

    def set_focus(self, target):
        self.visit = None
        self.type = None
        self.time_point = None
        self.start_datetime = None
        self.end_datetime = None

        self.target = target

        if ( isinstance(target, ICUVisit) ):
            self.type = SINGLE_VISIT
            if (self.talking == True):
                print('\nEcho: "Okay, I will focus on the visit of the patient_id: ' + str(target.person_id) + ', who visited ICU on ' + str(target.start_date) + '."\n')


    def set_time_point(self, timepoint, duration = timedelta(hours=3) ):

        self.duration = duration
        if ( isinstance(timepoint, datetime) ):
            self.time_point = timepoint
        else :
            raise ValueError('Error: The time point for focus should be the type of datetime.datetime.')

        self.start_datetime = self.time_point - duration
        self.end_datetime = self.time_point + duration

        if (self.talking == True):
            print('Echo: "I understand that you are intrested in what happend at ' + str(self.time_point) + " during the hospitalization. (plus/minus " + str(self.duration) + " hours) Therefore, it will be between " + str(self.start_datetime) + " and " + str(self.end_datetime) + ". ")


    def set_date_point(self, datepoint, duration = timedelta(hours=24)):
        self.start_datetime = datetime(year=datepoint.year, month=datepoint.month, day=datepoint.day, hour=0, minute=0, second=0)
        self.duration = duration
        self.end_datetime = self.start_datetime + duration

        if (self.talking == True):
            print('Echo: "I understand that you are intrested in what happend at ' + str(self.start_datetime) + " during the hospitalization. (will assume " + str(self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(self.end_datetime) + ".")

    def set_start_end_datetime(self, start_datetime, end_datetime):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.duration = end_datetime - start_datetime
        if (self.talking == True):
            print('Echo: "I understand that you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")

        return

    def set_start_end_date(self, start_date, end_date):
        self.start_datetime = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=0, minute=0,
                                   second=0)
        self.end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=0, minute=0,
                                   second=0)

        self.duration = self.end_datetime - self.start_datetime
        return


    def time_forward(self, duration):
        self.start_datetime = self.start_datetime + duration
        self.end_datetime = self.end_datetime + duration
        if (self.time_point != None):
            self.time_point = self.time_point + duration

    def days_later(self, days):
        self.time_forward(  timedelta( days = days)  )
        if (self.talking == True):
            print('Echo: "I understand that now you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")

    def hours_later(self, hours):
        self.time_forward(timedelta(hours=hours))
        if (self.talking == True):
            print('Echo: "I understand that now you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")


'''
    # Clinical Questions
    def patient_died_during_period( person_id, start, end ):

        patient_visits = connection.get_all_visits_by_patient( person_id )

        return 1

    def patient_died_during_visit( person_id, visit):
        patient_visits = connection.get_all_visits_by_patient(person_id)

        return 1

'''


class Loader:
    visits = None
    care_sites = None

    def __init__ (self, dbname = "mimic2", user = "jpark", password = "pc386pc386"):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.initialize()

    def initialize(self):
        conn_string = "dbname='" + self.dbname + "' user = '" + self.user + "' password = '" + self.password + "'"
        self.conn = psycopg2.connect(conn_string)
        print("Connecting to database -> %s " % (conn_string))


    def get_connection(self):
        return self.conn




'''
def get_all_visits_by_patient_id(self, person_id):
        self.get_visit_occurence()
        visits_by_patient = []

        for visit in self.visits:
            if visit.person_id ==

visits = []
for record in records:
    visit = ICUVisit( record.subje )
    visits.append( )
    print(record)


class ICUVisit:
    def __init__( self, visit_id ):
        self.visit_id = visit_id

'''


