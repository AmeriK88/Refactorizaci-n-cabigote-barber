from django.core.exceptions import ValidationError

def apply_validation_error_to_form(form, e: ValidationError):
    if hasattr(e, "message_dict"):
        for field, msgs in e.message_dict.items():
            for msg in msgs:
                form.add_error(field, msg)
    else:
        form.add_error(None, e.messages[0])
