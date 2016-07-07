
import EchoKit

loader = EchoKit.Loader( dbname = "mimic2", user = "jpark", password = "pc386pc386" )

echo = EchoKit.Echo( loader.get_connection() )
echo.hello_echo()

visits = echo.get_random_visits(2)
echo.set_focus( visits[0] )
echo.focus.set_time_point( timepoint = visits[0].get_start_datetime()  )
echo.focus.set_start_end_datetime( start_datetime = visits[0].get_start_datetime(), end_datetime = visits[0].get_end_datetime() )
echo.focus.hours_later(7)
echo.focus.days_later(2)

echo.ask_if_patient_died_during_the_visit()
echo.ask_if_patient_died_focused_period()
#echo.ask_if_patient_died_during_the_focused_period()

for visit in visits:
    visit.description()


    #Genie.Whether.patient_died_during_period(conn, )