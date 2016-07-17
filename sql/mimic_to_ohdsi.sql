﻿
﻿CREATE OR REPLACE FUNCTION is_number(prm_str text) RETURNS BOOLEAN AS $$
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

﻿
truncate table ohdsi.person;

INSERT INTO ohdsi.person(person_id, gender_concept_id, year_of_birth, month_of_birth,day_of_birth,race_concept_id, ethnicity_concept_id, gender_source_value)
SELECT subject_id,
 CASE
   when gender = 'M' then 8507  -- It was sex in MIMIC2 --> changed into gender (to make more politically correct? :)
   when gender = 'F' then 8532
   else 8851
 END as gender_concept_id, extract (year from dob),extract (month from dob), extract (day from dob),
0,0, gender
FROM mimiciii.patients
WHERE patients.subject_id > 82000 -- for testing


﻿
-- Procedureevents_mv -> procedure_occurrence
-- Only blood culture and lines for now

-- Procedure Properties into PROPERTY TABLE (NOTE: OHDSI Extension)

truncate ohdsi.device_exposure;
INSERT INTO ohdsi.device_exposure ( person_id, device_concept_id, device_exposure_start_date, device_exposure_end_date, device_type_concept_id, visit_occurrence_id
	, device_source_value, device_source_concept_id, device_exposure_start_time, device_exposure_end_time)
SELECT
	temp.subject_id,
	temp.procedure_concept_id,
	CAST(temp.starttime as DATE) as device_exposure_start_date,
	CAST(temp.endtime as DATE) as device_exposure_end_date,
	CASE
		WHEN lower(temp.locationcategory) = 'invasive arterial' AND lower(temp.location) ILIKE '%brachial%' THEN 4063510
		WHEN lower(temp.locationcategory) = 'invasive arterial' AND lower(temp.location) ILIKE '%femoral%' THEN 40518500 -- "Femoral Artery"
		WHEN lower(temp.locationcategory) = 'invasive arterial' AND lower(temp.location) IN ('right radial', 'left radial') THEN 44517235 -- "Radial Artery"
		WHEN lower(temp.locationcategory) = 'invasive venous' AND lower(temp.location) IN ('left subclavian', 'right subclavian') THEN 4311330 -- "Subclavian Vein"
		WHEN lower(temp.locationcategory) = 'invasive venous' AND lower(temp.location) IN ('right ij', 'left ij') THEN 4006845 -- "Internal jugular vein"
		WHEN lower(temp.locationcategory) = 'invasive venous' AND lower(temp.location) ILIKE '%femoral%' THEN 4052416 -- femoral vein
		WHEN lower(temp.label) IN ('picc line', 'midline') and lower(temp.location) ILIKE '%upper arm%' THEN 44791574 ---'structure of vein / anterior upper arm'
		WHEN lower(temp.label) IN ('picc line', 'midline') and lower(temp.location) ILIKE '%antecube%' THEN 4029825
		WHEN lower(temp.label) IN ('picc line', 'midline') and lower(temp.location) ILIKE '%brachial%' THEN 4029825

		ELSE 0
	END as anatomic_location,
	temp.hadm_id as visit_occurrence_id,
	temp.label as device_source_value,
	temp.item_id as device_source_concept_id,
	CAST(temp.starttime as TIME) as device_exposure_start_time,
	CAST(temp.endtime as TIME) as device_exposure_end_time

FROM

(SELECT procedureevents_mv.row_id as procedure_id,
   CASE

	-- Intubation/Extubation
	   WHEN lower(label) in ('invasive ventilation') THEN 4202832 --'intubation'

	-- arterial line
	   WHEN lower(label) in ('arterial line') THEN 4213288

	-- dialysis catheter
	   WHEN lower(label) in ('dialysis catheter') THEN 4265605 -- Device: Dialysis catheter

	-- Intraaortic balloon pump placement
           WHEN lower(label) ilike '%iabp line%' THEN 40485320 -- Insertion of intraaortic balloon pump via femoral artery

	-- PA Catheter
	   WHEN lower(label) = 'pa catheter' THEN 40461159 -- Procedure: SWAN-GANZ Catheterization

	-- central venous line (Hickman catheter, Multi-Lumen Catheter, Trauma Line)
	   WHEN lower(locationcategory) in ('invasive venous') and location ilike '%IJ%' THEN 4234953 -- Catheterization of internal jugular vein
	   WHEN lower(locationcategory) in ('invasive venous') and lower(location) ilike '%subclavian%' THEN 4052415 -- Catheterization of subclavian vein
	   WHEN lower(locationcategory) in ('invasive venous') and lower(location) ilike '%femoral%' THEN 4052416 -- Catheterization of femoral vein
	   WHEN lower(label) = 'multi lumen' and lower(category) ilike '%invasive%'   THEN 4052413 -- Central venous line, unspecified

	-- PICC line
	   WHEN lower(label) in ('picc line') THEN 4322380

	-- Peripheral line
	   WHEN lower(ordercategoryname) = 'peripheral lines' THEN 4049832

	-- Line Removal: Venous
	   WHEN lower(locationcategory) = 'invasive venous' and lower(label) ilike '%line/catheter removal%' THEN 4022792 -- SNOMED: Removal of central venous line
	   WHEN lower(locationcategory) = 'invasive arterial' and lower(label) ilike '%line/catheter removal%' THEN -1

	-- Pacemaker
	   WHEN lower(label) = 'temporary pacemaker wires inserted' THEN 2313790
	   ELSE NULL

	END as procedure_concept_id, procedureevents_mv.itemid as item_id,
	CASE
		WHEN (location IS NULL) or location = '' THEN ''
		ELSE '/'
	END as slash_if_location, d_items.itemid, *
 from mimiciii.procedureevents_mv,
	mimiciii.d_items
WHERE procedureevents_mv.itemid = d_items.itemid) as temp
WHERE
	temp.procedure_concept_id IS NOT NULL and temp.subject_id > 82000
	AND temp.procedure_concept_id IS NOT NULL -- ( 4213288, 4322380, 4234953, 4052415, 4052416 )



