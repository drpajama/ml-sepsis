CREATE OR REPLACE FUNCTION is_number(prm_str text) RETURNS BOOLEAN AS $$
DECLARE
  v_return BOOLEAN;
BEGIN
  IF regexp_matches(prm_str,E'^-*[[:digit:]]+\.?[[:digit:]]+$') is not null
  THEN
     v_return = TRUE;
  ELSE
    v_return = FALSE;
  END IF;
  RETURN v_return;
END;
$$ LANGUAGE 'plpgsql';


-- Persons

truncate table ohdsi.person;

INSERT INTO ohdsi.person(person_id, gender_concept_id, year_of_birth, month_of_birth,day_of_birth,race_concept_id, ethnicity_concept_id, gender_source_value)
SELECT subject_id,
 CASE
   when sex = 'M' then 8507
   when sex = 'F' then 8532
   else 8851
 END as gender_concept_id, extract (year from dob),extract (month from dob),extract (day from dob),
0,0, sex
FROM mimic2v26.d_patients;




-- CareSite

/* MIMIC3 data was collected in Beth Israel Deaconess Hospital and these
Table can be populated manually.*/

-- Type of ICU includes:
-- Please See: http://www.bidmc.org/Patient-and-Visitor-Information/Adult-Intensive-Care/About-Adult-IntensiveCareatBIDMC.aspx
-- (1) 'CCU'  : Cardiac/Coronary Care Unit
-- (2) 'MICU' : Medical ICU
-- (3) 'SICU' : Surgical ICU
-- (4) 'FICU' : Called Finard ICU for some historical reason. FICU/SICU combined unit, located on the West Campus (All other units are on the East Campus)
-- (5) 'CSRU' : Cardiac Surgery Recovery Unit
-- (6) 'NICU' : NeuroICU

/* Related Concept Codes
- Adult Critical Care Unit (LOINC/45877824) -> Will use for ICUs without proper concept codes
- Adult Medical Critical Care Unit (LOINC/45881476)
- Adult Coronary Critical Care Unit (LOINC/45885090)
- Adult Cardiothoracic Critical Care Unit (LOINC Meas Value/45881475)
- Adult Coronary Critical Care Unit (LOINC Meas Value/45885090)
- Neuro ICU (LOINC/45881477)
- Surgical ICU (LOINC/45877825)
- Adult Trauma Critical Care Unit (LOINC Meas Value/45885091)
- Postoperative Anethesia Care Unit (LOINC/45880582)
- Special Care Unit (SNOMED/4166938)

-- 'CCU' --> Coronary Unit, 'CTIC' --> Cardiothoracic ICU
-- ''
-- UNKNOWN --> 0
-- T_CTICU -->
-- Regular Ward -->
-- PACU -->
-- PCU -->
-- FICU --> ICU
-- NICU --> Neurologic ICU
-- NSICU --> Neurologic ICU (Could bd Controversial!)
-- CSRU --> Cardiothoracic ICU (Looke like = CTICU?)

*/
-- The website above mentioned that BIDMC has CVISU (not CCU) and Trauamtic ICU but not found in the MIMIC data
-- Note that the table has first_careunit and last_careunit column, which might have the same icu_stay id.
-- For now, the icu type will be just 'ICU' if first_careunit != last_careunit.
-- We will use icustay_id as visit_occurance id.


SELECT * from mimic2v26.icustay_detail
WHERE random () < 0.1;


-- Care Site (Done manually!)

-- Renew the table for care_site
truncate table ohdsi.care_site;

INSERT INTO ohdsi.care_site(care_site_id, care_site_name, place_of_service_concept_id, care_site_source_value, place_of_service_source_value)
VALUES
	(1, 'Adult Medical ICU', 45881476, '69', 'MICU'),
	(2, 'Adult Coronary Care Unit', 45885090, '1', 'CCU'),
	(3, 'Adult Surgical ICU', 45877825, '6', 'SICU'),
	(4, 'Cardiothoracic CCU', 45881475, '2', 'CTIC'),
	-- Finard ICU is a Med+Sug ICU in the west campus of BIDMC. Will be assigned to simply 'ICU'
	(5, 'Finard ICU (Concept_id is simply ICU)', 45877824, '53', 'FICU'),
	(6, 'Neurologic ICU', 45881477, '75', 'NICU'),
	(7, 'Surgical ICU', 45877825, '6', 'SICU'),
	-- Using the concept id for CTICU
	(8, 'Cardiac Surgery Recovery Unit', 45881475, '54', 'CSRU'),
	(9, 'Postoperative Anethesia Care Unit', 45880582, '46', 'PACU'),
	(10, 'Adult Trauma Critical Care Unit', 45885091, '7', 'T_CTICU'),
	-- The is no concept id for NeuroSurgical ICU, so we're using the id for NICU
	(11, 'Neurosurgical ICU', 45881477, '56', 'NSICU'),
	-- There is no concept id for PCI. The id for 'special care unit' is used.
	(12, 'Progressive Care Unit (PCU)', 4166938, '48', 'PCU'),
	(13, 'Regular Ward', 4024317, '8', 'Regular Ward');



-- ICU Stay to Visit Occurence
-- visit occurence can be icu visit, but it might be simply ward visit.
-- we will add 100,000 to the icustay_id, so it could 'overlap' with

truncate table ohdsi.visit_occurrence;


