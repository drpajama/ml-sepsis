from OHDSIConstants import CONST


def compare( value1,  operator, value2 ):

    if (operator == '='):
        return ( value1 ==value2)
    if (operator == ">"):
        return ( value1 >value2)
    if (operator == "<"):
        return ( value1 <value2)
    if (operator == ">="):
        return ( value1 >=value2)
    if (operator == "<="):
        return ( value1 <=value2)

    return None

class COHORTTYPE:
    PATIENT_COHORT = 1 # returns list of patient_id who pass the filter
    ICU_VISIT_COHORT = 2 # returns list of visit_occurrence_id which pass the filter
    ICU_ADMISSION_COHORT = 3 # returns list of visit_occurrence_id which pass the filter + admission time
    ICU_DAY_COHORT = 4 # returns list of visit_occurrence_id + day
    MOMENT_MORNING_LAB = 5 # returns list of visit_occurrences + start_time, end_time
    MOMENT_CBC_CHEM7 = 6

class SignificantInfectionFilter:

    def __init__(self):
        return

    def if_event_mett_filter(self, visit, time_point, hours_within, echo):
        return (True, {})

class SepticShockFilter:

    # Criteria for Septic Shock (Sepsis-3) --> Vasopressor (for MAP>=65) + Lactate > 2mmol [despite volume resuscitation]


    is_sepsis3 = None
    infection_already_assumed = None

    def __init__ ( self, is_sepsis3 = True , infection_already_assumed = True ):
        self.is_sepsis3 = is_sepsis3

    def search_all_moments_in_visit(self, visit, echo):
        # returns
        return

    def if_visit_meet_filter (self, visit, echo):
        # Returns (True, {}) is the visit was complicated with septic shock (sepsis3 or other)
        return

    def if_moment_meet_filter (self, visit, time_point, hours_within, echo):
        # it tells you whether certain moment given was followed by the development of septic shock.
        return


class NumericConceptFilter:
    concept = 0
    operator = None
    value = None
    type = 'at_least'

    def __init__ ( self, concept, operator, value ):
        self.concept = concept
        self.operator = operator
        self.value = value
        return

    def if_event_meet_filter (self, type, visit, start_time, end_time, echo):
        echo.set_focus(visit)

        if (self.concept == CONST.AGE):
            time_on_visit = visit.get_start_datetime
            patient = visit.get_person()
            age = patient.how_old_at(time_on_visit)

            if compare(age, self.operator, self.value) == True:
                return (True, {'age': age})
            else:
                return (False, {'age': age})
        else:
            echo.focus.set_start_end_datetime( start_time, end_time )
            measurements = echo.gather.get_measurement_by_concept_focused(self.concept)

        measurements_meet = []
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




    def if_visit_meet_filter (self, visit, echo):

        echo.set_focus(visit)

        measurements = []

        if ( self.concept == CONST.AGE ):
            time_on_visit = visit.get_start_datetime
            patient = visit.get_person()
            age = patient.how_old_at (time_on_visit)

            if compare( age, self.operator, self.value ) == True:
                return (True, { 'age': age }  )
            else:
                return (False, {'age': age})

        else:
            echo.focus.set_start_end_datetime( visit.get_start_datetime(), visit.get_end_datetime() )
            measurements = echo.gather.get_measurement_by_concept_focused(self.concept)

        measurements_meet = []
        measurements_not_meet = []

        for measurement in measurements:

            if compare(measurement.value, self.operator, self.value) == True:
                measurements_meet.append(measurement)
            else:
                measurements_not_meet.append(measurement)

        if (len(measurements_meet) >= 1):
            return (True, {'measurements_meet_criteria': measurements_meet, 'measurements_not_meet_criteria': measurements_not_meet})
        else:
            return (False, {'measurements_meet_criteria': measurements_meet, 'measurements_meet_criteria': measurements_not_meet})

        return

    def if_patient_meet_filter (self, visit, echo):
        echo.set_focus(visit)

        labs =  echo.gather.get_measurement_by_concept_unfocused( self.concept )
        labs_meet = []
        labs_not_meet = []

        for lab in labs:

            if compare(lab.value, self.operator, self.value) == True:
                labs_meet.append(lab)
            else:
                labs_not_meet.append(lab)


        if ( len(labs_meet) >= 1 ):
            return (True, { 'labs_meet_criteria': labs_meet, 'labs_not_meet_criteria': labs_not_meet } )
        else:
            return (False, {  'labs_meet_criteria': labs_meet, 'labs_not_meet_criteria': labs_not_meet })