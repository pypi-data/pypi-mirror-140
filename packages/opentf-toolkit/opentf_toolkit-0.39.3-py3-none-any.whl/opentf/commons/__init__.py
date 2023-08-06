# Copyright (c) 2021 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helpers for squash tf"""

from typing import Any, Dict, Iterable, List, Optional, Tuple

import argparse
import itertools
import logging
import json
import os
import sys

from datetime import datetime
from logging.config import dictConfig
from uuid import uuid4

import jwt
import yaml

from flask import Flask, make_response, request, Response
from jsonschema import validate, ValidationError

import requests

from toposort import toposort, CircularDependencyError

import opentf.schemas


########################################################################
# Constants

SUBSCRIPTION = 'opentestfactory.org/v1alpha1/Subscription'
SERVICECONFIG = 'opentestfactory.org/v1alpha1/ServiceConfig'
PROVIDERCONFIG = 'opentestfactory.org/v1alpha1/ProviderConfig'

WORKFLOW = 'opentestfactory.org/v1alpha1/Workflow'
WORKFLOWCOMPLETED = 'opentestfactory.org/v1alpha1/WorkflowCompleted'
WORKFLOWCANCELED = 'opentestfactory.org/v1alpha1/WorkflowCanceled'
WORKFLOWRESULT = 'opentestfactory.org/v1alpha1/WorkflowResult'

GENERATORCOMMAND = 'opentestfactory.org/v1alpha1/GeneratorCommand'
GENERATORRESULT = 'opentestfactory.org/v1alpha1/GeneratorResult'

PROVIDERCOMMAND = 'opentestfactory.org/v1alpha1/ProviderCommand'
PROVIDERRESULT = 'opentestfactory.org/v1alpha1/ProviderResult'

EXECUTIONCOMMAND = 'opentestfactory.org/v1alpha1/ExecutionCommand'
EXECUTIONRESULT = 'opentestfactory.org/v1alpha1/ExecutionResult'
EXECUTIONERROR = 'opentestfactory.org/v1alpha1/ExecutionError'

AGENTREGISTRATION = 'opentestfactory.org/v1alpha1/AgentRegistration'

NOTIFICATION = 'opentestfactory.org/v1alpha1/Notification'

DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Strict-Transport-Security': 'max-age=31536000; includeSubdomains',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
    'Content-Security-Policy': 'default-src \'none\'',
}

DEFAULT_CONTEXT = {
    'host': '127.0.0.1',
    'port': 443,
    'ssl_context': 'adhoc',
    'eventbus': {'endpoint': 'https://127.0.0.1:38368', 'token': 'invalid-token'},
}

REASON_STATUS = {
    'OK': 200,
    'Created': 201,
    'NoContent': 204,
    'BadRequest': 400,
    'Unauthorized': 401,
    'PaymentRequired': 402,
    'Forbidden': 403,
    'NotFound': 404,
    'AlreadyExists': 409,
    'Conflict': 409,
    'Invalid': 422,
}

ALLOWED_ALGORITHMS = [
    'ES256',  # ECDSA signature algorithm using SHA-256 hash algorithm
    'ES384',  # ECDSA signature algorithm using SHA-384 hash algorithm
    'ES512',  # ECDSA signature algorithm using SHA-512 hash algorithm
    'RS256',  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-256 hash algorithm
    'RS384',  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-384 hash algorithm
    'RS512',  # RSASSA-PKCS1-v1_5 signature algorithm using SHA-512 hash algorithm
    'PS256',  # RSASSA-PSS signature using SHA-256 and MGF1 padding with SHA-256
    'PS384',  # RSASSA-PSS signature using SHA-384 and MGF1 padding with SHA-384
    'PS512',  # RSASSA-PSS signature using SHA-512 and MGF1 padding with SHA-512
]

########################################################################
# Config Helpers


class ConfigError(Exception):
    """Invalid configuration file."""


def _add_securityheaders(resp):
    """Add DEFAULT_HEADERS to response."""
    for header, value in DEFAULT_HEADERS.items():
        resp.headers[header] = value
    return resp