/*
INSERT INTO extension.property ( domain_concept_id, target_id, location_concept_id, starttime, endtime, duration )
SELECT
	4040551 as domain_concept_id, -- 'Procedure on blood vessel'

	pro.row_id as target_id, -- Target procedure (invasive lines)
	CASE
		WHEN lower(pro.locationcategory) = 'invasive arterial' AND lower(pro.location) ILIKE '%brachial%' THEN 4063510
		WHEN lower(pro.locationcategory) = 'invasive arterial' AND lower(pro.location) ILIKE '%femoral%' THEN 40518500 -- "Femoral Artery"
		WHEN lower(pro.locationcategory) = 'invasive arterial' AND lower(pro.location) IN ('right radial', 'left radial') THEN 44517235 -- "Radial Artery"
		WHEN lower(pro.locationcategory) = 'invasive venous' AND lower(pro.location) IN ('left subclavian', 'right subclavian') THEN 4311330 -- "Subclavian Vein"
		WHEN lower(pro.locationcategory) = 'invasive venous' AND lower(pro.location) IN ('right ij', 'left ij') THEN 4006845 -- "Internal jugular vein"
		WHEN lower(pro.locationcategory) = 'invasive venous' AND lower(pro.location) ILIKE '%femoral%' THEN 4052416 -- femoral vein
		WHEN lower(item.label) IN ('picc line', 'midline') and lower(pro.location) ILIKE '%upper arm%' THEN 44791574 ---'structure of vein / anterior upper arm'
		WHEN lower(item.label) IN ('picc line', 'midline') and lower(pro.location) ILIKE '%antecube%' THEN 4029825

		ELSE 0
	END as location,
	pro.starttime as starttime,
	pro.endtime as endtime,
	(pro.endtime-pro.starttime) as duration
FROM
	mimiciii.procedureevents_mv as pro,
	mimiciii.d_items as item
WHERE
	pro.itemid = item.itemid
	AND (lower(pro.locationcategory) = 'invasive venous' OR lower(locationcategory) = 'invasive arterial')
	AND subject_id > 82000

*/

truncate ohdsi.procedure_occurrence;
INSERT INTO ohdsi.procedure_occurrence(procedure_occurrence_id,procedure_concept_id,person_id,procedure_date,procedure_type_concept_id,modifier_concept_id,
visit_occurrence_id,procedure_source_value,procedure_source_concept_id, procedure_time )
SELECT
	temp.procedure_id as procedure_occurrence_id,
	temp.procedure_concept_id,
	temp.subject_id as person_id,
	CAST(starttime as date) as procedure_date,
	0 as procedure_type_concept_id,
	0 as modifier_concept_id,
	temp.hadm_id as visit_occurrence_id,
	CONCAT(temp.label , temp.slash_if_location , location) as procedure_source_value,
	temp.item_id as procedure_source_concept_id,
	CAST(starttime as time) as procedure_time
FROM
(SELECT procedureevents_mv.row_id as procedure_id,
   CASE
	-- Cultures
	   WHEN lower(label) in ('blood culture', 'blood cultured') THEN 30088009 -- SNOMED Blood Culture
	   WHEN lower(label) in ('csf culture', 'csf cultured') THEN 4098503
	   WHEN lower(label) in ('pan culture', 'pan cultured') THEN 0 --
	   WHEN lower(label) in ('urine culture', 'urine cultured') THEN 4024509
	   WHEN lower(label) in ('stool culture', 'stool cultured') THEN 4024963
	   WHEN lower(label) in ('wound culture', 'wound cultured') THEN 4296651
	   WHEN lower(label) in ('sputum culture', 'sputum cultured') THEN 40312248
	   WHEN lower(label) in ('nasal swab') THEN 40335469
	   WHEN lower(label) in ('bal fluid culture') THEN 0 -- No code for BAL fluid culture

	-- Intubation/Extubation
	   WHEN lower(label) in ('invasive ventilation') THEN 4202832 --'intubation'
	   WHEN lower(label) in ('extubation') THEN 4148972 --'extubation of trachea'

	-- arterial line
	   WHEN lower(label) in ('arterial line') THEN 4213288

	-- dialysis catheter
	   WHEN lower(label) in ('dialysis catheter') THEN 4265605 -- Device: Dialysis catheter

	-- dialysis
	   WHEN lower(label) ilike '%crrt%' THEN 37018292

	-- Intraaortic balloon pump placement
           WHEN lower(label) ilike '%iabp line%' THEN 40485320 -- Insertion of intraaortic balloon pump via femoral artery

	-- PA Catheter
	   WHEN lower(label) = 'pa catheter' THEN 40461159 -- Procedure: SWAN-GANZ Catheterization

	-- central venous line (Hickman catheter, Multi-Lumen Catheter, Trauma Line)
	   WHEN lower(locationcategory) in ('invasive venous') and location ilike '%IJ%' THEN 4234953 -- Catheterization of internal jugular vein
	   WHEN lower(locationcategory) in ('invasive venous') and lower(location) ilike '%subclavian%' THEN 4052415 -- Catheterization of subclavian vein
	   WHEN lower(locationcategory) in ('invasive venous') and lower(location) ilike '%femoral%' THEN 4052416 -- Catheterization of femoral vein
	   WHEN lower(label) = 'multi lumen' and lower(category) ilike '%invasive%'   THEN 4052413 -- Central venous line, unspecified

	-- PICC line
	   WHEN lower(label) in ('picc line') THEN 4322380

	-- Peripheral line
	   WHEN lower(ordercategoryname) = 'peripheral lines' THEN 4049832

	-- Line Removal: Venous
	   WHEN lower(locationcategory) = 'invasive venous' and lower(label) ilike '%line/catheter removal%' THEN 4022792 -- SNOMED: Removal of central venous line
	   WHEN lower(locationcategory) = 'invasive arterial' and lower(label) ilike '%line/catheter removal%' THEN -1

	-- Defibrillation
	   WHEN lower(label) = 'cardioversion/defibrillation' THEN 45890325 -- Electrical conversion of arrhythmia

	-- Pacemaker
	   WHEN lower(label) = 'temporary pacemaker wires inserted' THEN 2313790

	   --WHEN lower(temp.locationcategory) = 'invasive arterial' and lower(temp.label) ilike '%line/catheter removal%' THEN 4022792 -- SNOMED: Removal of central venous line

	END as procedure_concept_id,
	procedureevents_mv.itemid as item_id,
	CASE
		WHEN (location IS NULL) or location = '' THEN ''
		ELSE '/'
	END as slash_if_location, *
 from mimiciii.procedureevents_mv,
	mimiciii.d_items
WHERE procedureevents_mv.itemid = d_items.itemid) as temp
WHERE temp.procedure_concept_id IS NOT NULL and temp.subject_id > 82000


-- locationcategory != '' and lower(d_items.label) not in ('paracentesis removal', 'hd fluid removal', 'hd removal', 'hemodialysis removal', 'bypass removal') and lower(d_items.label) ilike '%removal%'
﻿
truncate table ohdsi.death;
INSERT into ohdsi.death(person_id, death_date, death_type_concept_id, cause_concept_id, cause_source_concept_id)
SELECT subject_id, CAST(dod as DATE), 0, 0, 0
FROM mimiciii.patients
WHERE patients.expire_flag = 1 and subject_id > 82000


