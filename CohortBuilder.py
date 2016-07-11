
import datetime

class CohortBuilder:
    echo = None
    index = 0

    inclusion_filters = []
    exclusion_filters = []

    def check_for_visit ( self, visit ):

        inclusion_failed = 0

        for filter in self.inclusion_filters:
            if filter.if_patient_meet_filter(visit, self.echo) == False:
                inclusion_failed = inclusion_failed + 1

        if inclusion_failed == 0:
            return True
        else:
            return False


    def get_cohort_visit_list(self):

        number_of_visits = self.echo.ask.how_many_total_visits()
        count_of_cycles = number_of_visits / 100
        left_after_cycles = number_of_visits % 100
        all_visit_id = self.echo.gather.get_all_visit_id()
        id_list = []

        i = 1
        print( count_of_cycles )
        for x in range(0, count_of_cycles):
            for j in range(0, 100):
                visit = self.echo.gather.get_visit_by_id(all_visit_id[i])
                if ( self.check_for_visit(visit) == True ):
                    id_list.append( i )
                i = i + 1

        for x in range(0, left_after_cycles-1):
            visit = self.echo.gather.get_visit_by_id ( all_visit_id[i] )
            if (self.check_for_visit(visit) == True):
                id_list.append(i)
            i = i + 1



        return number_of_visits


    def set_inclusion_filters(self, filters):
        self.inclusion_filters = filters

    def set_exclusion_filters(self, filters):
        self.exclusion_filters = filters



class EventCohortBuilder(CohortBuilder):

    type = None

    def __init__(self, echo):
        self.echo = echo
        return

    def set_event_type(self, type):
        self.type = type

    def next(self):
        return

    def set_inclusion_filters(self, filters):
        self.inclusion_filters = filters

    def build(self):

        tuple_array = []
        visit_index = 0

        number_of_visits = self.echo.ask.how_many_total_visits()

        for visit_index in range( 0, number_of_visits-1 ):
            visit = self.echo.gather.get_visit_by_index ( visit_index )
            print (visit)

        if (type == 'daily_morning'):
            self.echo.set_focus( visit )
            self.echo.focus.set_time_point(visit.get_start_datetime(), duration=datetime.timedelta(hours=4))







class VisitCohortBuilder(CohortBuilder):

    def __init__(self, echo):
        self.echo = echo
        return



class Filter(object):
    echo = None

    def __init__(self, echo ):
        self.echo = echo
        return

#class ConceptFilter (Filter):



#class AntibioticsAdministrationFilter (Filter):



'''class CultureFilter (Filter):'''



class SignificantInfectionFilter (Filter):

    def process_visit( self, visit ):
        # returns tuple of (Bool, {dict/detail} )
        '''Sepsis-3 criteria for infection in EHR [Feb 2016, JAMA]:
            (1) Combination of culture sampling (blood, urine, CSF, etc) and start time to occur within a specific time epoch
                -> a. if antibiotics was given first, the culture sampling must have been obtained within 24 hours.
                   b. If the culture sampling was first, the antibiotic must have been ordered within 72 horus.
                   c. the onset of infection was defined as the time at which the first of these 2 events occured.

            return_value = []
            lab_abx_combinations = [ ]

            echo.set_focus ( visit )
            cultures = echo.gather.get_measurements_by_id ( CONST.BLOODCULTURE )
            cultures = cultures + echo.gather.get_measurements_by_id ( CONST.URINECULTURE )
            cultures = cultures + echo.gather.get_measurements_by_id ( CONST.CSFCULTURE )
            cultures = cultures + echo.gather.get_measurements_by_id ( CONST.OTHERCULTURE )

            for culture in cultures:
                echo.focus.set_start_datetime_with_duration (  culture.get_date_time(), deltatime( hours = 72) )
                answer = echo.ask.if_given_new_antibiotics()

                if ( answer[0] == True ):

                    culture_event = culture
                    antibiotics_administration_event = answer[1]

                    return_value.append(  (culture_event, antibiotics_event)  )

            if ( len(return_value) == 0 ):
                return ( True, {'administration_culture_events': return_value} )
            else:
                return ( False, {} )

        '''





class CohortBuilder:
    echo = None
    focus = None
    filters = None

    inclusion_criteria = None
    exclusion_criteria = None


    def __init__(self, echo):
        self.echo = echo
        self.focus = echo.focus

    def get_cohort(self):
        return


class CohortFilter:

    value = None
    operator = None

    data_gatherer = None

