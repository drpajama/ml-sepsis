from OHDSIConstants import CONST
from datetime import timedelta
import datetime
from ClinicalData import PersonPeriod
from UsefulFunctions import *

def compare( value1,  operator, value2 ):

   # if( isinstance( value1, timedelta) and isinstance( value1, int ) ):
    #    value1 = timedelta.

    if (operator == '='):
        return ( value1 == value2)
    if (operator == ">"):
        return ( value1 > value2)
    if (operator == "<"):
        return ( value1 < value2)
    if (operator == ">="):
        return ( value1 >= value2)
    if (operator == "<="):
        return ( value1 <= value2)

    return None

class Filter:

    def if_period_meet_filter(self, person_period, echo):
        return (False, {} )


class SepticShockFilter(Filter):
    type = 'sepsis3'
    # JAMA2016/SEPSIS3: Patient with sepsis shock can be identified with a clinical construct of sepsis with persisting hypotension requring vasopressor to maintain MAP >= 65mmHg and having a serum lactate level >2 mmol/L (18 mg/dL) despite adequate volume resuscitation. With these criteria, hospital mortality is in excess of 40%

    infection_known = True

    def __init__(self, type='sepsis3', infection_known=True):
        self.type = type
        self.infection_known = infection_known

    def if_period_meet_filter(self, person_period, echo):
        # persisting hypotension requring vasopressor to maintain MAP >= 65mmHg whould be defined as 'on vasopressor + at least 1 measurement of MAP <= 80 + serum lactate level of > 2'

        print (person_period)
        pressor_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.VASOPRESSORS)

        print("=== Pressure Exposure\n")
        if len(pressor_exposures) == 0:
            print("Not on pressor\n")
        for exposure in pressor_exposures:

            print exposure

        print("\n==== MAP Trend")
        maps = echo.gather.get_measurement_by_concept_focused(
            [CONST.MEAN_ARTERIAL_PRESSURE_INVASIVE, CONST.MEAN_ARTERIAL_PRESSURE_NONINVASIVE])

        print_list (maps)

        lowest_map = 999
        for map in maps:
            if map.value < lowest_map:
                lowest_map = map.value

        print("Lowest MAP: " + str(lowest_map))

        lactate_measurements = echo.gather.get_measurement_by_concept_focused(
            [CONST.LACTATE])


        print("\n==== Lactate")
        print_list (lactate_measurements)

        highest_lactate = 0

        for measure in lactate_measurements:
            if measure.value > highest_lactate:
                highest_lactate = measure.value



        print( "Highest Lactate: " + str(highest_lactate) )


        infection = None

        if self.infection_known == True:
            infection = True
        else:
            infection_filter = SignificantInfectionFilter()
            infection = infection_filter.if_period_meet_filter ( person_period, echo  ) [0]
            print("\n== Significant Infection: " + str(infection) + "\n")

        if highest_lactate >=2 and len(pressor_exposures) >=1 and lowest_map < 80 and infection == True:
            print echo.get_discharge_summary()
            print("\n== Result")
            return (True, {})

        else:
            print echo.get_discharge_summary()
            print("\n== Result")
            return (False, {})