def _make_authenticator(context):
    """Return an authenticator function tied to context."""

    def inner():
        """Ensure the incoming request is authenticated.

        If from localhost, allow.

        If from somewhere else, ensure there is a valid token attached.
        """
        if context['enable_insecure_login']:
            if request.remote_addr == context['insecure_bind_address']:
                return None
        authz = request.headers.get('Authorization')
        if authz is None:
            return make_status_response('Unauthorized', 'No Bearer token')
        parts = authz.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            logging.error(authz)
            return make_status_response('Unauthorized', 'Invalid Authorization header')
        for i, pubkey in enumerate(context['trusted_keys']):
            try:
                jwt.decode(parts[1], pubkey, algorithms=ALLOWED_ALGORITHMS)
                logging.debug('Token signed by trusted key #%d', i)
                return None
            except jwt.InvalidAlgorithmError as err:
                logging.error('Invalid algorithm while verifying token')
                logging.error(err)
            except:
                logging.debug('Token not signed by trusted key #%d', i)
        return make_status_response('Unauthorized', 'Invalid token')

    return inner


def get_actor():
    """Get actor."""
    if token := request.headers.get('Authorization'):
        payload = jwt.decode(
            token.split()[1],
            algorithms=ALLOWED_ALGORITHMS,
            options={'verify_signature': False},
        )
        return payload.get('sub')
    return None


def run_app(app):
    """Start the app."""
    context = app.config['CONTEXT']
    ssl_enabled = context.get('ssl_context') != 'disabled'

    app.run(
        host=context['host'],
        port=context['port'],
        ssl_context=context['ssl_context'] if ssl_enabled else None,
    )


