.SUFFIXES:
.DELETE_ON_ERROR:

.PHONY: clean tests unittest endtoendtest updatestandard checkversions

PYTHON ?= python
PYTEST_BIN=$(PYTHON) -m pytest

export PYTHONPATH := ..

VERSION=current

cleaned_dicom_html=$(patsubst standard/%.html,tmp/%.html,$(wildcard standard/*.html))


all: core_tables relationship_tables dist/references.json

core_tables: dist/ciods.json dist/modules.json dist/macros.json dist/attributes.json dist/sops.json dist/confidentiality_profile_attributes.json

relationship_tables: dist/ciod_to_modules.json dist/ciod_to_func_group_macros.json dist/module_to_attributes.json dist/macro_to_attributes.json


dist/ciods.json: tmp/raw_ciod_module_tables.json
	$(PYTHON) process_ciods.py $< > $@

dist/modules.json: tmp/preprocessed_modules_attributes.json dist/ciod_to_func_group_macros.json
	$(PYTHON) process_modules.py $^ > $@

dist/macros.json: tmp/preprocessed_macros_attributes.json
	$(PYTHON) process_macros.py $< > $@

dist/attributes.json: tmp/part06.html
	$(PYTHON) extract_attributes.py $< > $@

dist/sops.json: tmp/part04.html
	$(PYTHON) extract_sops.py $< > $@

dist/confidentiality_profile_attributes.json: tmp/part15.html dist/attributes.json
	$(PYTHON) extract_conf_profile_attributes.py $^ > $@

dist/ciod_to_modules.json: tmp/raw_ciod_module_tables.json
	$(PYTHON) process_ciod_module_relationship.py $< > $@

dist/ciod_to_func_group_macros.json: tmp/raw_ciod_func_group_macro_tables.json
	$(PYTHON) process_ciod_func_group_macro_relationship.py $< > $@

dist/module_to_attributes.json: tmp/module_to_attributes_no_duplicates.json dist/macros.json dist/ciod_to_func_group_macros.json dist/macro_to_attributes.json
	$(PYTHON) postprocess_integrate_func_group_macros.py $^ > $@

dist/macro_to_attributes.json: tmp/macros_attributes_updated_references.json
	$(PYTHON) postprocess_merge_duplicate_nodes.py $< > $@

dist/references.json: tmp/modules_attributes_partial_references.json tmp/macros_attributes_partial_references.json tmp/raw_section_tables.json
	$(PYTHON) postprocess_save_references.py $^ > $@


tmp/module_to_attributes_no_duplicates.json: tmp/modules_attributes_updated_references.json
	$(PYTHON) postprocess_merge_duplicate_nodes.py $< > $@

tmp/modules_attributes_updated_references.json: tmp/modules_attributes_partial_references.json dist/references.json
	$(PYTHON) postprocess_update_reference_links.py $^ > $@

tmp/macros_attributes_updated_references.json: tmp/macros_attributes_partial_references.json dist/references.json
	$(PYTHON) postprocess_update_reference_links.py $^ > $@

tmp/modules_attributes_partial_references.json: tmp/modules_attributes_no_references.json
	$(PYTHON) postprocess_mark_references.py $< > $@

tmp/macros_attributes_partial_references.json: tmp/macros_attributes_no_references.json
	$(PYTHON) postprocess_mark_references.py $< > $@

tmp/modules_attributes_no_references.json: tmp/preprocessed_modules_attributes.json
	$(PYTHON) process_module_attribute_relationship.py $< > $@

tmp/macros_attributes_no_references.json: tmp/preprocessed_macros_attributes.json
	$(PYTHON) process_macro_attribute_relationship.py $< > $@

tmp/preprocessed_modules_attributes.json: tmp/raw_module_macro_attribute_tables.json
	$(PYTHON) preprocess_modules_with_attributes.py $< > $@

tmp/preprocessed_macros_attributes.json: tmp/raw_module_macro_attribute_tables.json
	$(PYTHON) preprocess_macros_with_attributes.py $< > $@

tmp/raw_ciod_module_tables.json: tmp/part03.html
	$(PYTHON) extract_ciod_module_tables.py $< > $@

tmp/raw_ciod_func_group_macro_tables.json: tmp/part03.html
	$(PYTHON) extract_ciod_func_group_macro_tables.py $< > $@

tmp/raw_module_macro_attribute_tables.json: tmp/part03.html
	$(PYTHON) extract_modules_macros_with_attributes.py $< > $@

tmp/raw_section_tables.json: extract_sections.py $(cleaned_dicom_html)
	$(PYTHON) $^ > $@


tmp/%.html: standard/%.html
	$(PYTHON) make_helpers.py normalize-html $< > $@


tests: unittest endtoendtest

unittest:
	cd .. && $(PYTEST_BIN) -m "not endtoend" tests

endtoendtest:
	cd .. && $(PYTEST_BIN) -m "endtoend" tests


updatestandard:
	$(PYTHON) make_helpers.py update-standard $(VERSION)

checkversions:
	$(PYTHON) make_helpers.py check-python

clean:
	git clean -fqx dist tmp
	$(PYTHON) make_helpers.py clean-generated
