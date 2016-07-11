
import EchoKit
import CohortBuilder
import Criteria
import CohortFilters
from datetime import timedelta
from datetime import time

from OHDSIConstants import CONST

loader = EchoKit.Loader( dbname = "mimic2", user = "jpark", password = "pc386pc386" )

echo = EchoKit.Echo( loader.get_connection() )
#echo.shutup()
echo.hello_echo()

visits = echo.gather.get_random_visits(2)

echo.set_focus( visits[0] )


echo.focus.set_time_point( visits[0].get_start_datetime(), duration = timedelta( hours = 4) )
measures = echo.gather.get_all_measurements_focused()

print("\n\n---- Measurements on ICU Admission ------\n")

for measure in measures:
    print (measure)




echo.focus.set_time_point( visits[0].get_first_6am_datetime(), duration = timedelta(hours=4) )
measures = echo.gather.get_all_measurements_focused()

print("\n\n---- Day 1 in the ICU ------\n\nBP trend -->\n")



maps = echo.gather.get_measurement_by_concept_focused( CONST.MEAN_ARTERIAL_PRESSURE )

if len(maps) == 0:
    print("Note: Arterial BP was not measured in this patient.")

for map in maps:
    print (map)

print("\n# Other Labs ##\n")

for measure in measures:
    print (measure)

next_day_exist = echo.focus.hours_later(hours=24)
measures = echo.gather.get_all_measurements_focused()

if len(measures) >= 1:
    print("\n\n---- Day 2 in the ICU ------")

    for measure in measures:
        print (measure)


cohort = CohortBuilder.EventCohortBuilder(echo)
infection_filter = CohortFilters.SignificantInfectionFilter ()
age_filter = CohortFilters.NumericConceptFilter (concept = CONST.AGE, operator = '>=', value = 25)
hgb_filter = CohortFilters.NumericConceptFilter (concept = CONST.HEMOGLOBIN, operator = '<=', value = 8)
cohort.set_event_type ('daily_morning')
cohort.set_inclusion_filters ( [infection_filter, age_filter, hgb_filter] )
cohort.build(  )
(visit, start_time, end_time, index, total) = cohort.next()



'''
hgb_filter = CohortFilters.NumericConceptFilter (concept = CONST.HEMOGLOBIN, operator = '<=', type = 'once_at_least', value = 8)

cohort = CohortBuilder.EventCohortBuilder(echo)
cohort.set_event_type( 'dailymorning') # 2-10am daily morning for each patient. center = 6am
cohort.set_inclusion_criteria( [infection_filter, age_filter, hgb_filter] )

(visit, start_time, end_time, index) = cohort.next()

septic_shock_filter = CohortFilters.SepticShockWithinFilter( is_sepsis3 = True, within = timedelta(hours=24) )
if ( septic_shock_filter.if_meet_filter(echo) == True ):
    print("Developed septic shock within 24 hours")
else:
    print("Didn't develop septic shock within 24 hours")
'''



#echo.focus.set_time_point( timepoint = visits[0].get_start_datetime()  )
#echo.focus.set_start_end_datetime( start_datetime = visits[0].get_start_datetime(), end_datetime = visits[0].get_end_datetime() )
#echo.focus.hours_later(7)
#echo.focus.days_later(2)

#echo.ask.if_died_during_the_visit()
#echo.ask.if_died_focused_period()

#labs = echo.gather.get_measurement_by_concept_unfocused( CONST.HEMOGLOBIN )

#for lab in labs:
#    print( lab )

#print("\n\nNow let's focused on certain time period.. \n")


#labs = echo.gather.get_measurement_by_concept_focused( CONST.HEMOGLOBIN )

#for lab in labs:
#    print( lab )

#hgb_filter = CohortFilters.NumericConceptFilter (concept = CONST.HEMOGLOBIN, operator = '<=', value = 10)
#hct_filter = CohortFilters.NumericConceptFilter (concept = CONST.HEMATOCRIT, operator = '>=', value = 25  )
#patient_filtered = hgb_filter.if_patient_meet_filter ( visits[0], echo )
#visit_filtered = hgb_filter.if_visit_meet_filter ( visits[0], echo )


# filtering septic shock for one single date_time for one visit
#septic_shock_filter = CohortFilter.SepticShockWithinFilter( is_sepsis3 = True, within = timedelta(hours=24) )


