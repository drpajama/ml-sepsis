
import EchoKit
import CohortBuilder
import Criteria
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

cohort = CohortBuilder.PeriodCohortBuilder(echo)
cohort.set_selection_type ('daily_morning')
cohort.set_visit_type( CONST.ICU_ADMISSION ) # Not general ward

infection_filter = Filters.SignificantInfectionFilter()
age_filter = Filters.NumericConceptFilter( CONST.AGE, '>=', 40, 'on_start')
cohort.set_inclusion_filters( [age_filter] )

cohort.set_maximum_subject_number( 200 )
cohort.build()


#print(cohort)
#target = cohort.next()

target = cohort.get_by_index(5)

print(target)
echo.set_focus ( target )

axis_time = target.axis_datetime  # 6am
cohort_start_time = target.start_datetime # 2am
cohort_end_time = target.end_datetime # 10am
hospitalization = echo.gather.get_hospitalization( target.person.person_id, target.start_datetime ) # the record of the entire hospitalization which the current cohort belongs to.

admission_time = hospitalization.get_start_datetime()
discharge_time = hospitalization.get_end_datetime()

echo.focus.set_start_end_datetime( admission_time, axis_time ) # between admission - current time
abx_exposures = echo.gather.get_all_drug_exposure_by_type_focused( CONST.ANTIBIOTICS )
cultures = echo.gather.get_all_procedure_occurrence_focused_by_concept_id_list ( [CONST.BLOOD_CULTURE, CONST.URINE_CULTURE, CONST.STOOL_CULTURE,CONST.CSF_CULTURE] ) # PANCULTURE MISSED!

print abx_exposures[0]


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