INSERT INTO ohdsi.visit_occurrence (visit_occurrence_id, person_id, visit_concept_id, visit_start_date, visit_start_time, visit_end_date, visit_end_time
	, visit_type_concept_id, provider_id, care_site_id, visit_source_value, visit_source_concept_id)
SELECT icustay_id + 100000 as visit_occurrence_id, subject_id as person_id,
	9201 as visit_concept_id, -- visit ID for 'inpatient visit' (there is no visit domain for ICU stay)
	CAST(icustay_intime as DATE) as visit_start_date,
	CAST(icustay_intime as TIME) as visit_start_time,
	CAST(icustay_outtime as DATE) as visit_end_date,
	CAST(icustay_outtime as TIME) as visit_end_time,
	0 as visit_type_concept_id,
	NULL as provider_id,
	care_site.care_site_id as care_site_id,
	NULL as visit_source_value,
	NULL as visit_source_concept_id
 FROM mimic2v26.icustay_detail
LEFT JOIN ohdsi.care_site ON care_site.place_of_service_source_value = icustay_first_service

/*INSERT INTO visit_occurrence (visit_occurrence_id, person_id, visit_concept_id, visit_start_date, visit_start_time, visit_end_date, visit_end_time, visit_type_concept_id, visit_source_concept_id)
SELECT icustay_id, subject_id, 9203, begintime, pg_catalog.time(begintime), endtime, pg_catalog.time(endtime), 0, 0
FROM mimic2v26.icustay_days;*/









-- ChartedEvent to Measurement

/*

Features selection - features expected to be consistently precise/accurate?

# done: gcs. afib on tele. arterial pressure ('arterial BP' or 'arterial pressure

   PEEP, measured.
   PEEP, setting (VENT)
   lead reading: sinus tachy, afib

# issues: minus arterial pressure? isolation? crackles? (there is snomed code but hard to specify the location.
     could it be an objective measure/feature as it is highly dependent on performer/facility settings?
  Tidal volume setting vs spontaenous tidal volume without vent vs tidal volume observed on ventilation
  some ICU parameters are abscent in CODE: e.g. Mean airway pressure (just 'airway pressure' is present)
temperature locations?

# Measurement Targets of Interest:

(1) Vital Signs, including saturation
(2) Heart Rhythm Reading (Not waveform) - e.g. afib, normal sinus
(3) Precautions
(4) Weight, height
(5) Vent setting (set) and vent monitoring values : set fio2
(6) ICU-specific cardiac measurement: CVP, Arterial BP,
(7) Level of conscious?
(8) Physical: Bowel sounds, lung sounds (LLL lung sounds, LUL lung sounds)
(9) Stool guiac positive and negative
(10) Pain
(11) Code???? (DNR is there but..)

# By System

(1) Neuro: GCS. Conscious? On sededation? SOFA-Neuro
(2) Cardio: BP (see how there are dealing with BP here!), Central line. Pressor
(3) Pulmo: Vent parameters (Peak and plateau pressure. PEEP. Tidal volume. FiO2. Sat and ABG)
(4) Infectious: On ABx? Fever. WBC....
(5) Nephro: Urine output (not here). Input (not here)
(6) GI: Feeding, Feeding tube.
(7)


# Not converted at this moment

* Alarms
* Code status change
* Health care proxy-related charted events
* Declaration without values e.g.  'Skin care'
* Sputum color
* Side rails
* Support sytems.
* Overlap with labevents: e.g. WBC count. LFT
* has health care proxy?
* oral cavity visualization
* 'Circulation Adequte?'
* 'suctioned - moderate'
* Lung sounds location

# Concept not found in OHDSI concept
1. Precautions
2. Full code
3. Lung sounds location
4. Continuous positive airway pressure (CPAP) + PS? should I do both? issues of settings - setting should be able to overlap?
5. 3 different types of tidal volumes

??
* Vent type: Drager?

*/


CREATE OR REPLACE FUNCTION is_number(prm_str text) RETURNS BOOLEAN AS $$
DECLARE
  v_return BOOLEAN;
BEGIN
  IF regexp_matches(prm_str,E'^-*[[:digit:]]+\.?[[:digit:]]+$') is not null
  THEN
     v_return = TRUE;
  ELSE
    IF prm_str ='0' OR prm_str ='1' OR prm_str ='2' OR prm_str ='3' OR prm_str ='4' OR prm_str ='5'
      OR prm_str ='6' OR prm_str ='7' OR prm_str ='8' OR prm_str ='9'
		THEN v_return = TRUE;
    ELSE v_return = FALSE;
    END IF;
  END IF;
  RETURN v_return;
END
$$ LANGUAGE 'plpgsql';



-- ChartEvents to Observation


