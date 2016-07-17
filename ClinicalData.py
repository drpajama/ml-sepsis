
# Abstracted Clinical Data in Class Structures

from datetime import datetime
from datetime import timedelta
from OHDSIConstants import CONST

class VitalSigns:
    temperature = None
    mean_arterial_pressure = None
    heart_rate = None
    respiratory_rate = None
    saturation = None
    is_celcius = None

class MentalStatus:
    orientation = None
    following_command = None

class VentilationSetting:
    mechanical_ventilation = None

class VentilationMonitoring:
    fsfasfds = None

class PersonTimePoint:
    person = None
    time_point = None

    def __init__ (self, person, time_point):
        self.person = person
        self.time_point = time_point

class PersonPeriod:
    person = None
    start_datetime = None
    end_datetime = None
    duration = None
    axis_datetime = None

    def __init__(self, person, start_datetime, end_datetime, axis_datetime = None ):
        self.person = person
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.axis_datetime = axis_datetime


    def __repr__(self):
        temp = "[Patient ID: " + str(self.person.person_id) + "/" + str(self.person.get_age_at( self.start_datetime ).days/365) + " yo] " + "Between " + str(self.start_datetime) + " and " + str(self.end_datetime) + "\n"

        return temp

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

class VisitPeriod:

    def __init__ (self, visit, start_time, end_time):
        self.visit = visit
        self.start_time = start_time
        self.end_time = end_time


class Visit:
    echo = None

    def __init__(self, visit_id, person_id, start_date, start_time, end_date, end_time, care_site, echo=None):
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
                        hour=self.start_time.hour, minute=self.start_time.minute, second=self.start_time.second)

    def get_end_datetime(self):
        return datetime(year=self.end_date.year, month=self.end_date.month, day=self.end_date.day,
                        hour=self.end_time.hour, minute=self.end_time.minute, second=self.end_time.second)

    def get_duration_date(self):
        return self.end_date - self.start_date

    def get_duration(self):
        return self.get_end_datetime() - self.get_start_datetime()

    def get_person(self):
        return self.echo.gather.get_person_by_id(self.person_id)

    def get_first_6am_datetime(self):
        one_day_ago = datetime(year=self.start_date.year, month=self.start_date.month, day=(self.start_date.day),
                               hour=6, minute=0, second=0)
        timimg = one_day_ago + timedelta(days=1)

        return timimg

    def __repr__(self):
        return "\n" + "Visit ID: " + str(self.visit_id) + "\nPatient ID: " + str(
            self.person_id) + "\nCareSite: " + self.care_site.description() + "\nDuration: Hospitalized in the hospital starting from " + str(
            self.get_start_datetime()) + " until " + str(self.get_end_datetime()) + " (Total: " + str(
            self.get_duration()) + " )"

    def description(self):
        print(self.__repr__(self))


class ICUVisit(Visit):

    def __init__(self, icu_visit_id, person_id, start_date, start_time, end_date, end_time, care_site, echo=None):

        self.icu_visit_id = icu_visit_id
        self.person_id = person_id

        self.start_date = start_date

        if isinstance( start_time , str ) == True:
            self.start_time = datetime.strptime(start_time, '%H:%M:%S')

        self.end_date = end_date
        if isinstance( end_time , str ) == True:
            self.end_time = datetime.strptime(end_time, '%H:%M:%S')

        self.care_site = care_site
        self.echo = echo


    def __repr__(self):
        return "\n" + "ICU Visit ID: " + str(self.icu_visit_id) + "\nPatient ID: " + str(
            self.person_id) + "\nCareSite: " + self.care_site.description() + "\nDuration: stayed in the ICU starting from " + str(
            self.get_start_datetime()) + " until " + str(self.get_end_datetime()) + " (Total: " + str(
            self.get_duration()) + " )"


class DeviceExposure:
    name = None
    person_id = None
    device_concept_id = None
    start_time = None
    device_type_concept_id = None
    end_time = None

    def __init__ (self, person_id, device_concept_id, device_type_concept_id, start_time, end_time, name = None ):
        self.person_id = person_id
        self.device_concept_id = device_concept_id
        self.start_time = start_time
        self.end_time = end_time
        self.device_type_concept_id = device_type_concept_id
        self.name = name

    def __repr__(self):
        temp = "Device Placement: " + self.name + " was placed between " + str(self.start_time) + " and " + str(self.end_time) + " (Duration: " + str(self.end_time-self.start_time) + ")"
        return temp


