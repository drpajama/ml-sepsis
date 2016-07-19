
import psycopg2
import psycopg2.extras
from ClinicalData import *
from OHDSIConstants import CONST
import CareSite
from datetime import timedelta
from datetime import datetime
from datetime import date

SINGLE_VISIT, VISIT, SINGLE_PATIENT, PATIENTS, VISITS, PERSON_PERIOD = range(6)

class Echo:

    talking = True

    focus = None
    visits_interested = None
    patients_interested = None
    cursors_interested = None
    db_connect = None

    cohorts = []

    ask = None
    gather = None
    filter = None

    def __init__ (self, db_connect):
        self.db_connect = db_connect
        self.focus = Focus(self)
        self.ask = AskEcho(self)
        self.gather = GatherEcho(self)
        self.filter = Filter()

    def copy(self):
        echo = Echo(self.db_connect)
        echo.shutup()
        return echo

    def hello_echo(self):

        if ( self.talking == False ):
            print("\n-------")
            print('You: "Hello Echo!"')
            print("Echo: ...... \n")
        else:
            print("\n-------")
            print('"You: Hello Echo!"')
            print('"Echo: Hello Echo!"\n')

    def say(self, what_to_say):

        if (self.talking == True):
            print(what_to_say)

    def shutup(self):
        #print('Echo: Okay. No more talking.')
        self.talking = False

        if (self.focus != None):
            self.focus.talking = False
    def commit_close_db(self):
        self.db_connect.commit()
        self.db_connect.close()

    def excuteSQL_dict(self, query):
        cur = self.db_connect.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute (query)
        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError:
            return


    def excuteSQL(self, query):

        cur = self.db_connect.cursor()
        cur.execute (query)
        try:
            return cur.fetchall()
        except psycopg2.ProgrammingError:
            return


    def set_focus(self, target):
        self.focus.set_focus(target)

    def get_note_by_name (self, name):
        data = self.excuteSQL("SELECT * FROM mimiciii.noteevents as n WHERE n.subject_id = " + str(
            self.focus.patient.person_id) + "  and n.category = '" + name + "'")
        print (data)

        temp = ""

        for single in data:

            date = single[3]
            print(date)
            if self.focus.if_fall_into_date(date):
                temp = str(single[3])
                temp = temp + "\n"
                temp = temp + single[6]
                temp = temp + "\n"
                temp = temp + single[7]
                temp = temp + "\n"
                temp = temp + single[10]
                return temp

        return ""

    def get_resident_progress_note(self):
        data = self.excuteSQL("SELECT * FROM mimiciii.noteevents as n WHERE n.subject_id = " + str(self.focus.patient.person_id) + "  and n.category = 'Physician Resident Progress Note'")

        temp = ""

        for single in data:

            date = single[3]
            print(date)
            if self.focus.if_fall_into_date( date ):
                temp = str(single[3])
                temp = temp + "\n"
                temp = temp + single[6]
                temp = temp + "\n"
                temp = temp + single[7]
                temp = temp + "\n"
                temp = temp + single[10]
                return temp

        return ""


    def get_discharge_summary(self):
        data = self.excuteSQL("SELECT * FROM mimiciii.noteevents as n WHERE n.subject_id = " + str(self.focus.patient.person_id) + "  and n.category = 'Discharge summary'")
        single = data[0]
        temp = str(single[3])
        temp = temp + "\n"
        temp = temp + single[6]
        temp = temp + "\n"
        temp = temp + single[7]
        temp = temp + "\n"
        temp = temp + single[10]
        return temp

    def add_current_focus_into_cohort(self):
        self.cohorts.append(self.focus)
        return