truncate table ohdsi.measurement;
INSERT INTO ohdsi.measurement (measurement_id, person_id, measurement_concept_id, measurement_date, measurement_time, measurement_type_concept_id,
	operator_concept_id, value_as_number, value_as_concept_id, unit_concept_id, provider_id, visit_occurrence_id, measurement_source_value, measurement_source_concept_id,
	unit_source_value, value_source_value)
SELECT
	temp_table.measurement_id,
	temp_table.person_id,
	temp_table.concept_id as measurement_concept_id,
	temp_table.measurement_date,
	temp_table.measurement_time,
	temp_table.measurement_type_concept_id,
	temp_table.operater_concept_id,
	temp_table.value_as_number,
	temp_table.value_as_concept_id,
  CASE
	WHEN is_number ( CAST(unit_concept.concept_id AS TEXT) ) = TRUE THEN unit_concept.concept_id
	WHEN LOWER(temp_table.valueuom) = 'mm hg' OR LOWER(temp_table.valueuom) = 'mmhg'
		OR temp_table.loinc_code = '19991-9' THEN 8876 -- UCUM Code for millimeter mercury column
	WHEN LOWER(temp_table.valueuom) = 'meq/l' THEN 9557
	WHEN temp_table.valueuom = '%' THEN 8554
	WHEN LOWER(temp_table.valueuom) = 'meq/l' THEN 9557
	WHEN LOWER(temp_table.valueuom) = 'mg/dl' THEN 8840
	WHEN LOWER(temp_table.valueuom) = 'g/dl' THEN 8713
	WHEN LOWER(temp_table.valueuom) = 'mmol/l' THEN 8753
	WHEN LOWER(temp_table.valueuom) = 'l/min' THEN 8698
	WHEN temp_table.loinc_code ='11558-4' OR temp_table.loinc_code ='2748-2' THEN 8482  -- 11558-4 is LOINC code for pH. 8482 if UCUM code for pH
	WHEN LOWER(temp_table.valueuom) = 'iu/l' THEN 8923
	WHEN LOWER(temp_table.valueuom) = 'ug/ml' THEN 8859
	WHEN LOWER(temp_table.valueuom) = 'ng/ml' THEN 8842
	WHEN LOWER(temp_table.valueuom) = 'umol/l' THEN 8749
	WHEN LOWER(temp_table.valueuom) = 'iu/ml' THEN 8985
	WHEN LOWER(temp_table.valueuom) = 'u/ml' THEN 8763
	WHEN LOWER(temp_table.valueuom) = 'ratio' THEN 8523
	WHEN LOWER(temp_table.valueuom) = 'ug/dl' THEN 8837
	WHEN LOWER(temp_table.valueuom) = 'pg/ml' THEN 8845
	WHEN LOWER(temp_table.valueuom) = 'miu/l' THEN 9040
	WHEN LOWER(temp_table.valueuom) = 'miu/ml' THEN 9550
	WHEN LOWER(temp_table.valueuom) = 'units' THEN 8510
	WHEN LOWER(temp_table.valueuom) = 'uiu/l' THEN 44777583
	WHEN LOWER(temp_table.valueuom) = 'uiu/ml' THEN 9093
	WHEN LOWER(temp_table.valueuom) = 'uu/ml' THEN 9093 -- uIU/mL
	WHEN LOWER(temp_table.valueuom) = 'mg/24hr' THEN 8909
	WHEN LOWER(temp_table.valueuom) = 'u/l' THEN 8645
	WHEN LOWER(temp_table.valueuom) = 'ml/min' THEN 8795
	WHEN LOWER(temp_table.valueuom) = '#/cu mm' THEN 8785 -- per cubic millimeter [for WBC or RBC in peritoneal fluid]
	WHEN LOWER(temp_table.valueuom) = '#/uL' THEN 8647
	WHEN LOWER(temp_table.valueuom) = 'gpl' THEN 4171221
	WHEN LOWER(temp_table.valueuom) = 'score' and temp_table.loinc_code = '15112-6' THEN 4196800 -- SNOMED code for Leukocyte alkaline phosphatase score (class: procedure)
	WHEN LOWER(temp_table.valueuom) = '/mm3' THEN 8785
	WHEN LOWER(temp_table.valueuom) = 'sec' OR LOWER(temp_table.valueuom) = 'seconds' THEN 8555
	WHEN LOWER(temp_table.valueuom) = 'serum vis' THEN 3010493 -- LOINC code for Viscosity of Serum
	WHEN LOWER(temp_table.valueuom) = 'eu/dl' THEN 8829
	WHEN LOWER(temp_table.valueuom) = 'mm/hr' THEN 8752
	ELSE 0
  END as unit_concept_id,
   0 as provider_id,
   visit_occurence_id,
   measurement_source_value,
   measurement_source_concept_id,
   valueuom as unit_source_value,
   value_source_value
FROM
(SELECT
 labevents.row_id as measurement_id,
 labevents.subject_id as person_id,
 main_concept.concept_id,
 CAST( labevents.charttime as DATE ) as measurement_date,
 CAST( labevents.charttime as TIME ) as measurement_time,
 CASE
      WHEN is_number(CAST(labevents.hadm_id AS TEXT)) = TRUE THEN 45877824  -- It mean that it was measured in the ICU
      ELSE 45461226 -- could be anything else
 END as measurement_type_concept_id,
 CASE

	WHEN labevents.value ILIKE '%:%' THEN 000000 -- ????
	WHEN labevents.value ILIKE '%/%' THEN 000000 -- ????
	WHEN labevents.value ILIKE '%-%' THEN 000000 -- Range
	WHEN labevents.value ILIKE '%<=%' THEN 4171754 -- SNOMED Meas Value Operator (<=)
	WHEN labevents.value ILIKE '%<%' or LOWER(labevents.value) ILIKE '%less than%' THEN 4171756 -- SNOMED Meas Value Operator (<)
	WHEN labevents.value ILIKE '%>=%' THEN 4171755 -- SNOMED Meas Value Operator (>=)
	WHEN labevents.value ILIKE '%>%' or LOWER(labevents.value) ILIKE '%greater than%' THEN 4172704 -- SNOMED Meas Value Operator (>)
	ELSE 0
   END as operater_concept_id,
 valuenum as value_as_number,
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
   END as value_as_concept_id,
   labevents.hadm_id as visit_occurence_id,
   d_labitems.label as measurement_source_value,
   labevents.itemid as measurement_source_concept_id,
   labevents.valueuom as valueuom,
   CASE
	WHEN ( length( labevents.value ) > 45 ) THEN CONCAT( LEFT ( labevents.value, 45 ), '...')
	ELSE labevents.value  --
   END as value_source_value,
   d_labitems.loinc_code as loinc_code


FROM
  mimiciii.labevents
INNER JOIN mimiciii.d_labitems ON d_labitems.itemid = labevents.itemid
LEFT JOIN ohdsi.concept as main_concept ON main_concept.concept_code = d_labitems.loinc_code
WHERE is_number(CAST(main_concept.concept_id AS TEXT)) = TRUE
	and subject_id > 82000 -- for test purpose (limiting the number of subjects)
--LIMIT 1000
) as temp_table
LEFT JOIN ohdsi.concept as unit_concept on LOWER( unit_concept.concept_code) = LOWER(temp_table.valueuom)
---WHERE patients.subject_id = labevents.subject_id and patients.subject_id > 82000


