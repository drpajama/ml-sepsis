
import datetime
import ClinicalData

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

#class RelativeTimeIntervalGenerator:

class TimePointCohortBuilder(CohortBuilder):
    type = None
    list = []


    def __init__(self, echo):
        self.echo = echo
        return



class PeriodCohortBuilder(CohortBuilder):

    type = None
    cohort_list = []

    def __init__(self, echo):
        self.echo = echo
        return

    def set_event_type(self, type):
        self.type = type

    def next(self):
        return (1, 1, 1, 1, 1, 1)

    def set_inclusion_filters(self, filters):
        self.inclusion_filters = filters

    def __repr__(self):
        temp = ""
        i = 1
        for single in self.cohort_list:
            temp = temp + "#" + str(i) + " " + str(single)
            i = i + 1

        return temp

    def build(self):

        number_of_total_icu_visits = self.echo.ask.how_many_total_icu_visits()

        # Index is total number of ICU visit - 1 (as it starts from 0)
        max_visit_index =  number_of_total_icu_visits - 1

        # for tests (will be removed later)
        max_visit_index = 4
        cohort_list = []

        for index in range (0, max_visit_index ):
            visit = self.echo.gather.get_icu_visit_by_index(index)

            print (visit)

            duration = visit.get_duration()
            start_time = visit.get_start_datetime()
            one_day_later = start_time + datetime.timedelta( hours = 24)
            first_morning = datetime.datetime( year=one_day_later.year, month = one_day_later.month, day= one_day_later.day, hour=6  )
            one_day_interval = datetime.timedelta(hours=24)

            # Notably, this delta-time could be > 24 hours (maximum around ~28 hours)
            admission_to_first_morning = (first_morning - start_time)

            self.echo.focus.set_start_end_datetime( start_time, visit.get_end_datetime() )
            was_the_patient_in_the_icu_in_the_first_morning = self.echo.focus.if_fall_into ( first_morning )

            if was_the_patient_in_the_icu_in_the_first_morning == True:
                total_day_hour_first_morning = (duration - admission_to_first_morning).total_seconds() / 3600
                total_day_since_first_morning = int(total_day_hour_first_morning / 24)
                number_of_morning = total_day_since_first_morning + 0   # The last day is ignored.
            else:
                number_of_morning = 0



            for i in range(0, number_of_morning):
                plusminus = datetime.timedelta(hours=4)
                morning_time = start_time + admission_to_first_morning + datetime.timedelta(hours=24 * i)
                morning_start_time = morning_time - plusminus
                morning_end_time = morning_time + plusminus
                self.echo.set_focus(visit)

                person_period = ClinicalData.PersonPeriod ( visit.get_person(), morning_start_time, morning_end_time, morning_time )
                self.cohort_list.append  ( person_period )


        '''
        tuple_array = []
        visit_index = 0



        '''
        '''if (self.type == 'daily_morning')

        #first_morning =

        for visit_index in range( 0, max_visit_index ):
            non = []
            visit = self.echo.gather.get_visit_by_index ( visit_index )

            duration = visit.get_duration()
            start_time = visit.get_start_datetime()
            one_day_later = start_time + datetime.timedelta( hours = 24)
            first_morning = datetime.datetime( year=one_day_later.year, month = one_day_later.month, day= one_day_later.day, hour=6  )

            first_interval = (first_morning - start_time)


            total_day_hour = (duration - first_interval).total_seconds() / 3600
            total_day = int(total_day_hour / 24)
            number_of_morning = total_day + 1  # patient might get morning lab and leave the ICU.
            one_day_interval = datetime.timedelta(hours=24)

            # on admission
            for i in range (0, number_of_morning):
                ## all morning

                print( "\n====== Day #" + str(i+1) )

                plusminus = datetime.timedelta( hours = 4 )
                morning_time = start_time + first_interval + datetime.timedelta( hours = 24*i )
                morning_start_time = morning_time - plusminus
                morning_end_time = morning_time + plusminus

                self.echo.set_focus(visit)
                print( str(morning_start_time) + " / "+ str(morning_end_time))
                self.echo.focus.set_start_end_datetime(morning_start_time, morning_end_time)

                measurements = self.echo.gather.get_all_measurements_focused()
                for measurement in measurements:
                    print(measurement)

                # on admission
                filters = self.inclusion_filters

                meet_all_inclusion_filters = True

                # check if the visit-period meet all inclusion criteria
                for filter in filters:
                    if filter.if_period_meet_filter(visit, start_time, morning_end_time,
                                                    self.echo)[0] == False:
                        meet_all_inclusion_filters = False

                if (meet_all_inclusion_filters == True):
                    tuple_array.append((visit_index, visit, morning_start_time, morning_end_time))
                else:
                    non.append((visit_index, visit, morning_start_time, morning_end_time))

            '''




        '''
        self.list = tuple_array
        print( self.list )

        print(non)
        '''



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