class SignificantInfectionFilter(Filter):

    def __init__ (self):
        return


    def if_period_meet_filter(self, person_period, echo):

        axis_time = person_period.axis_datetime  # 6am
        cohort_start_time = person_period.start_datetime  # 2am
        cohort_end_time = person_period.end_datetime  # 10am
        hospitalization = echo.gather.get_hospitalization(person_period.person.person_id,
                                                          person_period.start_datetime)  # the record of the entire hospitalization which the current cohort belongs to.

        admission_time = hospitalization.get_start_datetime()
        discharge_time = hospitalization.get_end_datetime()

        echo.set_focus (person_period)
        echo.focus.set_start_end_datetime(admission_time, discharge_time)  # between admission - current time
        abx_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.ANTIBIOTICS)

        # Exclusion: Is is not excluded if only one dose was given. [ See the eAppendix of http://jama.jamanetwork.com/article.aspx?articleid=2492875 ]

        #abx_exposures = echo.filter.remove_if_only_one_dose ( abx_exposures )
        first_dose_exposures = echo.gather.get_only_first_doses ( abx_exposures )
        temp = []


        for exposure in first_dose_exposures:

            if exposure.how_many_from ( abx_exposures ) > 1:
                temp.append (exposure)

        first_dose_exposures = temp


        print("------ First Doses")
        #print_list ( first_dose_exposures )



        cultures = echo.gather.get_all_procedure_occurrence_focused_by_concept_id_list(
            [CONST.BLOOD_CULTURE, CONST.URINE_CULTURE, CONST.STOOL_CULTURE, CONST.CSF_CULTURE, CONST.WOUND_CULTURE], ['pan culture'])

        #print_list(abx_exposures, "List of Antibiotics")
        #print_list(cultures, "List of Cultures")

        # Option 1 for JAMA Feb 2016 [ See the eAppendix of http://jama.jamanetwork.com/article.aspx?articleid=2492875 ]

        met_option1 = False

        reason = []
        for culture in cultures:
            # In option 1, the body fluid culture was drawn first, and the antibiotic administration must occur within 72 hrs.

            culture_time = culture.procedure_time

            for abx_initiation_event in first_dose_exposures:

                abx_time = abx_initiation_event.start_time
                delta = datetime.timedelta(hours=72)

                # culture is done first, and
                if ( culture_time <= abx_time and culture_time+delta >= abx_time):
                    met_option1 = True
                    reason.append( { 'culture': culture,  'abx_time': abx_initiation_event, 'condition': 'culture -> abx within 72 hours' }    )


        met_option2 = False

        # Option 2 for JAMA Feb 2016 [ See the eAppendix of http://jama.jamanetwork.com/article.aspx?articleid=2492875 ]
        # In option 2, the antibiotic dose occurs first, and the body fluid culture must occur within 24 hrs.


        for abx_initiation_event in first_dose_exposures:
            abx_time = abx_initiation_event.start_time
            delta = datetime.timedelta(hours=24)

            for culture in cultures:
                culture_time = culture.procedure_time

                if (person_period.person.person_id == 82006):
                    print "Culture_time: " + str(culture_time)

                if( abx_time <= culture_time and abx_time+delta >= culture_time):
                    met_option2 = True
                    reason.append({'culture': culture, 'abx_time': abx_initiation_event,
                               'condition': 'abx -> culture within 24 hours'})


        # Single-dose antibiotics is excluded

        # [or Inclusion] The patient would be considered to be in significant infection if the patient is on two antibiotics on the person_period

        # [Exclusion] The patient would be excluded if the patient is not on antibiotics for 5 days

        if (met_option1 == True or met_option2 == True):
            return (True, {'reasoning': reason } )
        else:
            return (False, {'reasoning': reason} )



class NumericConceptFilter(Filter):
    concept = 0
    operator = None
    value = None

    type_for_period = 'on_start'

    def __init__ ( self, concept, operator, value, type_for_period = 'on_start' ):
        self.concept = concept
        self.operator = operator
        self.value = value
        self.type_for_period = type_for_period
       # self.type = type
        return

    def if_period_meet_filter (self, person_period, echo):

        local_echo = echo.copy()
        local_echo.set_focus(person_period)

        if (self.concept == CONST.AGE):
            time_on_visit = person_period.start_datetime
            patient = person_period.person

            age = patient.get_age_at(time_on_visit).days/365
            reasoning = "The patient was " + str(age) + " at the starting timepoint of the period you set (" + str(
                time_on_visit) + ", and the dob is " + str(patient.dob.year) +  "-" +  str(patient.dob.month)  + "-" + str(patient.dob.day) + " ). We compared the age to the value you set (" + str(self.value) + "yo" + "), using the operator of '" + self.operator + "'."

            if compare(age, self.operator, self.value) == True:
                return (True, {'age': age, 'reasoning': reasoning})
            else:
                return (False, {'age': age, 'reasoning': reasoning})
        else:
            '''echo.focus.set_start_end_datetime( start_time, end_time )
            measurements = echo.gather.get_measurement_by_concept_focused(self.concept)'''
            return None

        '''measurements_meet = []
        measurements_not_meet = []

        for measurement in measurements:

            if compare(measurement.value, self.operator, self.value) == True:
                measurements_meet.append(measurement)
            else:
                measurements_not_meet.append(measurement)

        if (len(measurements_meet) >= 1):
            return (True, {'measurements_meet_criteria': measurements_meet,
                           'measurements_not_meet_criteria': measurements_not_meet})
        else:
            return (False, {'measurements_meet_criteria': measurements_meet,
                            'measurements_meet_criteria': measurements_not_meet})
        '''

