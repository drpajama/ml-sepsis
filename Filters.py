from OHDSIConstants import CONST
from datetime import timedelta
from ClinicalData import PersonPeriod

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

class SignificantInfectionFilter(Filter):

    def __init__ (self):
        return



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

