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

    def get_start_datetime(self):
        return datetime(year=self.start_date.year, month=self.start_date.month, day=self.start_date.day,
                        hour = self.start_time.hour, minute= self.start_time.minute, second = self.start_time.second)

    def get_end_datetime(self):
        return datetime(year=self.end_date.year, month=self.end_date.month, day=self.end_date.day,
                        hour=self.end_time.hour, minute=self.end_time.minute, second=self.end_time.second)

    def get_duration_date(self):
        return self.end_date - self.start_date

    def get_duration_datetime(self):
        return self.get_end_datetime() - self.get_start_datetime()

    def description(self):
        print("")
        print("Visit ID: " + str(self.visit_id) )
        print("Patient ID: " + str(self.person_id) )
        print("CareSite: " + self.care_site.description() )
        print("Duration: stayed in the ICU starting from " + str(self.get_start_datetime()) + " until " + str(self.get_end_datetime())  + " (Total: " + str(self.get_duration_datetime()) + " )" )