'''

# filtering septic shock within 24 horus.
septic_shock_filter = CohortFilter.SepticShockWithinFilter( is_sepsis3 = True, within = timedelta(hours=24) )




# every morning moment, related to the development of septic shock within 48 hours.

septic_moment_cohort_builder = CohortBuilder.TimeCohortBuilder(echo)
# check every 8am for the development of septic shock within 24 hours
septic_moment_cohort_builder.set_absolute_time( time_point = time(hour=8), duration = timedelta(hours=3) )
septic_moment_cohort_builder.set_inclusion_filters( age_filter, septic_shock_filter )

list = septic_moment_cohort_builder.build()


# visit with septic shock at any moment

septic_visit_cohort_builder = CohortBuilder.VisitCohortBuilder(echo)
septic_moment_cohort_builder.set_inclusion_filters( age_filter, septic_shock_filter )


'''
# every morning moment, not related to the development of septic shock within 48 hours.


# returns positive

#moment_cohort_builder = CohortBuilder.MomentCohortBuilder(relative_to_visit_start_time = timedelta(hours=0), echo)

#morning_measurements_filtered_for_septic_shock = septic_shock_filter.if_moment_meet_filter( visit = visits[0] )

# potential targets:
# a morning focus / chem7+cbc timing which -> ended up with septic shock within 48 hours


#print("\n\n--FOR THE ALL VISITS FOR THE PATIENT--\n")

#print( "===================== Hgb <= than 10")

#for lab in patient_filtered[1]['labs_meet_criteria']:
#    print(lab)

#print( "\n===================== Hgb > than 10")

#for lab in patient_filtered[1]['labs_not_meet_criteria']:
#    print(lab)


#print("\n\n--ONLY FOR THE SPECIFIC VISIT--\n")

#print( "===================== Hgb <= than 10")

#for lab in visit_filtered[1]['labs_meet_criteria']:
#    print(lab)

#print( "\n===================== Hgb > than 10")

#for lab in visit_filtered[1]['labs_not_meet_criteria']:
#    print(lab)

#visit_cohort_builder = CohortBuilder.VisitCohortBuilder(echo)
#visit_cohort_builder.set_inclusion_filters ( [hgb_filter] )

#visit_id_list = visit_cohort_builder.get_cohort_visit_list()
#visit_id_list = visit_cohort_builder.get_cohort_day_list()
#print(visit_id_list)


#print( "===================== Hgb >= 10")

#cohort_builder = CohortBuilder(echo)
#cohort_builder.return_type = CONST.VISIT

#infection_inclusion_filter = CohortBuilder.InfectionFilter()
#age_inclusion_filter = CohortBuilder.ConceptFilter( concept = CONST.AGE, operator = '>=', value = 45 )



#orientation_inclusion_filter = CohortBuilder.OrientationFileter ( operator = '>=', value = 2  )
#SOFA_inclusion_filter = CohortBuilder.SOFAFilter( type = 'on_admin', operator = '>=', value = 4 )

#cohort_builder.set_inclusion_criteria ( [age_inclusion_filter, orientation_inclusion_filter, SOFA_inclusion_filter] )
#cohort_builder.set_exclusion_criteria ( [] )

#visits = cohort_builder.get_cohort_visits()


'''

inclusion_filters = [ infection_inclusion_filter ]
cohort_builder.set_inclusion_criteria ( inclusion_filters )


age_inclusion_filter = CohortBuilder.CohortFilter ( gatherer = gatherer_by_id(CONST.AGE), operator = '>=', value = 45 )
sex_inclusion_filter = CohortBuilder.CohortFilter ( gatherer = gatherer_by_id(CONST.SEX), operator = '=', value = CONST.MALE )
SOFA_inclusion_filter = CohortBuilder.CohortFilter ( gatherer = initial_SOFA_gatherer(), operator = '<=', value = 15 )
age_exclusion_filter = CohortBuilder.CohortFilter ( gatherer = gatherer_by_id(CONST.AGE), oeprator = '>=', value = 100  )

filters = [age_inclusion_filter, sex_inclusion_filter]

cohort_builder.set_inclusion_criteria ( filters )
cohort_builder.set_exclusion_criteria ( [age_exclusion_filter] )

visits = cohort_builder.get_cohort()
'''



# cohort_builder.set_selection_timing ( CONST.ON_ICU_ADMISSION )



#criteria = Criteria(   )


#for visit in visits:
 #   visit.description()

# Test Project: Age on admission + The lowest SBP during the three days of ICU stays predict mortality?
# Build criteria and feed gatherer --> Next. Next. Next.
# echo.gather.pick_single_patient( criteria )
# echo.gather.pick_focuses( criteria )


# every morning, after the morning lab. let's say 8-9am in the morning.
# get all the lab in the morning. Expand focus changing start time 24-48 hours so that collect important labs.
# gathering --> get_morning_labs() should be available?