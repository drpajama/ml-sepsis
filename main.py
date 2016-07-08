
import EchoKit
import Criteria
from OHDSIConstants import CONST

loader = EchoKit.Loader( dbname = "mimic2", user = "jpark", password = "pc386pc386" )

echo = EchoKit.Echo( loader.get_connection() )
echo.hello_echo()

visits = echo.gather.get_random_visits(2)
echo.set_focus( visits[0] )
echo.focus.set_time_point( timepoint = visits[0].get_start_datetime()  )
echo.focus.set_start_end_datetime( start_datetime = visits[0].get_start_datetime(), end_datetime = visits[0].get_end_datetime() )
echo.focus.hours_later(7)
echo.focus.days_later(2)

echo.ask.if_died_during_the_visit()
echo.ask.if_died_focused_period()

labs = echo.gather.get_measurement_by_concept_unfocused( CONST.HEMOGLOBIN )
labs = labs + echo.gather.get_measurement_by_concept_unfocused( CONST.HEMATOCRIT )

for lab in labs:
    lab.description()


#echo.ask_if_patient_died_during_the_focused_period()

visits[0].get_person().description()

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