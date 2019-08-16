"""
"""

from __future__ import absolute_import
from .exceptions import ValidationError
import six


def _is_empty(field_value):
    ### TODO if field_value is None, skip  ### TODO makea parameter
    if field_value is None:
        return True
    # treat empty strings as empty values and skip
    if isinstance(field_value, (str, six.text_type)) and \
           len(field_value.strip()) == 0:
        return True
    return False

MISSING = object()

def validate(cls, values, partial=False, report_rogues=False):
    ### Reject model if _fields isn't present
    if not hasattr(cls, '_fields'):
        error_msg = 'cls is not a Model instance'
        raise ValidationError(error_msg)

    ### Containers for results
    new_data = {}
    errors = []

    if partial:
        needs_check = lambda k, v: k in values
    else:
        needs_check = lambda k, v: v.required or k in values

    ### Validate data based on cls's structure
    for field_name, field in cls._fields.items():
        ### Rely on parameter for whether or not we should check value
        if needs_check(field_name, field):
            try:
                field_value = values[field_name]
            except KeyError:
                field_value = MISSING

            ### TODO - this will be the new validation system soon
            if field_value is MISSING:
                if field.required:
                    error_msg = "Required field (%s) not found" % field_name
                    errors.append(error_msg)
                continue

            elif _is_empty(field_value):
                if not field.allow_empty and field.required:
                    error_msg = "Empty value found for (%s)." % field_name
                    errors.append(error_msg)
                new_data[field_name] = field_value
                continue

            ### Validate field value via call to BaseType._validate
            try:
                field._validate(field_value)
                ### TODO clean this
                result = field.for_python(field_value)
                new_data[field_name] = result
            except ValidationError as ve:
                errors.append(ve.messages)

    ### Report rogue fields as errors if `report_rogues`
    if report_rogues:
        class_fields = list(cls._fields.keys())
        rogues_found = set(values.keys()) - set(class_fields)
        if len(rogues_found) > 0:
            for field_name in rogues_found:
                error_msg = 'Unknown field found %s' % field_name
                field_value = values[field_name]
                errors.append(error_msg)

    ### Return on if errors were found
    if len(errors) > 0:
        #error_msg = 'Model validation errors'
        raise ValidationError(errors)

    return new_data