class Focus:
    patient = None
    visit = None

    type = None
    time_point = None
    duration = None
    start_datetime = None
    end_datetime = None
    axis_datetime = None
    target = None
    talking = True
    echo = None

    def __init__(self, echo):
        self.echo = echo
        return

    def set_focus(self, target):
        self.visit = None
        self.type = None
        self.time_point = None
        self.start_datetime = None
        self.end_datetime = None

        self.target = target

        if ( isinstance(target, PersonPeriod) ):
            self.type = PERSON_PERIOD
            self.start_datetime = target.start_datetime
            self.end_datetime = target.end_datetime
            self.axis_datetime = target.axis_datetime
            self.patient = target.person


        if ( isinstance(target, ICUVisit) ):
            self.type = SINGLE_VISIT
            self.echo.say('\nEcho: "Okay, I will focus on the visit of the patient_id: ' + str(target.person_id) + ', who visited ICU on ' + str(target.start_date) + '."\n')
            self.visit = target
            self.patient = target.get_person()

        if( isinstance(target, Person)):
            self.type = SINGLE_PATIENT
            self.patient = target



    def set_time_point(self, timepoint, duration = timedelta(hours=4) ):

        self.duration = duration
        if ( isinstance(timepoint, datetime) ):
            self.time_point = timepoint
        else :
            raise ValueError('Error: The time point for focus should be the type of datetime.datetime.')

        self.start_datetime = self.time_point - duration
        self.end_datetime = self.time_point + duration

        self.echo.say('Echo: "I understand that you are intrested in what happend at ' + str(self.time_point) + " during the hospitalization. (plus/minus " + str(self.duration) + " hours) Therefore, it will be between " + str(self.start_datetime) + " and " + str(self.end_datetime) + ". ")


    def set_date_point(self, datepoint, duration = timedelta(hours=24)):
        self.start_datetime = datetime(year=datepoint.year, month=datepoint.month, day=datepoint.day, hour=0, minute=0, second=0)
        self.duration = duration
        self.end_datetime = self.start_datetime + duration

        self.echo.say('Echo: "I understand that you are intrested in what happend at ' + str(self.start_datetime) + " during the hospitalization. (will assume " + str(self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(self.end_datetime) + ".")

    def set_start_datetime(self, start_datetime):
        # when you want to reset start_time

        self.start_datetime = start_datetime
        if (self.end_datetime != None):
            self.duration = self.end_datetime - start_datetime

        self.echo.say('Echo: "I understand that you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")

        return

    def set_end_datetime(self, end_datetime):
        # when you want to reset end_time

        self.end_datetime = end_datetime
        if (self.start_datetime != None):
            self.duration = end_datetime - self.start_datetime

        self.echo.say('Echo: "I understand that you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")

        return

    def set_start_end_datetime(self, start_datetime, end_datetime):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.duration = self.end_datetime - self.start_datetime


        self.echo.say('Echo: "I understand that you are intrested in what happend at ' + str(
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

    def start_hours_earlier(self, hours):
        hours_datetime = timedelta(hours = hours)
        self.set_start_datetime( self.start_datetime-hours_datetime )

    def days_later(self, days):
        self.time_forward(  timedelta( days = days)  )

        self.echo.say('Echo: "I understand that now you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")

    def hours_later(self, hours):
        self.time_forward(timedelta(hours=hours))

        self.echo.say('Echo: "I understand that now you are intrested in what happend at ' + str(
            self.start_datetime) + " during the hospitalization. (will be " + str(
            self.duration) + " period) Therefore, it will be between " + str(self.start_datetime) + " and " + str(
            self.end_datetime) + ".")

    def if_fall_into_date(self, date):

        if ( date.year == self.start_datetime.year and date.month == self.start_datetime.month and date.day == self.start_datetime.day) :
            return True
        return False


    def if_fall_into(self, datetime_point ):

        if ( self.start_datetime == None or self.end_datetime == None):
            return None

        if ( datetime_point >= self.start_datetime and datetime_point <= self.end_datetime ):
           # print("true")
            return True
        else:
           # print('false')
            return False


'''
    # Clinical Questions
    def patient_died_during_period( person_id, start, end ):

        patient_visits = connection.get_all_visits_by_patient( person_id )

        return 1

    def patient_died_during_visit( person_id, visit):
        patient_visits = connection.get_all_visits_by_patient(person_id)

        return 1

'''

'''
class NoiseReducer:

class TrendSetter:


'''

class GatherEcho:
    echo = None
    care_sites = None

    def __init__(self, echo):
        self.echo = echo
        self.care_sites = self.get_caresites()

    def get_all_device_exposure_raw(self):
        data = self.echo.excuteSQL(
            "SELECT * from ohdsi.device_exposure WHERE person_id=" + str(self.echo.focus.patient.person_id))
        return data

    def get_hospitalization(self, person_id, timepoint):

        hospitalizations = self.get_all_hospitalization_by_person_id(person_id)

        for hospitalization in hospitalizations:
            start_time_hospitalization = hospitalization.get_start_datetime()
            end_time_hospitalization = hospitalization.get_end_datetime()

            if (timepoint >= start_time_hospitalization and timepoint < end_time_hospitalization):
                return hospitalization

        return None

    def get_all_device_exposure_unfocused(self):
        data = self.get_all_device_exposure_raw()

        devices_processed = []

        for single_data in data:
            start_date = single_data[2]
            start_time = datetime.strptime(single_data[12], '%H:%M:%S')
            end_date = single_data[3]
            end_time = datetime.strptime(single_data[13], '%H:%M:%S')

            start_datetime = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=start_time.hour,
                                          minute=start_time.minute, second=start_time.second)
            end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour,
                                      minute=end_time.minute, second=end_time.second)

            device = DeviceExposure(
                person_id=single_data[0],
                device_concept_id=single_data[1],
                device_type_concept_id=single_data[4],
                start_time = start_datetime,
                end_time=end_datetime,
                name=single_data[9]
            )

            devices_processed.append(device)
        return devices_processed

    def get_all_procedure_occurrence_focused_by_concept_id_list(self, concept_id_list, name_list=[]):


        if self.echo.focus == None:
            return

        procedures = self.get_all_procedure_occurrence_unfocused_by_concept_id_list(concept_id_list, name_list )
        procedures_met = []

        for procedure in procedures:
            if (self.echo.focus.if_fall_into(procedure.procedure_time) == True):
                procedures_met.append(procedure)

        return procedures_met


    def get_all_procedure_occurrence_unfocused_by_concept_id_list (self, concept_id_list, name_list = [] ):
        data = []

        for single in concept_id_list:
            data = data + self.get_all_procedure_occurrence_by_concept_id_raw(single)

        for single in name_list:
            data = data + self.get_all_procedure_occurrence_by_name_raw( single )

        procedures_processed = []

        for single_data in data:
            date = single_data['procedure_date']
            time = datetime.strptime(single_data['procedure_time'], '%H:%M:%S')

            procedure_datetime = datetime(year=date.year, month=date.month, day=date.day, hour=time.hour,
                                          minute=time.minute, second=time.second)

            procedure = ProcedureOccurrence(
                person_id=single_data['person_id'],
                procedure_concept_id=single_data['procedure_concept_id'],
                procedure_type_id=single_data['procedure_type_concept_id'],
                procedure_time=procedure_datetime,
                name=single_data['procedure_source_value']
            )

            procedures_processed.append(procedure)

        return procedures_processed

    def get_all_procedure_occurrence_unfocused_by_concept_id(self, concept_id = None):
        data = []

        if concept_id == None:
            data = self.get_all_procedure_occurrence_raw()
        else:
            data = self.get_all_procedure_occurrence_by_concept_id_raw( concept_id )

        procedures_processed = []

        for single_data in data:
            date = single_data[3]
            time = datetime.strptime(single_data[12], '%H:%M:%S')

            procedure_datetime = datetime(year=date.year, month=date.month, day=date.day, hour=time.hour,
                                          minute=time.minute, second=time.second)

            procedure = ProcedureOccurrence(
                person_id=single_data[1],
                procedure_concept_id=single_data[2],
                procedure_type_id=single_data[4],
                procedure_time=procedure_datetime,
                name=single_data[9]
            )

            procedures_processed.append(procedure)
        return procedures_processed


    def get_all_procedure_occurrence_unfocused (self):
        return self.get_all_procedure_occurrence_unfocused_by_concept_id(None)

    def get_only_first_doses(self, exposures):

        first_doses = []

        for exposure in exposures:

            #print("for : " + str(exposure))
            if_first_dose =  exposure.if_the_first_dose( exposures )
            #print if_first_dose

            if if_first_dose[0] == True:
                first_doses.append( exposure )

        return first_doses



    def get_all_drug_exposure_by_type_unfocused(self, type):

        data = self.get_all_drug_exposure_by_type_raw( type )
        exposures_processed = []

        for single_data in data:

            date = single_data[2]
            time = single_data[20] #datetime.strptime(single_data[20], '%H:%M:%S')

            end_date = single_data[3]
            end_time = single_data[21] #datetime.strptime(single_data[21], '%H:%M:%S')

            start_datetime = datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second)
            end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour, minute=end_time.minute, second=end_time.second)

            exposure = DrugExposure(
                    person_id = single_data[0],
                    drug_concept_id = single_data[1],
                    drug_type_id = single_data[4],
                    start_time = start_datetime,
                    end_time = end_datetime,
                    dose = single_data[11],
                    dose_unit_id = single_data[12],
                    route = single_data[10],
                    name = single_data[16]
            )

            exposures_processed.append( exposure )

        return exposures_processed


    def get_all_drug_exposure_by_type_focused (self, type):
        if self.echo.focus == None:
            return

        exposures = self.get_all_drug_exposure_by_type_unfocused(type)
        exposures_met = []

        for exposure in exposures:
            if (self.echo.focus.if_fall_into(exposure.timepoint) == True):
                exposures_met.append(exposure)

        return exposures_met

    def get_all_procedure_occurrence_by_name_raw(self, name):

        name = "'" + name + "'"
        data = self.echo.excuteSQL_dict("SELECT * from ohdsi.procedure_occurrence WHERE person_id=" + str(
            self.echo.focus.patient.person_id) + " and lower(procedure_source_value) = " + name )
        return data

    def get_all_procedure_occurrence_by_concept_id_raw (self, concept_id):

        temp = str(concept_id)

        data = self.echo.excuteSQL_dict("SELECT * from ohdsi.procedure_occurrence WHERE person_id=" + str(self.echo.focus.patient.person_id) + " and procedure_concept_id = " + temp )
        return data

    def get_all_procedure_occurrence_raw (self):
        data = self.echo.excuteSQL_dict("SELECT * from ohdsi.procedure_occurrence WHERE person_id=" + str(self.echo.focus.patient.person_id)  )
        return data

    def get_all_drug_exposure_by_type_raw(self, type):
        data = self.echo.excuteSQL("SELECT * from ohdsi.drug_exposure WHERE person_id=" + str(self.echo.focus.patient.person_id) + " and drug_type_concept_id = " + str(type) )
        return data

    def get_all_drug_exposure_raw(self):
        data = self.echo.excuteSQL("SELECT * from ohdsi.drug_exposure WHERE person_id=" + str(self.echo.focus.patient.person_id) )
        return data

    def get_all_measurements_raw(self):
        data = self.echo.excuteSQL("SELECT * from ohdsi.measurement WHERE person_id=" + str(self.echo.focus.patient.person_id) )
        return data

    def get_measurement_by_concept_raw(self, concept_id_array):

        concept_id_list = concept_id_array

        if isinstance(concept_id_list, list) == False:
            concept_id_list = [concept_id_list]

        data = []

        for concept_id in concept_id_list:
            data = data + self.echo.excuteSQL("SELECT * from ohdsi.measurement WHERE measurement_concept_id=" + str(concept_id) + ' and person_id=' + str(self.echo.focus.patient.person_id) )
        return data

    def get_all_measurements_focused (self):
        if self.echo.focus == None:
            return None

        measurements = self.get_all_measurements_unfocused()
        measurements_met = []

        for measurement in measurements:

            if (self.echo.focus.if_fall_into(measurement.timepoint) == True):

                measurements_met.append(measurement)

        return measurements_met

    def get_measurement_by_concept_focused(self, concept_id_array):
        if self.echo.focus == None:
            return

        labs = self.get_measurement_by_concept_unfocused(concept_id_array)
        labs_met = []

        for lab in labs:
            if( self.echo.focus.if_fall_into( lab.timepoint ) == True):
                labs_met.append( lab )

        return labs_met

    def get_all_measurements_unfocused(self):

        data = self.get_all_measurements_raw()
        measures_processed = []

        for single_data in data:

            is_ICU = False
            date = single_data[2]
            time = datetime.strptime(single_data[3], '%H:%M:%S')

            timepoint = datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second)

            if single_data[4] == 45877824:
                is_ICU = True


            lab = LabValue(
                name = single_data[13],
                concept_id = single_data[1],
                person_id = single_data[0],
                hadm_id = single_data[12],
                is_ICU = is_ICU,
                timepoint = timepoint,
                value = single_data[6],
                operator_id = single_data[5],
                unit_id = single_data[8],
                unit_name = single_data[15],
                value_id=single_data[7],
                value_str = single_data[16]
                )

            measures_processed.append( lab )


        return measures_processed

    def get_measurement_by_concept_unfocused(self, concept_id_array):


        data = self.get_measurement_by_concept_raw(concept_id_array)
        labs = []


       # self.echo.say('Echo: "Okay. Let me give you the list of labs. It looks like we have ' + str(len(data)) + " labs.\n\n------------------------------- Labs -----------------------------")

        for single_data in data:

            is_ICU = False
            date = single_data[2]
            time = datetime.strptime(single_data[3], '%H:%M:%S')

            timepoint = datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second)

            if single_data[4] == 45877824:
                is_ICU = True


            lab = LabValue(
                name = single_data[13],
                concept_id = single_data[1],
                person_id = single_data[0],
                hadm_id = single_data[12],
                is_ICU = is_ICU,
                timepoint = timepoint,
                value = single_data[6],
                operator_id = single_data[5],
                unit_id = single_data[8],
                unit_name = single_data[15]
                )

            labs.append( lab )


        return labs

    def get_random_icu_visits (self, number = 1 ):
        data = self.echo.excuteSQL("SELECT * from ohdsi.visit_occurrence as visit WHERE random() < 0.01 and visit.visit_concept_id = " + str(CONST.ICU_ADMISSION) + " LIMIT "+ str(number))
        return self.get_icu_visits_with_data(data)
        print data

    '''def get_random_visits(self, number = 1):
        data = self.echo.excuteSQL("SELECT * from ohdsi.visit_occurrence WHERE random () < 0.01 LIMIT " + str(number))
        return self.get_visit_occurence_with_data(data)
    '''

    def get_visit_by_id(self, id):
        data = self.echo.excuteSQL("SELECT * from ohdsi.visit_occurrence WHERE visit_occurrence_id=" + str(id))
        if len(data) == 0:
            return None

        return (self.get_visit_occurence_with_data(data))[0]

    def get_person_by_id(self, id):
        data = self.echo.excuteSQL("SELECT * from ohdsi.person WHERE person_id=" + str(id) )
        if len(data) == 0:
            return None

        return (self.get_person_with_data(data))[0]


    def get_random_people_raw(self, number = 1):
        data = self.echo.excuteSQL("SELECT * from ohdsi.person WHERE random () < 0.01 LIMIT " + str(number))
        return data

    def get_all_hospitalization_by_person_id(self, person_id):
        dict_list = self.get_all_hospitalization_by_person_id_raw(person_id)
        hospitalization_list = []

        for dict in dict_list:


            hospitalization = Hospitalization(
                visit_id = dict['visit_occurrence_id'],
                person_id = dict['person_id'],
                start_date= dict['visit_start_date'],
                start_time= dict['visit_start_time'],
                end_date = dict['visit_end_date'],
                end_time = dict['visit_end_time'],
                visit_type = dict['visit_type_concept_id']
            )
            hospitalization_list.append(hospitalization)

        return hospitalization_list


    def get_all_hospitalization_by_person_id_raw(self, person_id):
        data = self.echo.excuteSQL_dict("SELECT * FROM ohdsi.visit_occurrence WHERE visit_occurrence.visit_concept_id = " + str(CONST.HOSPITAL_ADMISSION) + " and visit_occurrence.person_id = " + str(person_id) )
        return data

    def get_all_ICU_visit_id(self):
        data = self.echo.excuteSQL("SELECT visit_occurrence_id from ohdsi.visit_occurrence")

        id_list = []

        for single_data in data:
            print(single_data)
            single_data[None]
            id_list.append( single_data[0] )

        return id_list


    def get_caresites_raw(self):
        return self.echo.excuteSQL("SELECT * from ohdsi.care_site")


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

    def get_icu_visit_by_index(self, index):
        raw = self.get_icu_visit_by_index_raw(index)
        visits = self.get_icu_visits_with_data(raw)
        return visits[0]

    def get_icu_visit_by_index_raw(self, index):
        return self.echo.excuteSQL("SELECT * FROM (SELECT temp.*, row_number() OVER(ORDER BY temp.person_id) as index  FROM (SELECT * FROM ohdsi.visit_occurrence) as temp WHERE temp.visit_concept_id = " + str(CONST.ICU_ADMISSION) + ") as temp2 WHERE temp2.index = " + str(index+1) )


    def get_all_visit_occurence_raw(self):
        return self.echo.excuteSQL("SELECT * from ohdsi.visit_occurrence")

    def get_person_with_data(self, data):
        persons = []

        for single_patient_data in data:

            person = Person(person_id=single_patient_data[0],
                            gender_id=single_patient_data[1],
                            year_of_birth=single_patient_data[2],
                            month_of_birth=single_patient_data[3],
                            day_of_birth=single_patient_data[4],
                            echo=self.echo  )
            persons.append(person)

        return persons

    def get_icu_visits_with_data(self, data):
        visits = []

        for single_visit_data in data:
            # single_visit_data[2] is concept_id for 'inpatient visit (9201), which is obvious when building an object for ICUVisit

            site = CareSite.get_site_by_name(self.care_sites, single_visit_data[9])

            visit = ICUVisit(
                icu_visit_id = single_visit_data[0],
                person_id = single_visit_data[1],
                start_date = single_visit_data[3],
                start_time = single_visit_data[4],
                end_date = single_visit_data[5],
                end_time = single_visit_data[6],
                care_site = site,
                echo = self.echo
            )
            visits.append(visit)

        return visits


    def get_all_visit_occurence(self):
        data = self.get_all_visit_occurence_raw()
        return self.get_visit_occurence_with_data(data)


