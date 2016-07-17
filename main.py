
import EchoKit
import CohortBuilder
import Criteria
import Filters
import CohortFilters
from datetime import timedelta
from datetime import time
import TestModule

from OHDSIConstants import CONST

loader = EchoKit.Loader( dbname = "mimic", user = "jpark", password = "pc386pc386" )

echo = EchoKit.Echo( loader.get_connection() )
echo.hello_echo()
echo.shutup()

cohort = CohortBuilder.PeriodCohortBuilder(echo)
cohort.set_selection_type ('daily_morning')

age_filter = Filters.NumericConceptFilter( CONST.AGE, '>=', 40, 'on_start')
cohort.set_inclusion_filters( [age_filter] )

cohort.set_maximum_subject_number( 200 )
cohort.build()


print(cohort)
target = cohort.next()

cohort.build_anti_cohort()
print(cohort)


'''filtered = age_filter.if_period_meet_filter( target, echo )
print(filtered)

#print(cohort)
print(target)
target = cohort.next()
filtered = age_filter.if_period_meet_filter( target, echo )
print(filtered)
'''

#infection_filter = CohortFilters.SignificantInfectionFilter ()



