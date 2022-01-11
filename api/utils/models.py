from django.db.models import Model, Manager, QuerySet


def get_or_none(model, *args, **kwargs):
    if issubclass(model, Model):
        qs = model._default_manager.all()
    elif isinstance(model, Manager):
        qs = model.all()
        manager = model
        model = manager.model
    elif isinstance(model, QuerySet):
        qs = model
        model = qs.model
    else:
        raise Exception(f'You must provide a Model, Manager or QuerySet instance.')

    try:
        return qs.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
