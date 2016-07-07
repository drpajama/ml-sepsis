
class Cursor:
    start_time = None
    end_time = None
    target_subject = None
    target_visit = None

    def set_subject(self, subject):
        target_subject = subject

    def set_visit(self, visit):
        target_visit = visit
        target_subject = visit.get_subject()


class HourCursor(Cursor):

class DayCursor(Cursor):

class CursorCustomDuration(Cursor):

