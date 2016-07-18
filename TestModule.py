import EchoKit
import CohortBuilder
import Filters
import CohortFilters
from datetime import timedelta
from datetime import time
import TestModule
import ClinicalData
from OHDSIConstants import CONST
from UsefulFunctions import *

def test_reverse_infection(echo):

    age_filter = Filters.NumericConceptFilter(CONST.AGE, '>=', 40, 'on_start')
    infection_filter = Filters.SignificantInfectionFilter()

    cohort = CohortBuilder.PeriodCohortBuilder(echo)
    cohort.set_selection_type('daily_morning')
    cohort.set_visit_type(CONST.ICU_ADMISSION)  # Not general ward

    cohort = CohortBuilder.PeriodCohortBuilder(echo)
    cohort.set_selection_type('daily_morning')
    cohort.set_visit_type(CONST.ICU_ADMISSION)
    cohort.set_inclusion_filters([age_filter])
    cohort.set_exclusion_filters( [infection_filter]  )

    cohort.set_maximum_subject_number(100)
    cohort.build()

    print(cohort)

    #test_target = cohort.get_by_index(2) # antibiotics initiated soon after culture, but only one dose was given and discontinued.
    #test_target = cohort.get_by_index(3) # on cefepime and vanco but never cultured [confirmed in MIMICIII database]
    #test_target = cohort.get_by_index(4) # the same patient with index-3
    #test_target = cohort.get_by_index(7) # one dose of ceftriaxone was given but never cultured. [confirmed in MIMICIII database]
    test_target = cohort.get_by_index(10) # never cultured. note that 2 doses of zosyn was given on 5/23 but the afternoon dose was excluded from the list shown below. (as our focus range is 2~10am)

    print(test_target)

    hospitalization = echo.gather.get_hospitalization(test_target.person.person_id,
                                                      test_target.start_datetime)
    admission_time = hospitalization.get_start_datetime()

    echo.set_focus(test_target)
    echo.focus.set_start_end_datetime(admission_time, test_target.axis_datetime)

    antibiotics_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.ANTIBIOTICS)
    first_dose_exposures = echo.gather.get_only_first_doses(antibiotics_exposures)

    print("======== ABx Given ")
    print_list(antibiotics_exposures)

    print("\n======== ABx Given: First Doses ")
    print_list(first_dose_exposures)

    cultures = echo.gather.get_all_procedure_occurrence_focused_by_concept_id_list(
        [CONST.BLOOD_CULTURE, CONST.URINE_CULTURE, CONST.STOOL_CULTURE, CONST.CSF_CULTURE, CONST.WOUND_CULTURE],
        ['pan culture'])

    print("\n======== Culture List ")
    print_list(cultures)

    reasoning_for_filtering = infection_filter.if_period_meet_filter(test_target, echo)
    print (reasoning_for_filtering)



def test_infection_cohort(echo):
    cohort = CohortBuilder.PeriodCohortBuilder(echo)
    cohort.set_selection_type('daily_morning')
    cohort.set_visit_type(CONST.ICU_ADMISSION)  # Not general ward

    infection_filter = Filters.SignificantInfectionFilter()
    age_filter = Filters.NumericConceptFilter(CONST.AGE, '>=', 25, 'on_start')
    cohort.set_inclusion_filters([age_filter, infection_filter])

    cohort.set_maximum_subject_number(100)
    cohort.build()

    print(cohort)
    target = cohort.next()


    ## Testing
    pause()

    test_target = cohort.get_by_index(13)
    print( test_target )

    hospitalization = echo.gather.get_hospitalization(test_target.person.person_id,
                                                      test_target.start_datetime)
    admission_time = hospitalization.get_start_datetime()

    echo.set_focus (test_target)
    echo.focus.set_start_end_datetime(admission_time, test_target.axis_datetime)

    antibiotics_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.ANTIBIOTICS)
    first_dose_exposures = echo.gather.get_only_first_doses(antibiotics_exposures)

    print_list(antibiotics_exposures)
    print_list(first_dose_exposures)

    cultures = echo.gather.get_all_procedure_occurrence_focused_by_concept_id_list(
        [CONST.BLOOD_CULTURE, CONST.URINE_CULTURE, CONST.STOOL_CULTURE, CONST.CSF_CULTURE, CONST.WOUND_CULTURE],
        ['pan culture'])

    print_list(cultures)

    reasoning_for_filtering = infection_filter.if_period_meet_filter(target, echo)
    print ( reasoning_for_filtering )

    pause()