-- ChartEvents to Measurement
SELECT


  CASE
	-- Note: Valid Observation Concepts are not enforced to be from any domain.
	-- They still should be Standard Concepts, and they typically belong to the
	-- “Observation” or sometimes “Measurement” domain.
	--WHEN is_number (CAST( observation_concept_translator.target_concept_id as varchar(20))) = TRUE
	--	THEN observation_concept_translator.target_concept_id -- Uses translator table

	-- Basic Measurements
	WHEN LOWER(label) = 'admit wt' THEN 4268280 -- SNOMED Observation for 'baseline weight'
	WHEN LOWER(label) = 'admit ht' THEN 4177340 -- SNOMED Observation for 'body height measure'
	WHEN LOWER(label) = 'daily weight' THEN 40786050 -- (LOINC/Measurement for 'Weight')
	WHEN LOWER(label) ILIKE 'present weight%' THEN 40786050 -- (LOINC/Measurement for 'Weight')
	WHEN LOWER(label) ILIKE 'weight kg' THEN 40786050 -- (LOINC/Measurement for 'Weight')
	WHEN LOWER(label) = 'weight change' THEN 4268831 -- (SNOMED/Measurement for 'Weight change finding')
	--WHEN LOWER(label) = 'birthweight' THEN

	-- Clinical Scorings
	WHEN LOWER(label) ILIKE '%overall sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE '%cardiovascular sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE '%respiratory sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE '%hematologic sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE '%renal sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE '%neurologic sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE '%hepatic sofa%' THEN 0 -- There is no concept code for SOFA
	WHEN LOWER(label) ILIKE 'RSBI%' THEN 0 -- THere is no concept code for 'rapid shallow breathing index'
	WHEN LOWER(label) ILIKE 'calculated saps%' THEN 45434748

	-- Clinical Assessment (Should be moved to observation)
	WHEN LOWER(label) = 'orientation' THEN 4183166 -- SNOMED Observation for 'Orientation'
	WHEN LOWER(label) = 'pupil size r/l' THEN 4062823 -- SNOMED Condition for 'O/E - pupil size'

	-- GCS
	WHEN LOWER(label) = 'gcs total' THEN 40623633 -- Measurement: GCS

	-- Temperature
	WHEN LOWER(label) ilike 'temperature c%' THEN 40786332 -- LOINC/Temperature, F is calculated so no need for migration. the site is unspecified
	WHEN LOWER(label) = 'temp. site' AND LOWER(value1) = 'blood' THEN 3007416 -- LOINC/Measurement: 'Body temperature - Intravascular'
	WHEN LOWER(label) = 'temp. site' AND LOWER(value1) = 'oral' THEN 3006322
	WHEN LOWER(label) = 'temp. site' AND LOWER(value1) = 'axillary' THEN 3025085
	WHEN LOWER(label) = 'temp. site' AND LOWER(value1) = 'rectal' THEN 3022060
	WHEN LOWER(label) = 'inspired gas temperature' THEN 4353948

	-- BP
	WHEN LOWER(label) IN ( 'arterial bp mean' , 'radial map') THEN 4108290
	WHEN LOWER(label) = 'arterial bp' THEN 4302410
	WHEN LOWER(label) = 'nbp' THEN 4326744
	WHEN LOWER(label) = 'nbp mean' THEN 4108289

	-- Heart Rate
	WHEN LOWER(label) = 'heart rate' THEN 3027018 -- LOINC Code for HR

	-- Respiratory Rate
	WHEN LOWER(label) = 'resp rate' or LOWER(label) = 'respiratory rate' or LOWER(label) = 'resp rate (total)'  THEN 3024171 -- LOINC Code for Resp Rate
	WHEN LOWER(label) = 'resp rate (spont)' OR LOWER(label) = 'spont resp rate' THEN 4154772 -- SNOMED code for 'Rate of spontaneous respiratorion'

	-- Oxygen saturation
	WHEN LOWER(label) = 'spo2' THEN 40762499
	WHEN LOWER(label) = 'cao2' THEN 40772930 -- LOINC/Measurement - Oxygen Content

	-- Cardic monitoring

	WHEN LOWER(label) = 'cardiac index' THEN 4208254 --- SNOMED Code for Cardiac Index (Observation)
	WHEN LOWER(label) ILIKE 'c.o.%' THEN 3005555 --- LOINC Code for LV Cardiac Output (Measurement)

	WHEN LOWER(label) = 'heart rhythm' THEN 40630178 --- SNOMED Code for Cardiac Rhythm [Observable Entity]
	WHEN LOWER(label) = 'respiratory rate' THEN  86290005 ---
	WHEN LOWER(label) = 'precaution' AND LOWER(value1) = 'contact' THEN 000000 --'contact precaution'
	WHEN LOWER(label) = 'arterial bp' or LOWER(label) = 'arterial bp mean' THEN 4108290
	WHEN LOWER(label) = 'temperature f' THEN 4022230

	WHEN LOWER(label) = 'pap mean' THEN 4353611 -- SNOMED Observation for Pulmonary artery pressure
	WHEN LOWER(label) = 'pap s/d' THEN 4353855 -- SNOMED Observation for Pulmonary artery systolic pressure
	WHEN LOWER(label) = 'swan svo2' THEN 0
        WHEN LOWER(label) = 'svi' THEN 0
        WHEN LOWER(label) = 'svri' THEN 0
        WHEN LOWER(label) = 'stroke volume' THEN 0

        WHEN LOWER(label) = 'swan svo2' THEN 4096100 -- SNOMED Measurement for 'Mixed venous oxygen saturation measurement'

        -- IABP-related

        WHEN LOWER(label) = 'IABP setting' THEN 0
        WHEN LOWER(label) = 'BAEDP' THEN 0 -- Balloon Aortic End Diastolic Pressure

	-- Vent setting

	-- VENT / PEEP-related
	WHEN LOWER(label) = 'peep set' or LOWER(label) = 'peep' THEN 4216746 -- SNOMED Clinical observation for 'Positive end expiratory pressure setting'
	WHEN LOWER(label) = 'auto-peep level'  THEN 0 -- Concept not available
	WHEN LOWER(label) ILIKE 'total peep%' or LOWER(label) = 'measured peep'THEN 4353713 -- SNOMED Clinical observation for 'Positive end expiratory pressure'

	-- VENT / Tidal volume
	WHEN LOWER(label) IN ('spont. tidal volume', 'tidal volume (spont)', 'spont tidal volumes'
	 ,'spon. vt (l) (mech.)') THEN 4108448 -- SNOMED Clinical observation for 'spontaneous tidal volume'
	WHEN LOWER(label) = 'tidal volume (obser)' THEN 4108137 -- SNOMED Clinical observation for 'ventilator delivered tidal volume'
	WHEN LOWER(label) = 'tidal volume' or LOWER(label) = 'tidal volume (set)' THEN 4220163 -- SNOMED Clinical observation for 'tidal volume setting'

	-- VENT / Respiratory rate set
	WHEN LOWER(label) = 'respiratory rate set' THEN 4108138 -- SNOMED Observation 'Ventilator rate'

	-- VENT / FiO2
	WHEN LOWER(label) IN ('fio2', 'fio2 [meas]', 'fio2 set', 'fio2 (analyzed)', 'vision fio2') THEN 4353936
	WHEN LOWER(label) ILIKE 'o2 flow%' THEN 3005629

	-- VENT / Other vent monitoring parameters
	WHEN LOWER(label) IN ('mean airway pressure') THEN 44782824
	WHEN LOWER(label) IN ('peak insp. pressure') THEN 4139633
	WHEN LOWER(label) IN ('plateau pressure') THEN 44782825
	WHEN LOWER(label) ILIKE 'pressure support' THEN 3000461
	WHEN LOWER(label) IN ('compliance (40-60ml)') THEN 4090322 -- 'Static lung compliance'
	WHEN LOWER(label) IN ('o2 delivery device') THEN 4036936
	WHEN LOWER(label) IN ('i:e ratio') THEN 4084278

	-- Other resp
	WHEN LOWER(label) IN ('hourly pfr') THEN 4197461

	-- Feeding
	WHEN LOWER(label) IN ('diet type') THEN 4043372 --- "Feeding"/Observation/SNOMED