class AskEcho:
    echo = None

    def __init__(self, echo):
        self.echo = echo

    def summarize_day(self, datepoint) :

        self.echo.focus.start_datetime = datetime(year=datepoint.year, month=datepoint.month, day=datepoint.day, hour=0,
                                           minute=0, second=0)
        self.echo.focus.duration = timedelta(hours=24)
        self.echo.focus.end_datetime = self.echo.focus.start_datetime + self.echo.focus.duration

        measurements = self.get_measurement_by_concept_focused()

        return measurements

    def how_many_total_icu_visits(self):

        data = self.echo.excuteSQL("SELECT COUNT(*) from ohdsi.visit_occurrence where visit_concept_id = " + str(CONST.ICU_ADMISSION) )
        return data[0][0]

    def if_died_during_the_visit(self):
        if (self.echo.focus == None or self.echo.focus.target == None):

            self.echo.say ('\nEcho: "You said you want to know whether a patient died? but.... which patient(s)?"')
            return None

        if (self.echo.focus.type == SINGLE_VISIT):
            visit = self.echo.focus.target
            subject_id = visit.person_id

            data = self.echo.excuteSQL("SELECT * from ohdsi.death WHERE person_id = " + str(subject_id))
            if (len(data) == 0):

                self.echo.say ('\nEcho: "We have no record that the patient died in the hospital."\n')
                return (False, dict())

            else:
                death_date = data[0][1]
                visit_start_date = visit.start_date
                visit_end_date = visit.end_date

                if (visit_start_date <= death_date and death_date <= visit_end_date):

                    self.echo.say (
                        '\nEcho: "We have a record that the patient died in the hospital during the visit. The patient died on ' + str(
                            death_date) + ', which is between ' + str(visit_start_date) + ' and ' + str(
                            visit_end_date) + ' (the duration of the target ICU visit.)\n')
                    return (True, dict(death_date=death_date))
                else:
                    self.echo.say (
                            '\nEcho: "We have a record that the patient died in the hospital, but it was not during the visit. The patient died on ' + str(
                                death_date) + ', which IS NOT between ' + str(visit_start_date) + ' and ' + str(
                                visit_end_date) + ' (the duration of the target ICU visit.)\n')
                    return (False, dict(death_date=death_date))

        return None


    def if_died_focused_period(self):

        if (self.echo.focus.start_datetime == None):
            self.echo.say('\nEcho: "I am not sure what you are talking about...... I think you forgot specifiying the time period."\n')
            return None

        if (self.echo.focus.type == SINGLE_VISIT):
            visit = self.echo.focus.target
            subject_id = visit.person_id

            data = self.echo.excuteSQL("SELECT * from ohdsi.death WHERE person_id = " + str(subject_id))
            if (len(data) == 0):
                self.echo.say ('\nEcho: "We have no record that the patient died in the hospital."\n')
            else:
                death_date = data[0][1]
                death_datetime = datetime(year=death_date.year, day=death_date.day, month=death_date.month)
                start_datetime = self.echo.focus.start_datetime
                end_datetime = self.echo.focus.end_datetime

                if (start_datetime <= death_datetime and death_datetime <= end_datetime):
                    self.echo.say (
                            '\nEcho: "We have a record that the patient died in the hospital during the period as the patient died on ' + str(
                                death_date) + ', which is between ' + str(start_datetime) + ' and ' + str(
                                end_datetime) + '.\n')
                    return (True, dict(death_date=death_date))
                else:
                    self.echo.say (
                        '\nEcho: "We have a record that the patient died in the hospital, but it was not during the period specified. The patient died on ' + str(
                            death_date) + ', which IS NOT between ' + str(start_datetime) + ' and ' + str(
                            end_datetime) + '.\n')
                    return (False, dict(death_date=death_date))


class Filter:

    def remove_if_only_one_dose( exposures ):

        return_exposures = []


        return


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


