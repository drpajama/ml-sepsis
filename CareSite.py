

'''class ICUTypes:
    MedicalICU  = 45881476
    CCU = 45885090
    SurgicalICU = 45877825
    CardiothoracicICU = 45881475
    FICU = 45877824
    NeuroICU = 45881477
    CardicRecovery = 45881475
    PACU = 45880582
    TraumaICU = 45885091
    NSICU = 45881477
    PCU = 4166938
    WARD = 4024317'''


def get_site_by_name(caresites, site_id):

    for site in caresites:
        if site.site_id == site_id:
            return site

    return


class CareSite:
    def __init__(self, site_id, site_name, site_concept_id, site_source_value):
        self.site_id = site_id
        self.site_name = site_name
        self.site_concept_id = site_concept_id
        self.site_source_value = site_source_value

    def description(self):
        return self.site_name + " (Concept ID: " + str(self.site_concept_id) + " / " + self.site_source_value + ")"

    def __repr__(self):
        if self.site_concept_id == 0:
            return "Not Applicable"
        return self.site_name + " (Concept ID: " + str(self.site_concept_id) + " / " + self.site_source_value + ")"