
import EchoKit

loader = EchoKit.Loader( dbname = "mimic2", user = "jpark", password = "pc386pc386" )

echo = EchoKit.Echo( loader.get_db_connection() )
echo.hi_echo()

visits = echo.get_random_visits(2)
echo.set_focus( visits[0] )
echo.ask_if_patient_died_during_the_visit()


for visit in visits:
    visit.description()


    #Genie.Whether.patient_died_during_period(conn, )