-- 'lvad flow lpm''

	-- Other circulation-related monitoring
	WHEN LOWER(label) = 'cvp' THEN 4323687

	-- Neuro parameters
	WHEN LOWER(Label) = 'icp' THEN 4353953
	WHEN LOWER(label) = 'ccp' THEN 4353710 -- Cerebral perfusion pressure

	-- Other
	WHEN LOWER(label) = 'bladder pressure' THEN 4090339
	WHEN LOWER(label) = 'abi (r)' THEN 44805247
	WHEN LOWER(label) = 'abi (l)' THEN 44805248

	ELSE 0

  END as observation_concept_id,
  CASE
	WHEN LOWER(label) = 'pupil size r/l' THEN CAST ( substring(value1 FROM '[0-9]+') as INTEGER ) -- 2mm --> 2
	ELSE chartevents.value1num
  END as value_number,
  CASE
	WHEN is_number(value1) != TRUE THEN chartevents.value1
	WHEN LOWER(label) = 'iabp setting' THEN chartevents.value1
	WHEN LOWER(label) = 'pap s/d' THEN CONCAT( value1, '/', value2) -- Pulmonary artery systolic/diastolic pressure
	ELSE NULL
  END as value_str,

  CASE
	-- Clinical assessment
	WHEN LOWER(value1) = 'pinpoint' THEN 4061876 -- SNOMED Condition: 'O/E - pinpoint pupils'
	WHEN LOWER(value1) = 'fully dilated' THEN 4290615 -- SNOMED Clinical finding: 'Dilatated pupil'
	-- O2 Delivery Methods
	WHEN LOWER(value1) = 'none' THEN 45881798 -- LOINC Meas Value: "Room Air"
	WHEN LOWER(value1) = 'face tent' THEN 4138487 -- SNOMED Device: "Face tent oxygen delivery device"
	WHEN LOWER(Value1) = 't-piece' THEN 4188570 -- SNOMED Device: "T-piece without bag"
	WHEN LOWER(value1) = 'nasal cannula' THEN 4224038 -- SNOMED Device: "oxygen Nasal cannula"
	WHEN LOWER(value1) = 'non-rebreather' THEN 4145528
	WHEN LOWER(value1) = 'aerosol-cool' THEN 4145694 -- SNOMED Device: "aerosol oxygen mask"
	WHEN LOWER(value1) = 'ventilator' THEN 40493026 -- SNOMED Device: "mechanical ventilator"
	WHEN LOWER(value1) = 'trach mask' THEN 45760219
	WHEN LOWER(value1) = 'venti mask' THEN 4322904 -- SNOMED Device: "venturi mask"
	WHEN LOWER(value1) = 'bipap mask' THEN 45767334 -- SNOMED Device: "Bipap face mask, single use"
	WHEN LOWER(value1) = 'hi flow neb' THEN 4139525 -- SNOMED Device: "high flow oxygen nasal cannula"
	--WHEN LOWER(value1) = ''

	-- Cardiac monitoring
	WHEN LOWER(value1) = 'sinus tachy' THEN 4007310
	WHEN LOWER(value1) = 'atrial fib' THEN 313217
	WHEN LOWER(value1) = 'sinus brady' THEN 4171683 -- SNOMED Condition for Sinus bradycardia
	WHEN LOWER(value1) = 'normal sinus' THEN 4276669 -- SNOMED Condition for Normal sinus
	WHEN LOWER(value1) = '1st deg av block' THEN 314379 -- SNOMED Condition for 'First degree atrioventricular block'
	WHEN LOWER(value1) = '2nd deg av block' THEN 318448 -- SNOMED Condition for 'second degree atrioventricular block'
	WHEN LOWER(value1) = '2nd avb/mobitz i' THEN 4205137
	WHEN LOWER(value1) = '2nd avb/mobitz ii' THEN 313780
	WHEN LOWER(value1) = 'comp heart block' THEN 40288216
	WHEN LOWER(value1) = 'av paced' THEN 4088998 -- SNOMED Measurement for 'AV sequential pacing pattern'
	WHEN LOWER(value1) = 'a paced' THEN 4089488 -- SNOMED Measurement for 'Atrial pacing pattern'
	WHEN LOWER(value1) = 'v paced' THEN 4092038 -- SNOMED Measurement for 'ventricular pacing pattern'
	WHEN LOWER(value1) = 'atrial flutter' THEN 314665
	WHEN LOWER(value1) = 'junctional' THEN 4038688 -- SNOMED Condition for 'junctional rhythm'
	WHEN LOWER(value1) = 'multfocalatrtach' THEN 0
	WHEN LOWER(value1) = 'parox atrial tach' THEN 0
	WHEN LOWER(value1) = 'supravent tachy' THEN 4275423
	WHEN LOWER(value1) = 'vent. tachy' THEN 4275423
	WHEN LOWER(value1) = 'asystole' THEN 4216773
	WHEN LOWER(stopped) = 'd/c''d' THEN 4132627 -- SNOMED Observation for 'Discontinued' (Mostly for mechanical vent)
	WHEN LOWER(value1) = 'tube feeding' THEN 4222605 -- SNOMED Observation / Tube feeding diet
	WHEN LOWER(value1) = 'diabetic' THEN 4052041 -- SNOMED Observation / Diabetic diet
	WHEN LOWER(value1) = 'full liquid' THEN 4033731 -- SNOMED Obsevation / Liquid diet
	WHEN LOWER(value1) = 'clear liquid' THEN 4033731 -- SNOMED Obsevation / Liquid diet (not diferrentiated from full liquid)
	WHEN LOWER(value1) = 'npo' THEN 4033731 -- SNOMED Observation / 'nothing by mouth status'
	WHEN LOWER(value1) = 'tpn' THEN 45881254 -- LOINC Meas Value / 'TPN'
	WHEN LOWER(value1) = 'renal' THEN 0 -- renal diet
	WHEN LOWER(value1) ILIKE '%low cholest' THEN 4215995 -- SNOMED Clinica Obs: Low cholesterol diet
	WHEN LOWER(value1) = 'soft solid' THEN 4301609 -- SNOMED Clinica Obs: Soft diet
	ELSE NULL
  END as value_concept_id,

  --value_concept_translator.target_concept_id as value_concept_id,
  CAST ( charttime AS DATE),
  CAST ( chartevents.charttime AS TIME),
  --chartevents.value1num as source_value,

  CASE
	--WHEN is_number (CAST( unit_concept_translator.target_concept_id as varchar(20))) = TRUE
	--	THEN unit_concept_translator.target_concept_id
	WHEN LOWER(value1uom) = 'mmhg' THEN 8876
	WHEN LOWER(value1uom) = 'deg. f' THEN 9289
	WHEN LOWER(value1uom) = 'deg. c' THEN 8653
	WHEN LOWER(value1uom) = 'l/min' THEN 8698
	WHEN LOWER(value1uom) = 'kg' THEN 9529
	WHEN LOWER(value1uom) = 'bpm' THEN 8541 -- UCUM per minute
	WHEN LOWER(value1uom) = '%' THEN 8554
	WHEN LOWER(value1uom) = 'cmh2o' THEN 44777590
	WHEN LOWER(value1uom) = 'ml/b' THEN 8587 -- UCUM unit for 'milliliter' (there is no unit avilable for ml per breath but it doesnt really matter...)
	WHEN LOWER(value1uom) = 'torr' THEN 4136788
	WHEN LOWER(label) = 'pupil size r/l' THEN 8588 -- Millimeter
	ELSE 0
  END as unit_concept_id,

  --chartevents.value1uom as unit_source_value,

 -- chartevents.elemid,

  chartevents.value1,
  chartevents.value2,
 /* chartevents.value2num,*/
  chartevents.value1uom,

 /* chartevents.stopped, */
  d_chartitems.label,
  d_chartitems.category,
  d_chartitems.description,
  chartevents.resultstatus
 -- value_concept_translator.target_concept_id as value_translated_id
