from functools import wraps

import attr

from tdxapi.models import CustomAttributeList


@attr.s
class TdxManager(object):
    dispatcher = attr.ib(repr=False, eq=False)

    def _new(self, class_, **kwargs):
        model = class_(**kwargs)

        # New objects should not be flagged as partial to allow saving
        model._partial = False

        # If manager has an app_id, set it on new object
        try:
            model.app_id = self.app_id
        except AttributeError:
            pass

        # If object has attributes and manager has a template, set it on the object
        try:
            model.attributes.match_template(self.attribute_template)
        except AttributeError:
            pass

        return model

    def _save(self, model, force, *args, **kwargs):
        if not force and model._partial:
            raise ValueError(
                "object data may not be complete, saving could "
                "result in data loss (use force=True to override)"
            )

        if model.id:
            updated_model = self._update(model, *args, **kwargs)
        else:
            updated_model = self._create(model, *args, **kwargs)

        for field in [f for f in attr.fields(model.__class__) if f.repr]:
            setattr(model, field.name, getattr(updated_model, field.name))

        try:
            model.attributes.match_template(self.attribute_template)
        except AttributeError:
            pass

    def _format_search_params(self, class_, dictionary):
        # dictionary comes from locals(), so remove self from the list and do not
        # set any search parameters that were not specified or custom attributes
        # because custom attributes need to be formatted first
        kwargs = {
            k: v
            for k, v in dictionary.items()
            if k not in ("self", "attributes") and v is not None
        }

        # Create search object from search data
        search_params = class_(**kwargs)

        search_attrs = dictionary.get("attributes", None)

        # If there are no custom attributes specified for searching, return object
        if search_attrs is None:
            return search_params

        formatted_search_attrs = CustomAttributeList()

        # If custom attributes were specified, get the attribute objects from template
        for search_attr in search_attrs:
            formatted_search_attrs.append(
                self.attribute_template.update_copy(search_attr[0], search_attr[1])
            )

        search_params.attributes = formatted_search_attrs

        return search_params

    def _create(self, *args, **kwargs):
        raise NotImplementedError

    def _update(self, *args, **kwargs):
        raise NotImplementedError


def tdx_method(method, url):
    def wrapper(f):
        f.method = method
        f.url = url

        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped

    return wrapper