-- #7 ANTIBIOTICS
/*

INSERT INTO ohdsi.drug_exposure( drug_concept_id, person_id, drug_exposure_start_date, drug_exposure_start_time,
	drug_exposure_end_date, drug_exposure_end_time, drug_type_concept_id,
	effective_drug_dose, dose_unit_concept_id, visit_occurrence_id, drug_source_value,route_source_value, route_concept_id )
SELECT DISTINCT ON (temp.administration_id)
	concept.concept_id as value_as_concept_id, -- Concept of the antibiotics
	temp.subject_id as person_id,
	CAST( temp.starttime as DATE ) as drug_exposure_start_date,
	CAST( temp.starttime as TIME ) as drug_exposure_start_time,
	CAST( temp.endtime as DATE ) as drug_exposure_end_date,
	CAST( temp.endtime as TIME ) as drug_exposure_end_time,
	21603553 as drug_type_concept_id, -- ATC 'Antibiotics'
	1 as effective_drug_dose,
	8513 as dose_unit_concept_id,
	temp.hadm_id as visit_occurrence_id,
	temp.label as drug_source_value,
	temp.ordercategorydescription as route_source_value,
	CASE
		WHEN lower(temp.ordercategorydescription) in ('drug push') THEN 21603553-- It is not really push mostly. It just means that it was pushed into saline.
		ELSE 0
	END as route_concept_id
FROM

(SELECT
	CONCAT( regexp_replace( regexp_replace(items.label, ' .*', ''), '/' , ' / ' ) , '%') as first_second_agent,
	lower(items.label) as l_label,
	input.row_id as administration_id,
	items.itemid as item_id,
* FROM
mimiciii.inputevents_mv as input,
mimiciii.d_items as items
WHERE items.itemid = input.itemid and input.subject_id > 82000 and
input.ordercategoryname ilike '%antibiotics%' and
lower(input.ordercomponenttypedescription) != 'mixed solution' and
cancelreason = 0) as temp
LEFT JOIN ohdsi.concept on concept.concept_name ILIKE temp.first_second_agent
WHERE  concept.vocabulary_id = 'RxNorm' AND
	concept_class_id in ('Clinical Drug', 'Ingredient', 'Branded Drug Form')
	AND concept_name !~ '.*[0-9].*'
	AND lower(concept_name) NOT ILIKE '%oral%'
	AND lower(concept_name) NOT ILIKE '%topical%'
	AND lower(concept_name) NOT ILIKE '%tablet%'
	AND lower(concept_name) NOT ILIKE '%otic%'
	AND lower(concept_name) NOT ILIKE '%injectable%'
	AND lower(concept_name) NOT ILIKE '%opthalmic%'
	AND lower(concept_name) NOT ILIKE '%irrigation%'
	AND lower(concept_name) NOT ILIKE '%capsule%'
	AND lower(concept_name) NOT ILIKE '%suspension%'
	AND lower(concept_name) NOT ILIKE '%syrup%'
	AND lower(concept_name) NOT ILIKE '%solution%'
	AND lower(concept_name) NOT ILIKE '%ointment%'
	AND lower(concept_name) NOT ILIKE '%suppository%'
	AND lower(concept_name) NOT ILIKE '%rectal%'
	AND lower(concept_name) NOT ILIKE '%vaginal%'
	AND lower(concept_name) NOT ILIKE '%prefilled%'
	AND lower(concept_name) NOT ILIKE '% pad%'

*/

-- #1 Vasopressor


INSERT INTO ohdsi.drug_exposure( drug_concept_id, person_id, drug_exposure_start_date, drug_exposure_start_time,
	drug_exposure_end_date, drug_exposure_end_time, drug_type_concept_id,
	effective_drug_dose, dose_unit_concept_id, visit_occurrence_id, drug_source_value,route_source_value, route_concept_id )
SELECT
	CASE
		WHEN lower(items.label) = 'norepinephrine' THEN 1321341
		WHEN lower(items.label) = 'dopamine' THEN 1337860
		WHEN lower(items.label) = 'dobutamine' THEN 1337720
		WHEN lower(items.label) = 'epinephrine' THEN 1343916
		WHEN lower(items.label) = 'phenylephrine' THEN 1135766
		WHEN lower(items.label) = 'vasopressin' THEN 1507835
		WHEN lower(items.label) = 'milrinone' THEN 1368671
	END as drug_concept_id,
	input.subject_id,

	CAST( input.starttime as DATE ) as drug_exposure_start_date,
	CAST( input.starttime as TIME ) as drug_exposure_start_time,
	CAST( input.endtime as DATE ) as drug_exposure_end_date,
	CAST( input.endtime as TIME ) as drug_exposure_end_time,

	44804810 as drug_type_concept_id, -- Procedure: IV Administration of vasoactive agents.

	CASE
		WHEN input.statusdescription = 'Paused' THEN 0.0001
		ELSE input.rate
	END as effective_drug_dose,
	CASE
		WHEN input.rateuom = 'mcg/kg/min' THEN 9692
		WHEN input.rateuom = 'units/hour' THEN 8630
		ELSE 0 --only these two types of units are used for vasopressors.
	END as dose_unit_concept_id,

	input.hadm_id as visit_occurrence_id,
	items.label as drug_source_value,
	input.ordercategorydescription as route_source_value,
	CASE
		WHEN lower(input.ordercategorydescription) in ('continuous med') THEN 4078727
		ELSE 0
	END as route_concept_id

FROM

mimiciii.inputevents_mv as input,
mimiciii.d_items as items

WHERE items.itemid = input.itemid and input.subject_id > 82000 and
lower(items.label) IN ( 'norepinephrine', 'dopamine', 'dobutamine' , 'epinephrine', 'phenylephrine', 'vasopressin', 'milrinone')
	and lower(input.ordercategoryname) = '01-drips' and cancelreason = 0

ORDER BY starttime


-- Populate Care Site

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