FROM
  mimic2v26.chartevents
 -- mimic2v26.d_chartitems
INNER JOIN mimic2v26.d_chartitems on d_chartitems.itemid = chartevents.itemid

WHERE

  COALESCE(d_chartitems.category, '') NOT ILIKE '%ABG%' AND
  COALESCE(d_chartitems.category, '') NOT ILIKE '%VBG%' AND
  COALESCE(d_chartitems.category, '') != 'Chemistry' AND COALESCE(d_chartitems.category, '') != 'Coags' AND
  COALESCE(d_chartitems.category, '') != 'Hematology' AND COALESCE(d_chartitems.category, '') != 'Enzymes' AND
  COALESCE(d_chartitems.category, '') NOT ILIKE '%Gases%' AND
  COALESCE(d_chartitems.category, '') != 'Heme/Coag' AND COALESCE(LOWER(d_chartitems.category), '') != 'drug level' AND COALESCE(LOWER(d_chartitems.category), '') != 'csf' AND
  COALESCE(d_chartitems.category, '') != 'Urine' AND
  LOWER(d_chartitems.label) NOT IN ( 'skin care', 'turn', 'pressurereducedevice', 'therapeutic bed', 'calprevflg' , 'inv#3 dsg change', 'risk for falls', 'bath', 'assistance device', 'back care', 'activity tolerance',
  'pressure sore odor#1', 'reason for restraint', 'tach care', 'side rails', 'trach size', 'tracheostomy cuff' ) AND
  LOWER(d_chartitems.label) NOT ILIKE '%alarm%' AND
  LOWER(d_chartitems.label) NOT ILIKE '%#1%' AND
  LOWER(d_chartitems.label) NOT ILIKE '%#2%' AND LOWER(d_chartitems.label) NOT ILIKE '%#3%' AND
  LOWER(d_chartitems.label) NOT ILIKE '%systolic unloading%' and
  LOWER(d_chartitems.label) NOT ILIKE '%eye care%' and
  LOWER(d_chartitems.label) NOT ILIKE '%behavior%' and
  LOWER(d_chartitems.label) NOT ILIKE '%INV%'and
  LOWER(d_chartitems.label) NOT ILIKE '%antiembdevice%' and
  LOWER(d_chartitems.label) NOT ILIKE '%behavior%' and
  LOWER(d_chartitems.label) NOT ILIKE '%trach%'and
  LOWER(d_chartitems.label) NOT ILIKE '%activity%'
  and
  LOWER(d_chartitems.label) NOT ILIKE '%precautions%' and
  LOWER(d_chartitems.label) NOT ILIKE '%code status%'
  and
  LOWER(d_chartitems.label) NOT ILIKE '%lung sounds%'

  and LOWER(d_chartitems.label) NOT ILIKE '%alarm%'

  and LOWER(d_chartitems.label) NOT ILIKE '%dialysis%'

  and LOWER(d_chartitems.label) NOT ILIKE '%impskin%'

  and LOWER(d_chartitems.label) NOT ILIKE '%impaired skin%'
  and LOWER(d_chartitems.label) NOT ILIKE '%movement%'
  and LOWER(d_chartitems.label) NOT ILIKE '%braden%'
  and LOWER(d_chartitems.label) NOT ILIKE '%iv site appear%'
  and LOWER(d_chartitems.label) NOT ILIKE '%temp/color%'
  and LOWER(d_chartitems.label) NOT ILIKE '%site/size%'
  and LOWER(d_chartitems.label) NOT ILIKE '%dialysate%' -- note: dialysis is not covered for now

  --and lower(label) ILIKE '%heart rhythm%'

  and lower(d_chartitems.label) NOT IN ('arterial bp mean', 'eye opening', 'temperature c (calc)', 'verbal response',
  'education response', 'posttib. pulses r/l', 'skin temp/condition', 'skin integrity', 'inspired gas temp', 'oral care'
  ,'bowel sounds', 'apnea time interval', 'health care proxy', 'oral cavity', 'removed x 5 mins'
  , 'restraint location', 'restraint type', 'support systems', 'riker-sas scale', 'stool management'
  , 'range of motion', 'current goal', 'skin color', 'pain present', 'cuff leak', 'rsbi (<100)', 'position'
  , 'hob', 'respiratory pattern' ,'religion', 'bsa', 'spontaneous movement', 'follows commands', 'ectopy frequency'
  , 'airway size', 'daily wake up' ,'cough reflex', 'plateau-off', 'speech', 'education readiness', 'ventilator mode',
  'gu catheter size', 'airway type', 'gi prophylaxis', 'sensitivity-vent','urine source', 'pain level (rest)', 'cough effort', 've high'
  , 'bsa - metric', 'waveform-vent', 'less restrict meas.', 'tank b psi.', 'restraints evaluated', 'previous weightf', 'tank a psi.'
  ,'pacemaker type', 'education method', 'pain type', 'ett mark/location', 'education learner', 'rue temp/color', 'ectopy type'
  , 'bsa - english', 'communication', 'pacer wires atrial', 'ventilator no.', 'flow-by sensitivity',
  'low exhaled min vol', 'flow-by (lpm)', 'ventilator type', 'abdominal assessment', 'neuro symptoms', 'education handout',
  'readmission', 'pain assess method', 'pacer wire condition','circulation/skinint', 'pain location', 'high resp. rate',
   'minute volume(obser)' , 'neuro drain lev/loc', 'neuro drain type', 'neuro drain status', 'neuro drain drainge',
   'radiologic study', 'high exhaled min vol', 'augmented diastole', 'assisted systole', 'resopnds to stimuli',
   'cervical collar type', 'pupil response r/l', 'family communication', 'suctioned', 'position change', 'sputum source/amt'
   , 'pain level' , 'education barrier', 'pa line cm mark', 'incentive spirometry', 'parameters checked'
   , 'martial status', 'previous weight', 'motor response', 'responds to stimuli', 'level of conscious'
   , 'pain management', 'high min. vol' , 'significant events', 'nursing consultation', 'return pressure mmhg',
   'marital status')
  --and LOWER(d_chartitems.label) ILIKE '%sofa%'

  --and random() < 0.01
  and random () < 0.01
  --and is_number ( value_concept_id ) = FALSE

