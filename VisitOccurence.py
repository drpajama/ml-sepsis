from datetime import datetime

class ICUVisit:

    def __init__(self, visit_id, person_id, start_date, start_time, end_date, end_time, care_site):

        self.visit_id = visit_id
        self.person_id = person_id

        self.start_date = start_date
        self.start_time = datetime.strptime(start_time, '%H:%M:%S')

        self.end_date = end_date
        self.end_time = datetime.strptime(end_time, '%H:%M:%S')

        self.care_site = care_site

    def get_duration_date(self):
        return self.end_date - self.start_date

    def description(self):
        print("")
        print("Visit ID: " + str(self.visit_id) )
        print("Patient ID: " + str(self.person_id) )
        print("CareSite: " + self.care_site.description() )
        print("Duration: stayed in the ICU starting from " + str(self.start_date) + " until " + str(self.end_date)  + " (Total: " + str(self.get_duration_date().days) + " days)" )
