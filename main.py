
import EchoKit
import CohortBuilder
import Filters
import CohortFilters
from datetime import timedelta
from datetime import time
import TestModule
import ClinicalData

from UsefulFunctions import *
from OHDSIConstants import *

loader = EchoKit.Loader( dbname = "mimic", user = "jpark", password = "pc386pc386" )

echo = EchoKit.Echo( loader.get_connection() )
echo.hello_echo()
echo.shutup()

#TestModule.test_infection_cohort(echo)
#TestModule.test_septic_shock_filter(echo)
#TestModule.test_reverse_infection(echo)
#TestModule.small_cohort_building(echo)
#TestModule.test_infection2_filter(echo)


'''
cohort = CohortBuilder.PeriodCohortBuilder(echo)
cohort.set_selection_type ('daily_morning')
cohort.set_visit_type( CONST.ICU_ADMISSION ) # Not general ward

infection_filter = Filters.SignificantInfectionFilter()
age_filter = Filters.NumericConceptFilter( CONST.AGE, '>=', 40, 'on_start')
cohort.set_inclusion_filters( [age_filter] )

cohort.set_maximum_subject_number( 200 )
cohort.build()
'''

#print(cohort)
#target = cohort.next()


# Culture-Abx relationship. See the subject 82010.
'''target = cohort.get_by_index(13)


print(target)
echo.set_focus ( target )

if_target_has_significant_infection = infection_filter.if_period_meet_filter(target, echo)
print(if_target_has_significant_infection)
'''

#print abx_exposures[0]


#test_exposure = ClinicalData.DrugExposure(person_id = 82010, drug_concept_id = 17711612, drug_type_id= 21603553, start_time = admission_time, end_time = discharge_time, dose=1,dose_unit_id=8513, route=CONST.ADMINISTRATION_INTRAVENOUS, name = "cefazolin/Trimethoprim" )

#print abx_exposures[0].if_the_same_with(test_exposure)

#if_first_dose = abx_exposures[0].if_the_first_dose ( abx_exposures, echo ) # it will also find the real first dose if the answer is no



#print_list(abx_exposures)



#print_list(cultures)

#cohort.build_anti_cohort()
#print(cohort)


'''filtered = age_filter.if_period_meet_filter( target, echo )
print(filtered)

#print(cohort)
print(target)
target = cohort.next()
filtered = age_filter.if_period_meet_filter( target, echo )
print(filtered)
'''

#infection_filter = CohortFilters.SignificantInfectionFilter ()