LIMIT 200


-- Conversion Target Necessary / Included:
-- Conversion Target Necessary but with issues:
-- Conversion Target Not Included


-- D_ITEMS is sourced from two distinct ICU databases. The main consequence is that there are duplicate ITEMID for each concept. For example, heart rate is captured both as an ITEMID of 212 (CareVue) and as an ITEMID of 220045 (Metavision). As a result, it is necessary to search for multiple ITEMID to capture a single concept across the entire database. This can be tedious, and it is an active project to coalesce these ITEMID - one which welcomes any and all help provided by the community!




-- Death

truncate table ohdsi.death;
INSERT into ohdsi.death(person_id, death_date, death_type_concept_id, cause_concept_id, cause_source_concept_id)
SELECT subject_id, CAST(dod as DATE), 0, 0, 0
FROM mimic2v26.d_patients
WHERE hospital_expire_flg = 'Y'


-- Labs to Measurement

truncate table ohdsi.measurement;
INSERT INTO ohdsi.measurement (measurement_id, person_id, measurement_concept_id, measurement_date, measurement_time, measurement_type_concept_id,
	operator_concept_id, value_as_number, value_as_concept_id, unit_concept_id, provider_id, visit_occurrence_id, measurement_source_value, measurement_source_concept_id,
	unit_source_value, value_source_value)