def make_app(name, description, configfile, schema=None, defaultcontext=None):
    """Create a new app.

    # Required parameters:

    - name: a string
    - description: a string
    - configfile: a string

    # Optional parameters:

    - schema: a string or None (None by default)
    - defaultcontext: a dictionary or None (None by default)

    # Returned value

    A new flask app.  Two entries are added to `app.config`: `CONTEXT`
    and `CONFIG`.

    `CONFIG` is a dictionary, the complete config file.  `CONTEXT` is a
    subset of `CONFIG`, the current entry in `CONFIG['context']`.  It is
    also a dictionary.

    # Raised Exception

    A _ConfigError_ exception is raised if the context is not found or
    if the config file is invalid.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--config', help=f'alternate config file (default to {configfile})'
    )
    parser.add_argument('--context', help='alternative context')
    parser.add_argument('--host', help='alternative host')
    parser.add_argument('--port', help='alternative port')
    parser.add_argument('--ssl_context', help='alternative ssl context')
    parser.add_argument('--trusted_authorities', help='alternative trusted authorities')
    parser.add_argument(
        '--enable_insecure_login',
        action='store_true',
        help='enable insecure login (disabled by default)',
    )
    parser.add_argument(
        '--insecure_bind_address',
        help='insecure bind address (127.0.0.1 by default)',
        default='127.0.0.1',
    )
    args = parser.parse_args()

    dictConfig(
        {
            'version': 1,
            'formatters': {
                'default': {
                    'format': f'[%(asctime)s] %(levelname)s in {name}: %(message)s',
                }
            },
            'handlers': {
                'wsgi': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default',
                }
            },
            'root': {
                'level': os.environ.get('DEBUG_LEVEL', 'INFO'),
                'handlers': ['wsgi'],
            },
        }
    )
    app = Flask(name)
    try:
        if args.config is None and not os.path.isfile(configfile):
            if args.context:
                raise ConfigError('Cannot specify a context with default configuration')
            context = defaultcontext or DEFAULT_CONTEXT
            config = {}
        else:
            with open(args.config or configfile, 'r') as cnf:
                config = yaml.safe_load(cnf)

            valid, extra = validate_schema(schema or SERVICECONFIG, config)
            if not valid:
                raise ConfigError(f'Not a valid config file: {extra}')

            context_name = args.context or config['current-context']
            contexts = [
                ctx for ctx in config['contexts'] if ctx['name'] == context_name
            ]

            if len(contexts) != 1:
                raise ConfigError(
                    'Could not find context {context_name} in config file {args.config}'
                )
            context = contexts[0]['context']
    except ConfigError as err:
        app.logger.error(err)
        raise

    if args.host:
        context['host'] = args.host
    if args.port:
        context['port'] = args.port
    if args.ssl_context:
        context['ssl_context'] = args.ssl_context
    if args.trusted_authorities:
        context['trusted_authorities'] = args.trusted_authorities.split(',')
    if args.enable_insecure_login:
        context['enable_insecure_login'] = True
    if 'enable_insecure_login' not in context:
        context['enable_insecure_login'] = False
    if 'insecure_bind_address' not in context:
        context['insecure_bind_address'] = args.insecure_bind_address

    context['trusted_keys'] = _read_key_files(context.get('trusted_authorities', []))

    app.config['CONTEXT'] = context
    app.config['CONFIG'] = config
    app.before_request(_make_authenticator(context))
    app.after_request(_add_securityheaders)
    return app


########################################################################
## Misc. internal helpers


def _read_key_files(items: Iterable[str]) -> List[str]:
    """Read a series of files.

    Items are either fully-qualified file names or fully-qualified
    directory name ending with '/*'.
    """
    files = []
    for item in items:
        if item.endswith('/*'):
            files += [
                f'{item[:-1]}{file}'
                for file in os.listdir(item[:-2])
                if not file.startswith('.')
            ]
        else:
            files.append(item)
    keys = []
    for i, keyfile in enumerate(files):
        try:
            with open(keyfile) as key:
                logging.debug('Reading trusted key #%d (%s)', i, keyfile)
                keys.append(key.read())
        except Exception as err:
            logging.error('Error while reading trusted key #%d (%s)', i, keyfile)
            logging.error(err)
    return keys


########################################################################
## Misc. helpers


def make_uuid():
    """Return a new uuid as a string."""
    return str(uuid4())


########################################################################
# JSON Schema Helpers

_schemas = {}


def get_schema(name: str) -> Dict[str, Any]:
    """Get specified schema.

    # Required parameters

    - name: a string, the schema name (its kind)

    # Returned value

    A _schema_.  A schema is a dictionary.

    # Raised exceptions

    If an error occurs while reading the schema, the initial exception
    is logged and raised again.
    """
    if name not in _schemas:
        try:
            with open(
                os.path.join(sys.modules['opentf.schemas'].__path__[0], f'{name}.json'),
                'r',
            ) as schema:
                _schemas[name] = json.loads(schema.read())
        except Exception as err:
            logging.error('Could not read schema %s: %s', name, err)
            raise
    return _schemas[name]


def validate_schema(schema, instance) -> Tuple[bool, Any]:
    """Return True if instance validates schema.

    # Required parameters

    - name: a string, the schema name (its kind)
    - instance: a dictionary

    # Returned value

    A (bool, Optional[str]) pair.  If `instance` is a valid instance of
    `schema`, returns `(True, None)`.  If not, returns `(False, error)`.

    # Raised exceptions

    If an error occurs while reading the schema, the initial exception
    is logged and raised again.
    """
    try:
        validate(schema=get_schema(schema), instance=instance)
    except ValidationError as err:
        return False, err
    return True, None


########################################################################
# API Server Helpers


def make_event(schema: str, **kwargs) -> Dict[str, Any]:
    """Return a new event dictionary.

    # Required parameters

    - schema: a string

    # Optional parameters

    A series of key=values

    # Returned value

    A dictionary.
    """
    apiVersion, kind = schema.rsplit('/', 1)
    return {'apiVersion': apiVersion, 'kind': kind, **kwargs}


def make_status_response(
    reason: str, message: str, details: Optional[Dict[str, Any]] = None
) -> Response:
    """Return a new status response object.

    # Required parameters

    - reason: a non-empty string (must exist in `REASON_STATUS`)
    - message: a string

    # Optional parameters:

    - details: a dictionary or None (None by default)

    # Returned value

    A _status_.  A status is a dictionary with the following entries:

    - kind: a string (`'Status'`)
    - apiVersion: a string (`'v1'`)
    - metadata: an empty dictionary
    - status: a string (either `'Success'` or `'Failure'`)
    - message: a string (`message`)
    - reason: a string (`reason`)
    - details: a dictionary or None (`details`)
    - code: an integer (derived from `reason`)
    """
    code = REASON_STATUS[reason]
    if code // 100 == 4:
        logging.warning(message)
    return make_response(
        {
            'kind': 'Status',
            'apiVersion': 'v1',
            'metadata': {},
            'status': 'Success' if code // 100 == 2 else 'Failure',
            'message': message,
            'reason': reason,
            'details': details,
            'code': code,
        },
        code,
    )


########################################################################
# Pipelines Helpers


def validate_pipeline(workflow):
    """Validate workflow jobs, looking for circular dependencies.

    # Required parameters

    - workflow: a dictionary

    # Returned value

    A (`bool`, extra) pair.

    If there are circular dependencies in the workflow jobs, returns
    `(False, description (a string))`.

    If there are no circular dependencies, returns `(True, jobs)` where
    `jobs` is an ordered list of job names lists.  Each item in the
    returned list is a set of jobs that can run in parallel.
    """
    try:
        jobs = {}
        for job in workflow['jobs']:
            needs = workflow['jobs'][job].get('needs')
            if needs:
                if isinstance(needs, list):
                    jobs[job] = set(needs)
                else:
                    jobs[job] = {needs}
            else:
                jobs[job] = set()
        return True, [list(items) for items in toposort(jobs)]
    except CircularDependencyError as err:
        return False, err


def get_execution_sequence(workflow):
    """Return an execution sequence for jobs.

    # Required parameters

    - workflow: a dictionary

    # Returned value

    `None` or a list of jobs names.
    """
    try:
        jobs = {}
        for job in workflow['jobs']:
            needs = workflow['jobs'][job].get('needs')
            if needs:
                if isinstance(needs, list):
                    jobs[job] = set(needs)
                else:
                    jobs[job] = {needs}
            else:
                jobs[job] = set()
        return list(itertools.chain.from_iterable(toposort(jobs)))
    except CircularDependencyError:
        return None


########################################################################
# Publishers & Subscribers Helpers


def make_subscription(
    name: str, selector: Dict[str, Any], target: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """Return a subscription manifest.

    # Required parameter

    - name: a string
    - selector: a dictionary
    - target: a string
    - context: a dictionary

    # Returned value

    A _subscription manifest_.  A subscription manifest is a dictionary
    with the following entries:

    - apiVersion: a string
    - kind: a string
    - metadata: a dictionary
    - spec: a dictionary
    """
    protocol = 'https' if context.get('ssl_context') != 'disabled' else 'http'
    hostname = context['eventbus'].get('hostname', context['host'])
    subscriber = {'endpoint': f'{protocol}://{hostname}:{context["port"]}/{target}'}
    return {
        'apiVersion': 'opentestfactory.org/v1alpha1',
        'kind': 'Subscription',
        'metadata': {'name': name, 'creationTimestamp': datetime.now().isoformat()},
        'spec': {'selector': selector, 'subscriber': subscriber},
    }


def subscribe(kind, target, app, labels=None, fields=None):
    """Subscribe on specified endpoint.

    `kind` is of form `[apiVersion/]kind`.

    # Required parameters

    - kind: a string
    - target: a string
    - app: a flask app

    # Optional parameters

    - labels: a dictionary
    - fields: a dictionary

    # Returned value

    A _uuid_ (a string).

    # Raised exceptions

    An exception is raised if the subscription failed.
    """
    if '/' in kind:
        apiVersion, kind = kind.rsplit('/', 1)
        if fields is None:
            fields = {}
        fields['apiVersion'] = apiVersion
    selector = {'matchKind': kind}
    if labels:
        selector['matchLabels'] = labels
    if fields:
        selector['matchFields'] = fields
    context = app.config['CONTEXT']
    return requests.post(
        context['eventbus']['endpoint'] + '/subscriptions',
        json=make_subscription(
            app.name, selector=selector, target=target, context=context
        ),
        headers={'Authorization': f'Bearer {context["eventbus"]["token"]}'},
        verify=not context['eventbus'].get('insecure-skip-tls-verify', False),
    ).json()['details']['uuid']


def unsubscribe(subscription_id, app):
    """Cancel specified subscription

    #  Required parameters

    - subscription_id: a string (an uuid)
    - app: a flask app

    # Returned value

    A `requests.Response` object.
    """
    context = app.config['CONTEXT']
    return requests.delete(
        context['eventbus']['endpoint'] + '/subscriptions/' + subscription_id,
        headers={'Authorization': f'Bearer {context["eventbus"]["token"]}'},
        verify=not context['eventbus'].get('insecure-skip-tls-verify', False),
    )


def publish(publication, context):
    """Publish publication on specified endpoint.

    If `publication` is a dictionary, and if it has a `metadata` entry,
    a `creationTimestamp` sub-entry will be created (or overwritten if
    it already exists).

    # Required parameters

    - publication: an object
    - context: a dictionary

    # Returned value

    A `requests.Response` object.
    """
    if isinstance(publication, dict) and 'metadata' in publication:
        publication['metadata']['creationTimestamp'] = datetime.now().isoformat()
    return requests.post(
        context['eventbus']['endpoint'] + '/publications',
        json=publication,
        headers={'Authorization': f'Bearer {context["eventbus"]["token"]}'},
        verify=not context['eventbus'].get('insecure-skip-tls-verify', False),
    )