/*
SELECT * from mimic2v26.icustay_detail
WHERE random () < 0.1;

*/
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
	--(, 'Surgical ICU', 45877825, '6', 'SICU'),
	-- Using the concept id for CTICU
	(7, 'Cardiac Surgery Recovery Unit', 45881475, '54', 'CSRU'),
	(8, 'Postoperative Anethesia Care Unit', 45880582, '46', 'PACU'),
	(9, 'Adult Trauma Critical Care Unit', 45885091, '7', 'T_CTICU'),
	-- The is no concept id for NeuroSurgical ICU, so we're using the id for NICU
	(10, 'Neurosurgical ICU', 45881477, '56', 'NSICU'),
	-- There is no concept id for PCI. The id for 'special care unit' is used.
	(11, 'Progressive Care Unit (PCU)', 4166938, '48', 'PCU'),
	(12, 'Trauma Surgical Intensive Care Unit (TSICU)', 45881482, '14', 'TSICU'),
	(13, 'Regular Ward', 4024317, '8', 'Regular Ward');

-- ICU Stay to Visit Occurence
-- visit occurence can be icu visit, but it might be simply ward visit.
-- we will add 100,000 to the icustay_id, so it could 'overlap' with


-- Admission to the ICU

/*

INSERT INTO ohdsi.visit_occurrence (visit_occurrence_id, person_id, visit_concept_id, visit_start_date, visit_start_time, visit_end_date, visit_end_time
	, visit_type_concept_id, provider_id, care_site_id, visit_source_value, visit_source_concept_id)

SELECT stay.icustay_id + 10000000 as visit_occurrence_id,
	subject_id as person_id,
	4137917 as visit_concept_id, -- "Admission to adult intensive care unit"
	CAST(intime as DATE) as visit_start_date,
	CAST(intime as TIME) as visit_start_time,
	CAST(outtime as DATE) as visit_end_date,
	CAST(outtime as TIME) as visit_end_time,
	0 as visit_type_concept_id,
	NULL as provider_id,
	care_site.care_site_id as care_site_id,
	NULL as visit_source_value,
	NULL as visit_source_concept_id
FROM mimiciii.icustays as stay
LEFT JOIN ohdsi.care_site ON care_site.place_of_service_source_value = first_careunit --and care_site IS NULL
WHERE stay.subject_id > 82000

*/


-- Admission to the ER (Might overlap with the ICU admission above)

/*

INSERT INTO ohdsi.visit_occurrence (visit_occurrence_id, person_id, visit_concept_id, visit_start_date, visit_start_time, visit_end_date, visit_end_time
	, visit_type_concept_id, provider_id, care_site_id, visit_source_value)
SELECT
	adm.hadm_id as visit_occurrence_id,
	adm.subject_id as person_id,
	8715 as visit_concept_id,
	CAST(admittime as DATE) as admittime,
	CAST(admittime as TIME) as admittime,
	CAST(dischtime as DATE) as dischtime,
	CAST(dischtime as TIME) as dischtime,
	CASE
		WHEN lower(admission_type) = 'newborn' THEN 40760826 -- Observation/Birth Time -- Obviously MIMIC3 contains the record of newborns!
		WHEN lower(admission_type) = 'emergency' and lower(admission_location) = 'emergency room admit' THEN 4163685 -- Emegency depeartment visit
		WHEN lower(admission_type) ilike '%elective%' THEN 4314435 -- Elective admission
		WHEN lower(admission_location) ilike '%transfer from hosp%' THEN 45884207 -- Acute care hospital transfer
		WHEN lower(admission_location) ilike '%referral%' THEN 4144684 --patient referral
		WHEN lower(admission_type) = 'emergency' and lower(admission_location) = 'transfer from%' THEN 4163685 -- Emegency depeartment visit
		ELSE 0
	END as visit_type_concept_id,
	0 as provider_id,
	0 as care_site_id,
	CONCAT(admission_type, '/', admission_location) as visit_source_value
FROM
	mimiciii.admissions as adm
WHERE
	adm.subject_id > 82000


*/


﻿
INSERT INTO ohdsi.measurement (measurement_id, person_id, measurement_concept_id, measurement_date, measurement_time, measurement_type_concept_id,
	operator_concept_id, value_as_number, value_as_concept_id, unit_concept_id, provider_id, visit_occurrence_id, measurement_source_value, measurement_source_concept_id,
	unit_source_value, value_source_value)

SELECT
	measurement_id, person_id, measurement_concept_id, measurement_date, measurement_time, measurement_type_concept_id,
	0 as operator_concept_id, value_number, value_concept_id, unit_concept_id, 0 as provider_id,
	temp.admission_id as visit_occurrence_id,
	CASE
		WHEN ( length( temp.label ) > 45 ) THEN CONCAT( LEFT ( temp.label, 45 ), '...')
		ELSE temp.label  --
	END as measurement_source_value,
	temp.item_id as measurement_source_concept_id,
	temp.valueuom as unit_source_value,
	CASE
		WHEN ( length( temp.value ) > 45 ) THEN CONCAT( LEFT ( temp.value, 45 ), '...')
		ELSE temp.value  --
	END as value_source_value
