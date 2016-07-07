
from OHDSILoader import OHDSILoader

loader = OHDSILoader( dbname = "mimic2", user = "jpark", password = "pc386pc386" )
loader.initialize()

visits = loader.get_visit_occurence()

for visit in visits:
    visit.description()
