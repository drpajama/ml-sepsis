
# Abstracted Clinical Data in Class Structures

from datetime import datetime

class Person:
    person_id = None
    gender_id = None
    dob = None
    echo = None

    def __init__(self, person_id, gender_id, year_of_birth, month_of_birth, day_of_birth, echo = None):
        self.person_id = person_id
        self.gender_id = gender_id
        self.dob = datetime(year=year_of_birth, month=month_of_birth, day=day_of_birth)
        self.echo = echo

    def get_age_at(self, at):
        if (self.dob == None):
            return None

        if ( isinstance(at, datetime) == False):
            raise ValueError("The parameter for get_age_at should be the type of datetime.datetime")

        age = at - self.dob
        return age

    def is_male(self):
        if (self.gender_id == 8507):
            return True
        return False

    def is_female(self):
        if (self.gender_id == 8537):
            return True
        return False

    def __repr__(self):
        return  "Patient ID: " + str(self.person_id) + "\nGender_ID: " + str(self.gender_id) + " (You can use the methods of 'is_male()' and 'is_female()')"  + "\nDate of Birth: " + str(self.dob)

    def description(self):
        print("Patient ID: " + str(self.person_id) )
        print("Gender_ID: " + str(self.gender_id) + " (You can use the methods of 'is_male()' and 'is_female()')" )
        print("Date of Birth: " + str(self.dob) )



class ICUVisit:
    echo = None

    def __init__(self, visit_id, person_id, start_date, start_time, end_date, end_time, care_site, echo = None):

        self.visit_id = visit_id
        self.person_id = person_id

        self.start_date = start_date
        self.start_time = datetime.strptime(start_time, '%H:%M:%S')

        self.end_date = end_date
        self.end_time = datetime.strptime(end_time, '%H:%M:%S')

        self.care_site = care_site
        self.echo = echo

    def get_start_datetime(self):
        return datetime(year=self.start_date.year, month=self.start_date.month, day=self.start_date.day,
                        hour = self.start_time.hour, minute= self.start_time.minute, second = self.start_time.second)

    def get_end_datetime(self):
        return datetime(year=self.end_date.year, month=self.end_date.month, day=self.end_date.day,
                        hour=self.end_time.hour, minute=self.end_time.minute, second=self.end_time.second)

    def get_duration_date(self):
        return self.end_date - self.start_date

    def get_duration_datetime(self):
        return self.get_end_datetime() - self.get_start_datetime()

    def get_person(self):
        return self.echo.gather.get_person_by_id( self.person_id )

    def __repr__(self):
        return "\n" + "Visit ID: " + str(self.visit_id) + "\nPatient ID: " + str(self.person_id) + "\nCareSite: " + self.care_site.description() + "Duration: stayed in the ICU starting from " + str(self.get_start_datetime()) + " until " + str(self.get_end_datetime())  + " (Total: " + str(self.get_duration_datetime()) + " )"

    def description(self):
        print(self.__repr__(self))

class LabValue:
    name = None
    person_id = None
    visit_id = None
    concept_id = None
    timepoint = None
    value = None
    unit_id = None
    unit_name = None
    is_ICU = None
    operator_id = None


    def __init__(self, name , concept_id, person_id, visit_id, is_ICU, timepoint, value, operator_id, unit_id, unit_name):
        self.name = name
        self.person_id = person_id
        self.visit_id = visit_id
        self.is_ICU = is_ICU
        self.timepoint = timepoint
        self.value = value
        self.operator_id = operator_id
        self.unit_id = unit_id
        self.unit_name = unit_name
        self.concept_id = concept_id

    def __repr__(self):

        tag = " - Non-ICU"
        if self.is_ICU == True:
            tag = ""
        return self.name + "/" + str(self.concept_id) + ": " + str(self.value) + str(self.unit_name) +  " (Done at " + str(self.timepoint) + ")" + tag

class VentilatorSetting:
    person_id = None
    visit_id = None

    def __init__(self):
        return


class MechanialVentliationStatus:
    person_id = None
    visit_id = None
    setting = None
    time_point = None


    def set_setting ( self ):
        self.setting = VentilatorSetting



class IVFluidSetting:
    def __init__(self):
        return

class CareSite:
    def __init__(self, site_id, site_name, site_concept_id, site_source_value):
        self.site_id = site_id
        self.site_name = site_name
        self.site_concept_id = site_concept_id
        self.site_source_value = site_source_value


    def __repr__(self):
        return self.site_name + " (Concept ID: " + str(self.site_concept_id) + " / " + self.site_source_value + ")"

