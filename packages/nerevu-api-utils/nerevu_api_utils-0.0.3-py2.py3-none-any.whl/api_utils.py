# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
api-utils
~~~~~~~~~

Attributes:
    LICENSES (dict): available python license classifiers.
"""
import re
from uuid import uuid4
from hashlib import md5
from datetime import datetime as dt, date, timedelta
from functools import wraps, partial
from json import loads, dumps
from ast import literal_eval
from os import path, listdir
from inspect import isclass, getmembers
from importlib import import_module
from http.client import responses
from urllib.parse import urlencode, quote
from time import gmtime
from subprocess import call

from dateutil.relativedelta import relativedelta
from flask import has_request_context, request, make_response
from meza import convert as cv, fntools as ft
from sqlalchemy import event
from sqlalchemy.inspection import inspect as sqlalchemy_inspect


import inflect

__version__ = "0.0.3"

__title__ = "nerevu-api-utils"
__author__ = "Reuben Cummings"
__description__ = "Flask API utility library"
__email__ = "reubano@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Reuben Cummings"


# https://alembic.sqlalchemy.org/en/latest/batch.html#dropping-unnamed-or-named-foreign-key-constraints
# https://github.com/sqlalchemy/sqlalchemy/issues/4784
def auto_constraint_name(constraint, table):
    unnamed = constraint.name is None or constraint.name == "_unnamed_"
    return f"sa_autoname_{str(uuid4())[:5]}" if unnamed else constraint.name


CASCADE = "save-update, merge, refresh-expire, expunge"
FK_KWARGS = {"onupdate": "CASCADE", "ondelete": "SET NULL"}
DAYS_PER_MONTH = 30
DAYS_PER_YEAR = 365
ENCODING = "utf-8"

SQLALCHEMY_NAMING_CONVENTION = {
    "auto_constraint_name": auto_constraint_name,
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
}

MIMETYPES = [
    "application/json",
    "application/xml",
    "text/html",
    "text/xml",
    "text/css",
    "image/jpg",
]

get_hash = lambda text: md5(str(text).encode(ENCODING)).hexdigest()
p = inflect.engine()
singularize = p.singular_noun


def get_seconds(seconds=0, months=0, years=0, **kwargs):
    seconds = timedelta(seconds=seconds, **kwargs).total_seconds()

    if months:
        seconds += timedelta(DAYS_PER_MONTH).total_seconds() * months

    if years:
        seconds += timedelta(DAYS_PER_YEAR).total_seconds() * years

    return int(seconds)


# http://flask.pocoo.org/snippets/45/
def get_mimetype(request):
    best = request.accept_mimetypes.best_match(MIMETYPES)
    mimetype = "text/html"

    if best and request.accept_mimetypes[best] > request.accept_mimetypes["text/html"]:
        mimetype = best

    return mimetype


def make_cache_key(*args, cache_query=False, cache_mimetype=False, path=None, **kwargs):
    """Creates a memcache key for a url and its query parameters

    Returns:
        (str): cache key
    """
    try:
        base_path, query_string = (path or request.full_path).split("?")
    except ValueError:
        base_path, query_string = (path or request.path), ""

    cache_key = base_path.rstrip("/") or "/"

    if cache_query and query_string:
        cache_key += f":{get_hash(query_string)}"

    if cache_mimetype:
        cache_key += f":{get_mimetype(request)}"

    return cache_key


def delete_cache(cache, cache_key=None, clear=False, **kwargs):
    if cache_key or (has_request_context() and not clear):
        cache_key = cache_key or make_cache_key(**kwargs)

        if len(cache_key.split(":")) == 2:
            # remove all downstream keys since they are also stale, e.g., all pages of
            # a paginated route
            cache_key = None

    cache.delete(cache_key) if cache_key else cache.clear()
    return f"Deleted cache for {cache_key}!" if cache_key else "All caches cleared!"


# https://gist.github.com/glenrobertson/954da3acec84606885f5
# http://stackoverflow.com/a/23115561/408556
# https://github.com/pallets/flask/issues/637
def cache_header(cache, max_age, versioned=False, refresh_period=0, **ckwargs):
    """
    Add Flask cache response headers based on max_age in seconds.

    If max_age is 0, caching will be disabled.
    Otherwise, caching headers are set to expire in now + max_age seconds

    Example usage:

    @app.route('/map')
    @cache_header(cache, 60)
    def index():
        return render_template('index.html')

    """

    def decorator(view):
        _max_age = get_seconds(years=1) if (max_age and versioned) else max_age
        f = cache.cached(_max_age, **ckwargs)(view)

        @wraps(f)
        def wrapper(*args, **wkwargs):
            response = f(*args, **wkwargs)
            response.cache_control.max_age = _max_age
            response.cache_control.s_maxage = get_seconds(years=1)

            if versioned:
                response.cache_control.immutable = True
            else:
                # because some browsers don't respect the spec and treat no-cache like
                # it was no-store (I'm looking at you chrome!)
                response.cache_control.must_revalidate = True

            if _max_age and request.method == "GET":
                extra = timedelta(seconds=_max_age)
                response.expires = (response.last_modified or dt.utcnow()) + extra
                response.cache_control.public = True
                response.add_etag()

                if refresh_period:
                    # TODO: set stale-while-revalidate and stale-if-error
                    pass
            else:
                response = _uncache_header(response)

            return response.make_conditional(request)

        return wrapper

    return decorator


def _uncache_header(response):
    """
    Removes Flask cache response headers
    """
    response.cache_control.no_store = True
    response.cache_control.max_age = 0
    response.cache_control.public = False
    response.headers["Pragma"] = "no-cache"
    response.expires = response.last_modified or dt.utcnow()
    return response


def uncache_header(cache, response):
    delete_cache(cache)
    _uncache_header(response)


def title_case(text):
    text_words = text.split(" ")
    return " ".join(
        [
            (lambda word: f"{word[0].upper()}{word[1:].lower()}")(word)
            for word in text_words
        ]
    )


def parse(string):
    """Parses a string into an equivalent Python object

    Args:
        string (str): The string to parse

    Returns:
        (obj): equivalent Python object

    Examples:
        >>> parse('True')
        True
        >>> parse('{"key": "value"}')
        {'key': 'value'}
    """
    if string.lower() in {"true", "false"}:
        parsed = loads(string.lower())
    else:
        try:
            parsed = literal_eval(string)
        except (ValueError, SyntaxError):
            parsed = string

    return parsed


def gen_models(model_file="models", model_dir=None):
    def filterer(file_name):
        py = file_name.endswith("py")
        pyc = file_name.endswith("pyc")
        return py and not (pyc or file_name.startswith("_"))

    if model_dir:
        modules = [fn for fn in listdir(model_dir) if filterer(fn)]
        models = [f"app.models.{path.splitext(x)[0]}" for x in modules]
    else:
        models = [f"app.{model_file}"]

    for x in models:
        yield import_module(x)


def gen_tables(models):
    for model in models:
        for name, table in getmembers(model, isclass):
            if hasattr(table, "__tablename__"):
                yield table


def get_table(tables, tablename, singularize=False):
    if singularize:
        tablename = p.singular_noun(tablename)

    try:
        table = next(t for t in tables if t.__tablename__ == tablename)
    except StopIteration:
        table = None

    return table


def get_col_type(col, table):
    return str(getattr(table, col).type)


def gen_independent_tables(tables, **kwargs):
    for table in tables:
        has_dependent_cols = any(gen_dependent_cols(table, **kwargs))
        has_relationships = any(gen_relationships(table, **kwargs))

        if not (has_dependent_cols or has_relationships):
            yield table


def gen_dependent_tables(tables, dependency, seen=None, **kwargs):
    seen = set(seen or [])
    dependency_name = dependency.__tablename__
    seen.add(dependency_name)

    for table in tables:
        tablename = table.__tablename__

        if tablename in seen:
            continue

        dependent_cols = set(gen_dependent_cols(table, **kwargs))

        if len(dependent_cols) == 2 and not table.id:
            # it's an association proxy table
            continue

        relationship_cols = {
            p.singular_noun(r) for r in gen_relationships(table, **kwargs)
        }
        all_dependent_cols = dependent_cols.union(relationship_cols)
        is_dependent = dependency_name in all_dependent_cols
        all_dependencies_met = all_dependent_cols.issubset(seen)

        if is_dependent and all_dependencies_met:
            yield table
            yield from gen_dependent_tables(tables, table, seen=seen, **kwargs)


def gen_association_tables(tables, **kwargs):
    for table in tables:
        dependent_cols = list(gen_dependent_cols(table, **kwargs))

        if len(dependent_cols) == 2:
            yield table


def gen_cols(table, excluded_cols=None):
    excluded_cols = set(excluded_cols or [])

    for col in table._sav_column_names():
        if col not in excluded_cols:
            if col.endswith("_id"):
                yield col.rsplit("_id", 1)[0]
            else:
                yield col


def gen_independent_cols(table, excluded_cols=None):
    excluded_cols = set(excluded_cols or [])

    for col in table._sav_column_names():
        if col in excluded_cols:
            continue
        elif not col.endswith("_id"):
            yield col


def gen_dependent_cols(table, excluded_cols=None):
    excluded_cols = set(excluded_cols or [])

    for col in table._sav_column_names():
        if col in excluded_cols:
            continue
        elif col.endswith("_id"):
            yield col.rsplit("_id", 1)[0]


def gen_relationships(table, **kwargs):
    mapper = sqlalchemy_inspect(table)
    columns = set(gen_cols(table, **kwargs))

    for key, value in mapper.relationships.items():
        if value.backref and key not in columns:
            yield key


def gen_from_independent_tables(tables, independent_tables, **kwargs):
    for dependency in independent_tables:
        yield from gen_dependent_tables(tables, dependency, **kwargs)


def get_all_tables(tables, **kwargs):
    _independent_tables = gen_independent_tables(tables, **kwargs)
    association_tables = list(gen_association_tables(tables, **kwargs))
    independent_tables = [t for t in _independent_tables if t not in association_tables]
    independent_table_names = set(t.__tablename__ for t in independent_tables)
    _gen_tables = partial(
        gen_from_independent_tables, tables, seen=independent_table_names
    )
    dependent_tables = list(_gen_tables(independent_tables))
    all_tables = independent_tables + dependent_tables

    return {
        "independent_tables": independent_tables,
        "dependent_tables": dependent_tables,
        "non_association_tables": [
            t for t in all_tables if t not in association_tables
        ],
        "association_tables": association_tables,
        "all_tables": all_tables,
    }


def trim_entry(target, value, oldvalue, initiator):
    """Prevent the insertion of whitespace chars"""
    return value.strip() if value else None


def add_listener(listener, *args, field="name", etype="set"):
    for table in args:
        try:
            column = getattr(table, field)
        except AttributeError:
            pass
        else:
            retval = etype in {"set"}
            event.listen(column, etype, listener, retval=retval)


def configure(flask_config, config, **kwargs):
    if kwargs.get("config_file"):
        flask_config.from_pyfile(kwargs["config_file"])
    elif kwargs.get("config_envvar"):
        flask_config.from_envvar(kwargs["config_envvar"])
    elif kwargs.get("config_mode"):
        obj = getattr(config, kwargs["config_mode"])
        flask_config.from_object(obj)
    else:
        flask_config.from_envvar("APP_SETTINGS", silent=True)


def responsify(mimetype, status_code=200, indent=2, sort_keys=True, **kwargs):
    """Creates a jsonified response. Necessary because the default
    flask.jsonify doesn't correctly handle sets, dates, or iterators

    Args:
        status_code (int): The status code (default: 200).
        indent (int): Number of spaces to indent (default: 2).
        sort_keys (bool): Sort response dict by keys (default: True).
        kwargs (dict): The response to jsonify.

    Returns:
        (obj): Flask response
    """
    encoding = kwargs.get("encoding", ENCODING)
    options = {"indent": indent, "sort_keys": sort_keys, "ensure_ascii": False}
    kwargs["status"] = responses[status_code]

    if mimetype.endswith("json"):
        content = dumps(kwargs, cls=ft.CustomEncoder, **options)
    elif mimetype.endswith("csv") and kwargs.get("result"):
        content = cv.records2csv(kwargs["result"]).getvalue()
    else:
        content = ""

    resp = (content, status_code)
    response = make_response(resp)
    response.headers["Content-Type"] = f"{mimetype}; charset={encoding}"
    response.headers.mimetype = mimetype
    response.last_modified = dt.utcnow()
    response.add_etag()
    return response


jsonify = partial(responsify, "application/json")


def fmt_elapsed(elapsed):
    """Generates a human readable representation of elapsed time.

    Args:
        elapsed (float): Number of elapsed seconds.

    Yields:
        (str): Elapsed time value and unit

    Examples:
        >>> formatted = fmt_elapsed(1000)
        >>> formatted.next()
        u'16 minutes'
        >>> formatted.next()
        u'40 seconds'
    """
    # http://stackoverflow.com/a/11157649/408556
    # http://stackoverflow.com/a/25823885/408556
    attrs = ["years", "months", "days", "hours", "minutes", "seconds"]
    delta = relativedelta(seconds=elapsed)

    for attr in attrs:
        value = getattr(delta, attr)

        if value:
            rounded = round(value, 0)
            yield "%d %s" % (rounded, attr[:-1] if rounded == 1 else attr)


def parse_kwargs(app, whitelist=None):
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    whitelist = set(whitelist or [])

    with app.app_context():
        for k, v in app.config.items():
            if k in whitelist:
                kwargs.setdefault(k.lower(), v)

    return kwargs


def fetch_bool(message, voice_over=False):
    if voice_over:
        call(["say", "enter a value"])

    valid = False

    while not valid:
        answer = input(f"{message} [y/N]: ") or "n"

        try:
            valid = answer.lower() in {"y", "n"}
        except AttributeError:
            pass
            # logger.error(f"Invalid selection: {answer}.")

    return answer


def strip_slash(path, **kwargs):
    stripped = path.rstrip("/") or "/"

    if kwargs:
        stripped += f"?{urlencode(kwargs, quote_via=quote)}"

    return stripped


EPOCH = dt(*gmtime(0)[:6])
HEADERS = {"Accept": "application/json"}

COMMON_ROUTES = {
    ("v1", "GET"): "home",
    ("ipsum", "GET"): "ipsum",
    ("memoization", "GET"): "memoize",
    ("memoization", "DELETE"): "reset",
}

AUTH_ROUTES = {
    ("auth", "GET"): "authenticate",
    ("auth", "DELETE"): "revoke",
    ("refresh", "GET"): "refresh",
    ("status", "GET"): "status",
}

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)


def get_common_rel(resourceName, method):
    key = (resourceName, method)
    return COMMON_ROUTES.get(key, AUTH_ROUTES.get(key))


def get_resource_name(rule):
    """Returns resourceName from endpoint

    Args:
        rule (str): the endpoint path (e.g. '/v1/data')

    Returns:
        (str): the resource name

    Examples:
        >>> rule = '/v1/data'
        >>> get_resource_name(rule)
        'data'
    """
    url_path_list = [p for p in rule.split("/") if p]
    return url_path_list[:2].pop()


def get_params(rule):
    """Returns params from the url

    Args:
        rule (str): the endpoint path (e.g. '/v1/data/<int:id>')

    Returns:
        (list): parameters from the endpoint path

    Examples:
        >>> rule = '/v1/random_resource/<string:path>/<status_type>'
        >>> get_params(rule)
        ['path', 'status_type']
    """
    # param regexes
    param_with_colon = r"<.+?:(.+?)>"
    param_no_colon = r"<(.+?)>"
    either_param = param_with_colon + r"|" + param_no_colon

    parameter_matches = re.findall(either_param, rule)
    return ["".join(match_tuple) for match_tuple in parameter_matches]


def get_rel(href, method, rule):
    """Returns the `rel` of an endpoint (see `Returns` below).

    If the rule is a common rule as specified in the utils.py file, then that rel is
    returned.

    If the current url is the same as the href for the current route, `self` is
    returned.

    Args:
        href (str): the full url of the endpoint (e.g. https://alegna-api.nerevu.com/v1/data)
        method (str): an HTTP method (e.g. 'GET' or 'DELETE')
        rule (str): the endpoint path (e.g. '/v1/data/<int:id>')

    Returns:
        rel (str): a string representing what the endpoint does

    Examples:
        >>> href = 'https://alegna-api.nerevu.com/v1/data'
        >>> method = 'GET'
        >>> rule = '/v1/data'
        >>> get_rel(href, method, rule)
        'data'

        >>> method = 'DELETE'
        >>> get_rel(href, method, rule)
        'data_delete'

        >>> method = 'GET'
        >>> href = 'https://alegna-api.nerevu.com/v1'
        >>> rule = '/v1
        >>> get_rel(href, method, rule)
        'home'
    """
    if href == request.url and method == request.method:
        rel = "self"
    else:
        # check if route is a common route
        resourceName = get_resource_name(rule)
        rel = get_common_rel(resourceName, method)

        # add the method if not common or GET
        if not rel:
            rel = resourceName
            if method != "GET":
                rel = f"{rel}_{method.lower()}"

        # get params and add to rel
        params = get_params(rule)
        if params:
            joined_params = "_".join(params)
            rel = f"{rel}_{joined_params}"

    return rel


def get_url_root():
    return request.url_root.rstrip("/")


def get_request_base():
    return request.base_url.split("/")[-1]


def gen_links(rules):
    """Makes a generator of all endpoints, their methods,
    and their rels (strings representing purpose of the endpoint)

    Yields:
        (dict): Example - {"rel": "data", "href": f"https://alegna-api.nerevu.com/v1/data", "method": "GET"}
    """
    url_root = get_url_root()

    for r in rules:
        if "static" not in r.rule and "callback" not in r.rule and r.rule != "/":
            for method in r.methods - {"HEAD", "OPTIONS"}:
                href = f"{url_root}{r.rule}".rstrip("/")
                rel = get_rel(href, method, r.rule)
                yield {"rel": rel, "href": href, "method": method}


def get_links(rules):
    """Sorts endpoint links alphabetically by their href"""
    links = gen_links(rules)
    return sorted(links, key=lambda link: link["href"])