SELECT
   0 as measurement_id, --
   mimic2v26.labevents.subject_id as person_id, --
   CASE
	WHEN is_number( CAST(main_concept.concept_id AS TEXT) ) = TRUE THEN main_concept.concept_id
	WHEN lower(d_labitems.test_name) = 'bands' THEN 40782560
	WHEN lower(d_labitems.test_name) = 'hct' THEN 3009542
	WHEN lower(d_labitems.test_name) = 'cd34' THEN 44817307
	WHEN lower(d_labitems.test_name) = 'tacrofk' THEN 4310327
	WHEN lower(d_labitems.test_name) = 'intubated' THEN 4158191
	WHEN lower(d_labitems.test_name) = 'crp' THEN 45888376
	ELSE 0
   END as measurement_concept_id, --
   CAST( labevents.charttime as DATE ) as measurement_date, --
   CAST( labevents.charttime as TIME ) as measurement_time, --
   CASE
      WHEN is_number(CAST(labevents.icustay_id AS TEXT)) = TRUE THEN 45877824  -- It mean that it was measured in the ICU
      ELSE 0 -- could be anything else
   END as measurement_type_concept_id, --
   CASE

	WHEN labevents.value ILIKE '%/%' THEN 000000 -- ????
	WHEN labevents.value ILIKE '%-%' THEN 000000 -- Range
	WHEN labevents.value ILIKE '%<=%' THEN 4171754 -- SNOMED Meas Value Operator (<=)
	WHEN labevents.value ILIKE '%<%' or LOWER(labevents.value) ILIKE '%less than%' THEN 4171756 -- SNOMED Meas Value Operator (<)
	WHEN labevents.value ILIKE '%>=%' THEN 4171755 -- SNOMED Meas Value Operator (>=)
	WHEN labevents.value ILIKE '%>%' or LOWER(labevents.value) ILIKE '%greater than%' THEN 4172704 -- SNOMED Meas Value Operator (>)
	ELSE 0
   END as operater_concept_id, --
   CASE
	WHEN labevents.value ILIKE '%/%' THEN CAST ( substring(labevents.value FROM '[0-9]+') as FLOAT ) -- ????
	WHEN labevents.value ILIKE '%-%' THEN CAST ( substring(labevents.value FROM '[0-9]+') as FLOAT )
	WHEN labevents.value ILIKE '%<%' or LOWER(labevents.value) ILIKE '%less than%'
		OR labevents.value ILIKE '%>%' or LOWER(labevents.value) ILIKE '%greater than%'
		OR  LOWER(labevents.value) ILIKE '%-%'
		THEN CAST ( substring(labevents.value FROM '[0-9]+') as FLOAT )
	WHEN is_number ( labevents.value ) = TRUE THEN CAST ( labevents.value as FLOAT )
	ELSE 0
   END as value_as_number, --
   CASE
	WHEN LOWER(labevents.value) = 'neg' or LOWER(labevents.value) = 'negative' THEN 9189 -- SNOMED Measurement value: Negative
	WHEN LOWER(labevents.value) = 'pos' or LOWER(labevents.value) = 'positive' THEN 9191 -- SNOMED Measurement value: Negative
	WHEN LOWER(labevents.value) = 'borderline' THEN 4162852 -- SNOMED Measurement value: boderline
	WHEN LOWER(labevents.value) = 'low' THEN 45881258
	WHEN LOWER(labevents.value) = 'high' THEN 45880619
	WHEN LOWER(labevents.value) = 'normal' THEN 45884153
	WHEN LOWER(labevents.value) = 'intubated' THEN 45884415
	WHEN LOWER(labevents.value) = 'not intubated' THEN 4134640
	ELSE '0'
   END as value_as_concept_id, --
     CASE
      --  WHEN unit_concept.concept_id != NULL THEN unit_concept.concept_id
        -- Many units can be found in concept table
	WHEN LOWER(labevents.valueuom) = 'mm hg' OR LOWER(labevents.valueuom) = 'mmhg'
		OR d_labitems.loinc_code = '19991-9' THEN 8876 -- UCUM Code for millimeter mercury column
	WHEN LOWER(labevents.valueuom) = 'meq/l' THEN 9557
	WHEN labevents.valueuom = '%' THEN 8554
	WHEN LOWER(labevents.valueuom) = 'meq/l' THEN 9557
	WHEN LOWER(labevents.valueuom) = 'mg/dl' THEN 8840
	WHEN LOWER(labevents.valueuom) = 'g/dl' THEN 8713
	WHEN LOWER(labevents.valueuom) = 'mmol/l' THEN 8753
	WHEN LOWER(labevents.valueuom) = 'l/min' THEN 8698
	WHEN d_labitems.loinc_code ='11558-4' OR d_labitems.loinc_code ='2748-2' THEN 8482  -- 11558-4 is LOINC code for pH. 8482 if UCUM code for pH
	WHEN LOWER(labevents.valueuom) = 'iu/l' THEN 8923
	WHEN LOWER(labevents.valueuom) = 'ug/ml' THEN 8859
	WHEN LOWER(labevents.valueuom) = 'ng/ml' THEN 8842
	WHEN LOWER(labevents.valueuom) = 'umol/l' THEN 8749
	WHEN LOWER(labevents.valueuom) = 'iu/ml' THEN 8985
	WHEN LOWER(labevents.valueuom) = 'u/ml' THEN 8763
	WHEN LOWER(labevents.valueuom) = 'ratio' THEN 8523
	WHEN LOWER(labevents.valueuom) = 'ug/dl' THEN 8837
	WHEN LOWER(labevents.valueuom) = 'pg/ml' THEN 8845
	WHEN LOWER(labevents.valueuom) = 'miu/l' THEN 9040
	WHEN LOWER(labevents.valueuom) = 'miu/ml' THEN 9550
	WHEN LOWER(labevents.valueuom) = 'units' THEN 8510
	WHEN LOWER(labevents.valueuom) = 'uiu/l' THEN 44777583
	WHEN LOWER(labevents.valueuom) = 'uiu/ml' THEN 9093
	WHEN LOWER(labevents.valueuom) = 'uu/ml' THEN 9093 -- uIU/mL
	WHEN LOWER(labevents.valueuom) = 'mg/24hr' THEN 8909
	WHEN LOWER(labevents.valueuom) = 'u/l' THEN 8645
	WHEN LOWER(labevents.valueuom) = 'ml/min' THEN 8795
	WHEN LOWER(labevents.valueuom) = '#/cu mm' THEN 8785 -- per cubic millimeter [for WBC or RBC in peritoneal fluid]
	WHEN LOWER(labevents.valueuom) = '#/uL' THEN 8647
	WHEN LOWER(labevents.valueuom) = 'gpl' THEN 4171221
	WHEN LOWER(labevents.valueuom) = 'score' and d_labitems.loinc_code = '15112-6' THEN 4196800 -- SNOMED code for Leukocyte alkaline phosphatase score (class: procedure)
	WHEN LOWER(labevents.valueuom) = '/mm3' THEN 8785
	WHEN LOWER(labevents.valueuom) = 'sec' OR LOWER(labevents.valueuom) = 'seconds' THEN 8555
	WHEN LOWER(labevents.valueuom) = 'serum vis' THEN 3010493 -- LOINC code for Viscosity of Serum
	WHEN LOWER(labevents.valueuom) = 'eu/dl' THEN 8829
	WHEN LOWER(labevents.valueuom) = 'mm/hr' THEN 8752
	ELSE 0
   END as unit_concept_id, --
   0 as provider_id,  --
   CASE
	WHEN is_number(CAST(labevents.icustay_id AS TEXT)) = TRUE THEN labevents.icustay_id + 1000000 -- Note that some patients does not have ICU visit ID as the values are for floor/PCU or whatever. In this case, hospital admission id is used instead but 1,000,000 is added to ICU idea to prevent overlap of id
	ELSE labevents.hadm_id
   END as visit_occurence_id, --
   CONCAT( d_labitems.test_name, ' / ' , mimic2v26.d_labitems.loinc_code, ' (', 'LOINC CODE', ')') as measurement_source_value, --
   0 as measurement_source_concept_id, --
   labevents.valueuom as unit_source_value, --
   labevents.value  as value_source_value --

