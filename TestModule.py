import EchoKit
import CohortBuilder
import Filters
import CohortFilters
from datetime import timedelta
from datetime import time
from datetime import date
import TestModule
import ClinicalData
from OHDSIConstants import CONST
from UsefulFunctions import *

def cohort_any_shock(echo):

    cohort = CohortBuilder.PeriodCohortBuilder(echo)
    cohort.set_selection_type('daily')
    cohort.set_visit_type(CONST.ICU_ADMISSION)  # Not general ward


    shock_filter = Filters.AnyShockFilter()
    age_filter = Filters.NumericConceptFilter(CONST.AGE, '>=', 20, 'on_start')
    cohort.set_inclusion_filters([age_filter, shock_filter])



    cohort.set_maximum_subject_number(100)
    responder = 0

    inp = raw_input('Who are you?? \n\n1. Researcher a (Joongheum Park)\n2. Researcher b\n\nAnswer>')
    if inp == '1':
        responder = 1
    elif inp == '2':
        responder =2
    else:
        raise ValueError



    print("Building Cohort......\n(Critiera: vasopressor use with an episode of lowest BP 75)")
    cohort.build()
    cohort.populate_cohort_table(196236, echo)

    print(cohort)
    target = cohort.next()

    target = cohort.get_by_index(12)

    hospitalization = echo.gather.get_hospitalization(target.person.person_id,
                                                      target.start_datetime)
    admission_datetime = hospitalization.get_start_datetime()

    echo.set_focus (target)



    print(target)
    inp = raw_input('We will show the daily summary of a patient: ' + str(target.person.person_id) + ' during the period of ' + str(target.start_datetime) + '-' + str(target.end_datetime) + '\n<Press Enter>\n')

    #temp_echo = echo.copy()
    #temp_echo.focus.set_start_end_datetime( admission_datetime, target.axis_datetime )

    cultures = echo.gather.get_all_procedure_occurrence_unfocused_by_concept_id_list(
        [CONST.BLOOD_CULTURE, CONST.URINE_CULTURE, CONST.STOOL_CULTURE, CONST.CSF_CULTURE, CONST.WOUND_CULTURE],
        ['pan culture', 'bal fluid culture'])

    inp = raw_input("<Enter> to see the pressor use of the day")
    print("====================== Pressor Use (of the day) ==============================")
    pressor_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.VASOPRESSORS)
    print_list(pressor_exposures)

    inp = raw_input("<Enter> to see the BP trend of the day")
    print("======================== BP Trend (of the day) ==============================")
    maps = echo.gather.get_measurement_by_concept_focused(
        [CONST.MEAN_ARTERIAL_PRESSURE_INVASIVE, CONST.MEAN_ARTERIAL_PRESSURE_NONINVASIVE])
    print_list (maps)

    inp = raw_input("<Enter> to see the culture since admission day")
    print ("================= Cultures (since the admission) =================")
    print_list(cultures)

    all_abx = echo.gather.get_all_drug_exposure_by_type_unfocused(CONST.ANTIBIOTICS)
    antibiotics_exposures = echo.gather.get_all_drug_exposure_by_type_focused(CONST.ANTIBIOTICS)
    first_dose_exposures = echo.gather.get_only_first_doses(antibiotics_exposures)

    inp = raw_input("<Enter> to see the antiobitcs given during the ICU visit")
    print("\n======== ABx Given (during the ICU visit) ====== ")
    print_list(antibiotics_exposures)

    inp = raw_input("<Enter> to see the entire history of antibiotic use during the hospitalization")
    print("\n======== ABx Given (all during hospitalization) ====== ")
    print_list(all_abx)

    inp = raw_input("<Enter> to see the lactate levels")
    print("\n======== Lactate (of the day) ========")

    lactate_measurements = echo.gather.get_measurement_by_concept_focused(
        [CONST.LACTATE])

    print_list(lactate_measurements)


    inp = raw_input("<Enter> to see clinical measurements/labs of the day")
    print("\n======== All measurements (of the day) ========")

    lab_measurements = echo.gather.get_all_measurements_focused()
    print_list(lab_measurements)

    print_list(lactate_measurements)

    '''print("\n==== Physician/Nursing Progress Note (of the day - not available often)=====")

    print( echo.get_note_by_name('Nursing') )
    print( echo.get_note_by_name('Physician') )
    '''

    inp = raw_input("<Enter> to see the discharge summary")
    print( "================= Discharge Summary =======================")
    print ( echo.get_discharge_summary() )

    inp = raw_input("<Enter> to make your decision.")
    print("\n================= Type to Decide =====================")

    date_of_shock = date( year = target.start_datetime.year, month = target.start_datetime.month, day =target.start_datetime.day )
    inp = raw_input('What type of shock was the patient experiencing? \n\n1. Septic Shock\n2. Cardiogenic Shock\n3. Hypovolemic Shock\n4. Other types of shock\n5. Shock with very mixed features (unable to determine)\n6. No shock\n7. Others (please specifiy)\n\n')
    if inp == '1':
        print("Okay. I undertood that you think the patient was experiencing septic shock.")
        echo.excuteSQL( "INSERT INTO extension.shock_differential (person_id, date, physician_1, physician_1_note) VALUES( " + str(target.person.person_id) + ",DATE '" + str(date_of_shock) + "' , "+ str(responder) + " , 'No Comment')" )

    elif inp == '2':
        print("Okay. I undertood that you think the patient was experiencing cardiogenic shock.")

    inp = raw_input(
        '\n\nDo you want to continue?\n\n1. Yes\n2. I am done for now. Please save the progress.')

    if inp =='1':
        print("Ok.")

    echo.commit_close_db()

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