def small_cohort_building(echo):
    cohort = CohortBuilder.PeriodCohortBuilder(echo)
    cohort.set_selection_type('daily_morning')
    cohort.set_visit_type(CONST.ICU_ADMISSION)  # Not general ward

    #infection_filter = Filters.SignificantInfectionFilter()
    age_filter = Filters.NumericConceptFilter(CONST.AGE, '>=', 40, 'on_start')
    cohort.set_inclusion_filters([age_filter])

    cohort.set_maximum_subject_number(100)
    cohort.build()

    print(cohort)
    target = cohort.next()

    print(cohort)

    cohort.build_anti_cohort()
    print(cohort)

    # echo.get_discharge_summary()

def test_septic_shock_filter(echo):

    visit = echo.gather.get_random_icu_visits(1)[0]

    target = ClinicalData.PersonPeriod( visit.get_person(), visit.get_start_datetime(), visit.get_end_datetime() )

    echo.set_focus (target)
    filter_shock = Filters.SepticShockFilter( infection_known = False )


    print( filter_shock.if_period_meet_filter(target, echo) )


def test_infection_filter(echo):

    cohort = CohortBuilder.PeriodCohortBuilder(echo)
    cohort.set_selection_type('daily_morning')
    cohort.set_visit_type(CONST.ICU_ADMISSION)  # Not general ward

    infection_filter = Filters.SignificantInfectionFilter()
    age_filter = Filters.NumericConceptFilter(CONST.AGE, '>=', 40, 'on_start')
    cohort.set_inclusion_filters([age_filter])

    cohort.set_maximum_subject_number(200)
    cohort.build()

    target = cohort.get_by_index(13)

    print(target)
    echo.set_focus(target)

    if_target_has_significant_infection = infection_filter.if_period_meet_filter(target, echo)
    print(if_target_has_significant_infection)

    #echo.get_discharge_summary()


def test(echo):
    icu_visits = echo.gather.get_random_icu_visits(2)

    print(icu_visits[0])
    echo.shutup()

    echo.set_focus(icu_visits[0])
    echo.focus.set_time_point(icu_visits[0].get_start_datetime(), duration=timedelta(hours=4))

    measures = echo.gather.get_all_measurements_focused()

    print("\n\n---- Measurements on ICU Admission ------\n")

    for measure in measures:
        print (measure)

    echo.focus.set_time_point(icu_visits[0].get_first_6am_datetime(), duration=timedelta(hours=4))

    measures = echo.gather.get_all_measurements_focused()

    print("\n\n---- Day 1 in the ICU ------\n\nBP trend -->\n")

    maps = echo.gather.get_measurement_by_concept_focused(
        [CONST.MEAN_ARTERIAL_PRESSURE_INVASIVE, CONST.MEAN_ARTERIAL_PRESSURE_NONINVASIVE])

    for map in maps:
        print (map)

    print("\n# Other Labs ##\n")

    for measure in measures:
        print (measure)

    print("\n---Progress note of Day 1")
    print(echo.get_resident_progress_note())

    next_day_exist = echo.focus.hours_later(hours=24)
    print(next_day_exist)
    measures = echo.gather.get_all_measurements_focused()

    if len(measures) >= 1:
        print("\n\n---- Day 2 in the ICU ------")

        for measure in measures:
            print (measure)

    echo.set_focus(icu_visits[0])
    echo.focus.set_start_end_date(icu_visits[0].get_start_datetime(), icu_visits[0].get_end_datetime())

    print("\n---Progress note of Day 2")
    print(echo.get_resident_progress_note())

    print("\n\n------- All antibiotic exposure")
    antibiotics_exposures = echo.gather.get_all_drug_exposure_by_type_unfocused(CONST.ANTIBIOTICS)
    if len(antibiotics_exposures) == 0:
        print("No known exposure to antibiotics")

    for exposure in antibiotics_exposures:
        print (exposure)

    print("\n\n------- Exposure to Antibiotics during the ICU visit.")
    antibiotics_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.ANTIBIOTICS)
    if len(antibiotics_exposures) == 0:
        print("No known exposure to antibiotics")

    for exposure in antibiotics_exposures:
        print (exposure)

    print("\n\n------- Vasopressores")
    vasopressor_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.VASOPRESSORS)
    for exposure in vasopressor_exposures:
        print (exposure)

    print("\n\n----- Procedures")
    procedures = echo.gather.get_all_procedure_occurrence_unfocused()

    for procedure in procedures:
        print(procedure)

    print("\n\n ----- Device Exposures")
    devices = echo.gather.get_all_device_exposure_unfocused()

    for device in devices:
        print(device)

    # print("\n\n----- Discharge Summary")
    # print(echo.get_discharge_summary())




    '''
    septic_shock_filter = CohortFilters.SepticShockWithinFilter( is_sepsis3 = True, within = timedelta(hours=24) )
    '''




def pause():
    programPause = raw_input("Press the <ENTER> key to continue...")