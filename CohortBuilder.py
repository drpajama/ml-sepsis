
class Filter(object):
    echo = None

    def __init__(self, echo ):
        self.echo = echo
        return

class AntibioticsAdministrationFilter (Filter):



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

