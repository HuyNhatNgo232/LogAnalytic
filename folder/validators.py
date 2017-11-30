def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext[1].isdigit():
        raise ValidationError(u'Unsupported file extension.')

