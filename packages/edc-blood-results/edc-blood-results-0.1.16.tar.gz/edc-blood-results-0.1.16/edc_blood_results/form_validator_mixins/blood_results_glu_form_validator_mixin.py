from edc_glucose.utils import validate_glucose_as_millimoles_per_liter

from .blood_results_ifg_form_validator_mixin import BloodResultsIfgFormValidatorMixin


class BloodResultsGluFormValidatorMixin(BloodResultsIfgFormValidatorMixin):
    def evaluate_value(self, field_name):
        if field_name == "glucose_value":
            validate_glucose_as_millimoles_per_liter("glucose", self.cleaned_data)