FROM
  mimic2v26.labevents
  INNER JOIN mimic2v26.d_labitems ON d_labitems.itemid = labevents.itemid
  LEFT JOIN ohdsi.concept as main_concept ON main_concept.concept_code = mimic2v26.d_labitems.loinc_code
 -- LEFT JOIN ohdsi.concept as unit_concept on LOWER(unit_concept.concept_code) = LOWER(labevents.valueuom)
WHERE is_number(CAST(main_concept.concept_id AS TEXT)) = TRUE
/*and ( lower(d_labitems.test_name) NOT IN ('misc', 'gr hold', '<crea-p>', '<crea-u>', 'uhold','rbcf', 'other', 'birefri', 'wbcclump', 'envelop', 'epi', 'inh scr'
	, 'ipt', 'cd20', 'cd16', 'cd71', 'fmc-7' ,'young',  'type', 'vent', 'edta hold', 'green hld', 'bc hold', 'ltgrn hld', '')
 AND lower(d_labitems.test_name) NOT IN ('bands', 'hct', 'cd34', 'tacrofk', 'intubated', 'unkcast', 'location', 'number', 'shape', 'rates', 'req o2', 'art', 'ven', 'crp') )   and
 lower(labevents.value) != 'done'*/
--WHERE mimic2v26.labevents.subject_id = 1371




-- Failed to catch: MPL (IgM somewhat unit...). U/g/hb (for 32546-4) 1977-8: SM, LG, MOD (for urine bilirubin)