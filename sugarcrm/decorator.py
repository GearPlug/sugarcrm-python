from sugarcrm.exception import WrongParameter
from functools import wraps

params = {
    'offset': int,
    'select_fields': list,
    'link_name_to_fields_array': dict,
    'max_results': int,
    'deleted': bool,
    'favorites': bool,
    'fields': list,
    'track_view': bool
}


def valid_parameters(func):
    @wraps(func)
    def helper(*args, **kwargs):
        for k, v in kwargs.items():
            if k in params.keys() and not isinstance(v, params[k]):
                raise WrongParameter('{} must be {} not {}'.format(k, params[k].__name__, type(v).__name__))

        return func(*args, **kwargs)

    return helper