FROM (
SELECT (chartevents.row_id + 900000000) as measurement_id, -- labvalue also get into measurement and there is risk of overlapping
	subject_id as person_id,
	CASE
	-- Note: Valid Observation Concepts are not enforced to be from any domain.
	-- They still should be Standard Concepts, and they typically belong to the
	-- “Observation” or sometimes “Measurement” domain.
	--WHEN is_number (CAST( observation_concept_translator.target_concept_id as varchar(20))) = TRUE
	--	THEN observation_concept_translator.target_concept_id -- Uses translator table

	-- Basic Measurements
	WHEN LOWER(item.label) in ('admit wt', 'admission weight (kg)') THEN 4268280 -- SNOMED Observation for 'baseline weight'
	WHEN LOWER(item.label) in ( 'admit ht' , 'height (cm)')THEN 4177340 -- SNOMED Observation for 'body height measure'
	WHEN LOWER(item.label) = 'daily weight' THEN 40786050 -- (LOINC/Measurement for 'Weight')
	WHEN LOWER(item.label) IN ( 'present weight (kg)') THEN 40786050 -- (LOINC/Measurement for 'Weight')
	WHEN LOWER(item.label) ILIKE 'weight kg' THEN 40786050 -- (LOINC/Measurement for 'Weight')
	WHEN LOWER(item.label) = 'weight change' THEN 4268831 -- (SNOMED/Measurement for 'Weight change finding')
	--WHEN LOWER(label) = 'birthweight' THEN

	-- Mental Status
	WHEN LOWER(item.label) = 'gcs - verbal response' THEN 3009094
	WHEN LOWER(item.label) = 'gcs - motor response' THEN 3008223
	WHEN LOWER(item.label) = 'gcs - eye opening' THEN 3016335

	-- Clinical Scorings
	WHEN (LOWER(item.label) ILIKE '%overall sofa%') or (item.label = 'SOFA Score') THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE '%cardiovascular sofa%' THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE '%respiratory sofa%' THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE '%hematologic sofa%' THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE '%renal sofa%' THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE '%neurologic sofa%' THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE '%hepatic sofa%' THEN -1 -- There is no concept code for SOFA
	WHEN LOWER(item.label) ILIKE 'RSBI%' THEN -1 -- THere is no concept code for 'rapid shallow breathing index'
	WHEN LOWER(item.label) ILIKE 'calculated saps%' THEN 45434748

	-- Clinical Assessment (Should be moved to observation)
	WHEN LOWER(item.label) = 'orientation' THEN 4183166 -- SNOMED Observation for 'Orientation'
	WHEN LOWER(item.label) = 'pupil size r/l' THEN 4062823 -- SNOMED Condition for 'O/E - pupil size'

	-- GCS
	WHEN LOWER(item.label) = 'gcs total' THEN 40623633 -- Measurement: GCS

	-- Temperature
	WHEN LOWER(item.label) ilike 'temperature fahrenheit' THEN 9289
	WHEN LOWER(item.label) ilike 'temperature c%' THEN 40786332 -- LOINC/Temperature
	WHEN LOWER(item.label) IN ( 'blood temperature cco (c)' ) THEN 40305166 --- 'core temperature'
	WHEN LOWER(item.label) = 'temp. site' AND LOWER(value) = 'blood' THEN 3007416 -- LOINC/Measurement: 'Body temperature - Intravascular'
	WHEN LOWER(item.label) = 'temp. site' AND LOWER(value) = 'oral' THEN 3006322
	WHEN LOWER(item.label) = 'temp. site' AND LOWER(value) = 'axillary' THEN 3025085
	WHEN LOWER(item.label) = 'temp. site' AND LOWER(value) = 'rectal' THEN 3022060
	WHEN LOWER(item.label) = 'inspired gas temperature' THEN 4353948

	-- BP
	WHEN LOWER(item.label) IN ( 'arterial blood pressure mean', 'arterial bp mean' , 'radial map') THEN 4108290 -- 'Invasive mean arterial pressure'
	WHEN LOWER(item.label) = 'arterial blood pressure systolic' THEN 4353843 -- 'Invasive Systolic Pressure'
	WHEN LOWER(item.label) = 'arterial blood pressure diastolic' THEN 4354253 -- 'Invasive Diastolic Pressure'
	WHEN LOWER(item.label) in ('non invasive blood pressure systolic', 'art bp systolic') THEN 4152194 -- 'Systolic blood pressure'
	WHEN LOWER(item.label) in ('non invasive blood pressure diastolic', 'art bp diastolic') THEN 4154790 -- Diastolic blood pressure'
	WHEN LOWER(item.label) in ('non invasive blood pressure mean', 'art bp mean') THEN 4239021 -- 'mean blood pressure'

	-- SWAN-GANTZ
	WHEN LOWER(item.label) = 'pulmonary artery pressure systolic' THEN 4353855
	WHEN LOWER(item.label) = 'pulmonary artery pressure diastolic' THEN 3017188
	WHEN LOWER(item.label) = 'pulmonary artery pressure mean' THEN 3028074

	-- Heart Rate
	WHEN LOWER(item.label) = 'heart rate' THEN 3027018 -- LOINC Code for HR

	-- Respiratory Rate
	WHEN LOWER(item.label) IN ('resp rate', 'respiratory rate','resp rate (total)', 'respiratory rate (total)')  THEN 3024171 -- LOINC Code for Resp Rate
	WHEN LOWER(item.label) IN ('resp rate (spont)', 'spont resp rate', 'respiratory rate (spontaneous)', 'spont rr') THEN 4154772 -- SNOMED code for 'Rate of spontaneous respiratorion'

	-- Oxygen saturation
	WHEN LOWER(item.abbreviation) = 'spo2' THEN 40762499
	WHEN LOWER(item.label) = 'cao2' THEN 40772930 -- LOINC/Measurement - Oxygen Content

	-- Cardic monitoring

	WHEN LOWER(item.label) IN ( 'cardiac index', 'ci (picco)') THEN 4208254 --- SNOMED Code for Cardiac Index (Observation)
	WHEN LOWER(item.label) ILIKE 'c.o.%' THEN 3005555 --- LOINC Code for LV Cardiac Output (Measurement)
	WHEN LOWER(item.label) = 'co (arterial)' THEN 4221102
	WHEN LOWER(item.label) IN ('permanent pacemaker rate') THEN 4215909
	WHEN LOWER(item.label) IN ('temporary pacemaker rate') THEN 4215909 -- not distingushed from permanent pacemaker rate

	WHEN LOWER(item.label) = 'heart rhythm' THEN 40630178 --- SNOMED Code for Cardiac Rhythm [Observable Entity]
	WHEN LOWER(item.label) = 'respiratory rate' THEN  86290005 ---
	WHEN LOWER(item.label) = 'precaution' AND LOWER(value) = 'contact' THEN 000000 --'contact precaution'
	WHEN LOWER(item.label) = 'arterial bp' or LOWER(label) = 'arterial bp mean' THEN 4108290
	WHEN LOWER(item.label) = 'temperature f' THEN 4022230

	WHEN LOWER(item.label) = 'pap mean' THEN 4353611 -- SNOMED Observation for Pulmonary artery pressure
	WHEN LOWER(item.label) = 'pap s/d' THEN 4353855 -- SNOMED Observation for Pulmonary artery systolic pressure
	WHEN LOWER(item.label) = 'swan svo2' THEN 0
        WHEN LOWER(item.label) ilike ('%svi%') THEN -1
        WHEN LOWER(item.label) IN ( 'svri', 'svri (picco)') THEN -1
        WHEN LOWER(item.label) in ( 'stroke volume', 'sv (arterial)' ) THEN -1
        WHEN LOWER(item.label) in ('svv (arterial)', 'svv (picco)' ) THEN -1 -- Stroke volume variation
	WHEN LOWER(item.label) = 'ef (cco)' THEN 3027172 -- simply 'ejection fraction'
        WHEN LOWER(item.label) IN ('swan svo2' , 'svo2', 'scvo2 (presep)') THEN 4096100 -- SNOMED Measurement for 'Mixed venous oxygen saturation measurement'

	WHEN LOWER(item.label) IN ('cardiac output (co nicom)', 'co (picco)') THEN 45766800 -- Noninvasive cardiac output monitoring
	WHEN LOWER(item.label) IN ('cardiac index (ci nicom)') THEN 4208254 -- there is no way to specify invasive vs noninvasive

        -- IABP-related

        WHEN LOWER(item.label) = 'IABP setting' THEN -1
        WHEN LOWER(item.label) = 'BAEDP' THEN 0 -- Balloon Aortic End Diastolic Pressure

	-- Vent setting

	-- BIPAP
	WHEN LOWER(item.label) in ('bipap epap') THEN 44817050 -- not distingushed from IPAP (but should be recognizable by the number difference)
	WHEN LOWER(item.label) in ('bipap ipap') THEN 44817050

	-- VENT / PEEP-related
	WHEN LOWER(item.label) = 'peep set' or LOWER(label) = 'peep' THEN 4216746 -- SNOMED Clinical observation for 'Positive end expiratory pressure setting'
	WHEN LOWER(item.label) = 'auto-peep level'  THEN -1 -- Concept not available
	WHEN LOWER(item.label) ILIKE 'total peep%' or LOWER(label) = 'measured peep'THEN 4353713 -- SNOMED Clinical observation for 'Positive end expiratory pressure'

	-- VENT / Tidal volume
	WHEN LOWER(item.label) IN ('spont. tidal volume', 'tidal volume (spont)', 'spont tidal volumes'
	 ,'spon. vt (l) (mech.)' ,'spont vt') THEN 4108448 -- SNOMED Clinical observation for 'spontaneous tidal volume'
	WHEN LOWER(item.label) = ( 'tidal volume (observed)' ) THEN 4108137 -- SNOMED Clinical observation for 'ventilator delivered tidal volume'
	WHEN LOWER(item.label) = 'tidal volume' or LOWER(label) = 'tidal volume (set)' THEN 4220163 -- SNOMED Clinical observation for 'tidal volume setting'
	WHEN LOWER(item.label) = 'tidal volume (spontaneous)' THEN 4108448

	-- VENT / Respiratory rate set
	WHEN LOWER(item.label) in ( 'respiratory rate set' , 'respiratory rate (set)') THEN 4108138 -- SNOMED Observation 'Ventilator rate'

	-- VENT / FiO2
	WHEN LOWER(item.label) IN ('fio2', 'fio2 [meas]', 'fio2 set', 'inspired o2 fraction', 'vision fio2') THEN 4353936
	WHEN LOWER(item.label) ILIKE 'o2 flow%' THEN 3005629

	-- VENT / Other vent monitoring parameters
	WHEN LOWER(item.label) IN ('mean airway pressure', 'paw high') THEN 44782824
	WHEN LOWER(item.label) IN ('peak insp. pressure') THEN 4139633
	WHEN LOWER(item.label) IN ('plateau pressure') THEN 44782825
	WHEN LOWER(item.label) ILIKE 'pressure support' THEN 3000461
	WHEN LOWER(item.label) IN ('compliance (40-60ml)') THEN 4090322 -- 'Static lung compliance'
	WHEN LOWER(item.label) IN ('o2 delivery device') THEN 4036936
	WHEN LOWER(item.label) IN ('i:e ratio') THEN 4084278
	WHEN LOWER(item.label) IN ('minute volume') THEN 4353621
	WHEN LOWER(item.label) IN ('inspiratory time') THEN 4353947
	WHEN LOWER(item.label) IN ('cuff pressure') THEN 4108458
	WHEN LOWER(item.label) in ('inspired gas temp.') THEN 4353948

	-- Other resp
	WHEN LOWER(item.label) IN ('hourly pfr') THEN 4197461

	-- SWAN-GANTZ
	WHEN LOWER(item.label) IN ('cardiac output (cco)', 'cardiac output (thermodilution)') THEN 4321094 -- 'CO thermodilution'
	WHEN LOWER(item.label) IN ('transpulmonary pressure (insp. hold)', 'pcwp') THEN 4040920 -- 'pulmonary capillary wedge pressure'
	WHEN LOWER(item.label) IN ('paedp') THEN 3014590


	-- Feeding
	WHEN LOWER(item.label) IN ('diet type') THEN 4043372 --- "Feeding"/Observation/SNOMED

-- 'lvad flow lpm''

	-- Other circulation-related monitoring
	WHEN LOWER(item.label) IN ('central venous pressure', 'cvp' ) THEN 4323687

	-- Neuro parameters
	WHEN LOWER(item.label) IN ('intracranial pressure', 'icp', 'intra cranial pressure') THEN 4353953
	WHEN LOWER(item.label) IN ('cerebral perfusion pressure', 'ccp') THEN 4353710 -- Cerebral perfusion pressure

	-- Other
	WHEN LOWER(item.label) = 'bladder pressure' THEN 4090339
	WHEN LOWER(item.label) = 'abi (r)' THEN 44805247
	WHEN LOWER(item.label) = 'abi (l)' THEN 44805248

	ELSE 0

  END as measurement_concept_id,
  CAST ( charttime AS DATE) as measurement_date,
  CAST ( chartevents.charttime AS TIME) as measurement_time,
  CASE
	WHEN is_number(CAST(chartevents.icustay_id as TEXT)) = FALSE THEN 0
	ELSE 45877824 -- ICU
  END as measurement_type_concept_id,
  valuenum as value_number,
  value as value_str,
  hadm_id as admission_id,
    CASE
	-- Clinical assessment
	WHEN LOWER(value) = 'pinpoint' THEN 4061876 -- SNOMED Condition: 'O/E - pinpoint pupils'
	WHEN LOWER(value) = 'fully dilated' THEN 4290615 -- SNOMED Clinical finding: 'Dilatated pupil'
	-- O2 Delivery Methods
	WHEN LOWER(value) = 'none' THEN 45881798 -- LOINC Meas Value: "Room Air"
	WHEN LOWER(value) = 'face tent' THEN 4138487 -- SNOMED Device: "Face tent oxygen delivery device"
	WHEN LOWER(value) = 't-piece' THEN 4188570 -- SNOMED Device: "T-piece without bag"
	WHEN LOWER(value) = 'nasal cannula' THEN 4224038 -- SNOMED Device: "oxygen Nasal cannula"
	WHEN LOWER(value) = 'non-rebreather' THEN 4145528
	WHEN LOWER(value) = 'aerosol-cool' THEN 4145694 -- SNOMED Device: "aerosol oxygen mask"
	WHEN LOWER(value) = 'ventilator' THEN 40493026 -- SNOMED Device: "mechanical ventilator"
	WHEN LOWER(value) = 'trach mask' THEN 45760219
	WHEN LOWER(value) = 'venti mask' THEN 4322904 -- SNOMED Device: "venturi mask"
	WHEN LOWER(value) = 'bipap mask' THEN 45767334 -- SNOMED Device: "Bipap face mask, single use"
	WHEN LOWER(value) = 'hi flow neb' THEN 4139525 -- SNOMED Device: "high flow oxygen nasal cannula"
	--WHEN LOWER(value1) = ''

	-- Cardiac monitoring
	WHEN LOWER(value) = 'sinus tachy' THEN 4007310
	WHEN LOWER(value) = 'atrial fib' THEN 313217
	WHEN LOWER(value) = 'sinus brady' THEN 4171683 -- SNOMED Condition for Sinus bradycardia
	WHEN LOWER(value) = 'normal sinus' THEN 4276669 -- SNOMED Condition for Normal sinus
	WHEN LOWER(value) = '1st deg av block' THEN 314379 -- SNOMED Condition for 'First degree atrioventricular block'
	WHEN LOWER(value) = '2nd deg av block' THEN 318448 -- SNOMED Condition for 'second degree atrioventricular block'
	WHEN LOWER(value) = '2nd avb/mobitz i' THEN 4205137
	WHEN LOWER(value) = '2nd avb/mobitz ii' THEN 313780
	WHEN LOWER(value) = 'comp heart block' THEN 40288216
	WHEN LOWER(value) = 'av paced' THEN 4088998 -- SNOMED Measurement for 'AV sequential pacing pattern'
	WHEN LOWER(value) = 'a paced' THEN 4089488 -- SNOMED Measurement for 'Atrial pacing pattern'
	WHEN LOWER(value) = 'v paced' THEN 4092038 -- SNOMED Measurement for 'ventricular pacing pattern'
	WHEN LOWER(value) = 'atrial flutter' THEN 314665
	WHEN LOWER(value) = 'junctional' THEN 4038688 -- SNOMED Condition for 'junctional rhythm'
	WHEN LOWER(value) = 'multfocalatrtach' THEN 0
	WHEN LOWER(value) = 'parox atrial tach' THEN 0
	WHEN LOWER(value) = 'supravent tachy' THEN 4275423
	WHEN LOWER(value) = 'vent. tachy' THEN 4275423
	WHEN LOWER(value) = 'asystole' THEN 4216773
	WHEN LOWER(value) = 'd/c''d' THEN 4132627 -- SNOMED Observation for 'Discontinued' (Mostly for mechanical vent)
	WHEN LOWER(value) = 'tube feeding' THEN 4222605 -- SNOMED Observation / Tube feeding diet
	WHEN LOWER(value) = 'diabetic' THEN 4052041 -- SNOMED Observation / Diabetic diet
	WHEN LOWER(value) = 'full liquid' THEN 4033731 -- SNOMED Obsevation / Liquid diet
	WHEN LOWER(value) = 'clear liquid' THEN 4033731 -- SNOMED Obsevation / Liquid diet (not diferrentiated from full liquid)
	WHEN LOWER(value) = 'npo' THEN 4033731 -- SNOMED Observation / 'nothing by mouth status'
	WHEN LOWER(value) = 'tpn' THEN 45881254 -- LOINC Meas Value / 'TPN'
	WHEN LOWER(value) = 'renal' THEN 0 -- renal diet
	WHEN LOWER(value) ILIKE '%low cholest' THEN 4215995 -- SNOMED Clinica Obs: Low cholesterol diet
	WHEN LOWER(value) = 'soft solid' THEN 4301609 -- SNOMED Clinica Obs: Soft diet
	ELSE NULL
  END as value_concept_id,

    CASE
	--WHEN is_number (CAST( unit_concept_translator.target_concept_id as varchar(20))) = TRUE
	--	THEN unit_concept_translator.target_concept_id
	WHEN LOWER(valueuom) = 'mmhg' THEN 8876
	WHEN LOWER(valueuom) = 'deg. f' THEN 9289
	WHEN LOWER(valueuom) = 'deg. c' THEN 8653
	WHEN LOWER(valueuom) = 'l/min' THEN 8698
	WHEN LOWER(valueuom) = 'kg' THEN 9529
	WHEN LOWER(valueuom) = 'bpm' THEN 8541 -- UCUM per minute
	WHEN LOWER(valueuom) = '%' THEN 8554
	WHEN LOWER(valueuom) = 'cmh2o' THEN 44777590
	WHEN LOWER(valueuom) = 'ml/b' THEN 8587 -- UCUM unit for 'milliliter' (there is no unit avilable for ml per breath but it doesnt really matter...)
	WHEN LOWER(valueuom) = 'torr' THEN 4136788
	WHEN LOWER(label) = 'pupil size r/l' THEN 8588 -- Millimeter
	ELSE 0
  END as unit_concept_id, chartevents.itemid as item_id, *

FROM
	mimiciii.chartevents_14 as chartevents

INNER JOIN mimiciii.d_items as item on item.itemid = chartevents.itemid
WHERE chartevents.subject_id > 82000
    ) as temp
    WHERE lower(temp.label) NOT ILIKE '%alarm%' and lower(temp.label) NOT ILIKE '%gauge%' and lower(temp.label) NOT ILIKE '%threshold%' and lower(temp.label) NOT ILIKE '%wires%'
     and lower(temp.label) NOT ILIKE '%mdi%'  and lower(temp.label) NOT ILIKE '%pca%' and lower(temp.label) NOT ILIKE '%arctic%' and temp.label NOT ILIKE '%arctic%'
      and lower(temp.label) NOT ILIKE '%psv%' and lower(temp.label) NOT ILIKE '%ett%' and lower(temp.label) NOT IN ('code status',
       'parameters checked', 'bed bath' , 'called out', 'trach care', 'stool guaiac qc',
       'apnea interval', 'ventilator tank #1', 'unassisted systole', 'assisted systole', 'temporary pacemaker wires ventricular',
       'cuff presure', 'fspn high', 'vti high', 'ventilator tank #2', 'return pressure', 'filter pressure', 'temporary pacemaker wires atrial',
       'access pressure', 'effluent pressure', 'inspiratory ratio', 'expiratory ratio', 'activity hr', 'activity rr', 'augumented diastole',
       'iabp mean', 'vital cap', 'baedp', 'paedp', 'baedp', 'pinsp (draeger only)', 'baseline current/mA', 'richmond-ras scale') /*and measurement_concept_id = 0*/
       and lower(temp.category) NOT IN ( 'labs', 'alarms', 'skin - impairment', 'treatments', 'adm history/fhpa', 'restraint/support systems', 'access lines - invasive' , 'tandem heart' ,'general'
       )


--ORDER BY random()

/*
Not addressed: 'PCA~', 'code status'

*/