class ProcedureOccurrence:
    name = None
    person_id = None
    procedure_concept_id = None
    procedure_time = None
    procedure_type_id = None
    start_time = None

    def __init__ (self, person_id, procedure_concept_id, procedure_type_id, procedure_time, name = None ):
        self.person_id = person_id
        self.procedure_concept_id = procedure_concept_id
        self.procedure_time = procedure_time
        self.procedure_type_id = procedure_type_id
        self.name = name

    def __repr__(self):
        temp = "Procedure: " + self.name + " was done at " + str(self.procedure_time) + ". (Concept ID: " + str(self.procedure_concept_id) + ") "
        if self.procedure_concept_id == CONST.PERIPHERAL_LINE:
            temp = temp + "- Peripheral Line"
        elif self.procedure_concept_id in (CONST.CENTRAL_FEMORAL, CONST.CENTRAL_IJ, CONST.CENTRAL_SUBCLAVIAN, CONST.CENTRAL_OTHER):
            temp = temp + "- Central Venous Line"

        return temp

class DrugExposure:
    person_id = None
    drug_concept_id = None
    drug_type_id = None
    start_time = None
    end_time = None
    dose = None
    dose_unit_id = None
    route = None
    hadm_id = None
    name = None

    def __init__ (self, person_id, drug_concept_id, drug_type_id, start_time, end_time, dose = 1, dose_unit_id = 8513, route = CONST.ADMINISTRATION_INTRAVENOUS, name = None):
        self.person_id = person_id
        self.drug_concept_id = drug_concept_id
        self.drug_type_id = drug_type_id
        self.start_time = start_time
        self.end_time = end_time
        self.dose = dose
        self.dose_unit_id = dose_unit_id
        self.name = name
        self.route = route

    @property
    def timepoint(self):
        return self.start_time

    def __repr__(self):
        temp = ""

        if self.route == CONST.CONTINUOUS_INFUSION and self.drug_type_id == CONST.VASOPRESSORS:
            temp = temp + "[IV Drip/Vasopressor] "
        elif self.route == CONST.CONTINUOUS_INFUSION:
            temp = temp + "[Drip] "
        elif self.route == CONST.ADMINISTRATION_INTRAVENOUS:
            temp = temp + "[IV Bolus] "

        if self.route == CONST.CONTINUOUS_INFUSION:
            temp = temp + self.name + " - " + str(self.dose)
            if( self.dose_unit_id == 9692 ):
                temp = temp + ' mcg/kg/min. '
            elif (self.dose_unit_id == 8630 ):
                temp = temp + ' unit/hour. '
            else:
                temp = temp + '(unit unspecified) '
            temp = temp + "Given at " + str(self.start_time) + " - " + str(self.end_time) + " (Duration: "  + str(self.end_time-self.start_time) + ")"
        else:
            temp = temp + self.name + " was administered at " + str(self.start_time) + " (finished at " + str(self.end_time) + "). Drug concept ID: " + str(self.drug_concept_id) + ". "

        if self.drug_type_id == CONST.ANTIBIOTICS:
            temp = temp + "The medication is in the category of antibiotics (" + str(CONST.ANTIBIOTICS) + ") "





        return temp





class LabValue:
    name = None
    person_id = None
    hadm_id = None
    concept_id = None
    timepoint = None
    value = None
    unit_id = None
    unit_name = None
    is_ICU = None
    operator_id = None

    value_str = None
    value_id = None


    def __init__(self, name , concept_id, person_id, hadm_id, is_ICU, timepoint, value, operator_id, unit_id, unit_name,
                 value_id = None, value_str = None):
        self.name = name
        self.person_id = person_id
        self.hadm_id = hadm_id
        self.is_ICU = is_ICU
        self.timepoint = timepoint
        self.value = value
        self.operator_id = operator_id
        self.unit_id = unit_id
        self.unit_name = unit_name
        self.concept_id = concept_id
        self.value_str = value_str
        self.value_id = value_id

    def __repr__(self):

        tag = " - Non-ICU"
        if self.is_ICU == True:
            tag = ""

        if self.value == None:
            return self.name + "/" + str(self.concept_id) + ": " + self.value_str + "(" + str(self.value_id)+ ")"  + " (Done at " + str(self.timepoint) + ")" + tag
        else:
            return self.name + "/" + str(self.concept_id) + ": " + str(self.value) + " "+ str(
                self.unit_name) + " (Done at " + str(self.timepoint) + ")" + tag


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

