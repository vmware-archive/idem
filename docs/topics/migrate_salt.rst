===========================
Migrating Support From Salt
===========================

Idem is not too far from Salt States. Idem extends Salt State functionality
though, and uses slightly different underlying interfaces. for instance, Idem
does not use `__salt__` or any of the dunder constructs, all of this
information is now on the hub. But migration is intended to be easy!

Exec Modules and State Modules
==============================

Idem follows the same constructs as Salt in seperating execution
functionality from idempotent enforcement into two seperate subsystems.
The idea is that these are seperate concerns and that raw execution
presents value in itself making the code more reusable.

salt/modules to exec
--------------------

Modules inside of `salt/modules` should be implemented as
`exec` modules in Idem. References on the hub should be changed from
`__salt__['test.ping']` to references on the hub, like
`hub.exec.test.ping`.

salt/states to states
---------------------

Modules inside of `salt/states` should be implemented as `states`
modules in Idem. References on the hub should be changed from
`__states__['pkg.installed']` to `hub.states.pkg.installed`.

salt/utils to exec
------------------

Many Salt modules use functions inside of utils. This grew in Salt out
of limitations from the salt loader and how shared code was originally
developed.

For Idem anything that is in utils should be moved into `exec`. This makes
those functions generally available for everything else on the hub which
solves the problem that created the utils system in Salt to begin with.

Namespaces
==========

Unlike Salt's loader, POP allows for nested plugin subsystems. Idem
recursively loads all lower subsystems for `exec` and `states` subsystems.

This means that you can move `exec` and `states` plugins into subdirectories!
So when porting a module called `salt/modules/boto_s3.py` it could be ported
to `exec/boto/s3.py`, or it could be ported to `exec/aws/s3.py` or
`exec/aws/storage/s3.py`. The location of the file reflects the location
on the hub, so these locations get referenced on the hub as `hub.exec.boto.s3`,
`hub.exec.aws.s3`, `hub.exec.aws.storage.s3` respectively.

Exec Function Calls
===================

All function calls now need to accept the hub as the first argument. Functions
should also be changed to be async functions where appropriate. So this
`exec` function signature:

.. code-block:: python

    def upload_file(
        source,
        name,
        extra_args=None,
        region=None,
        key=None,
        keyid=None,
        profile=None,
        ):

Gets changed to look like this:

.. code-block:: python

    async def upload_file(
        hub,
        source,
        name,
        extra_args=None,
        region=None,
        key=None,
        keyid=None,
        profile=None,
        ):

States Function Calls
=====================

States function calls now accept a `ctx` argument. This allows us to send
an execution context into the function. The `ctx` is a dict with the keys
`test` and `run_name`. The `test` value is a boolean telling the state if it
is running is test mode. The `run_name` is the name of the run as it is stored
on the hub, using the `run_name` you can gain access to the internal tracking
data for the execution of the Idem run located in `hub.idem.RUNS[ctx['run_name']]`.

So a state function signature that looks like this in Salt:

.. code-block:: python

    def object_present(
        name,
        source=None,
        hash_type=None,
        extra_args=None,
        extra_args_from_pillar='boto_s3_object_extra_args',
        region=None,
        key=None,
        keyid=None,
        profile=None):

Will look like this in Idem:

.. code-block:: python

    async def object_present(
        hub,
        ctx,
        name,
        source=None,
        hash_type=None,
        extra_args=None,
        extra_args_from_pillar='boto_s3_object_extra_args',
        region=None,
        key=None,
        keyid=None,
        profile=None):

Full Function Example
=====================

This example takes everything into account given a state function before and
after. Doc strings are omitted for brevity but should be preserved.

Salt Function
-------------

.. code-block:: python

	def object_present(
	    name,
	    source=None,
	    hash_type=None,
	    extra_args=None,
	    extra_args_from_pillar='boto_s3_object_extra_args',
	    region=None,
	    key=None,
	    keyid=None,
	    profile=None,
	):
	    ret = {
		'name': name,
		'comment': '',
		'changes': {},
	    }

	    if extra_args is None:
		extra_args = {}
	    combined_extra_args = copy.deepcopy(
		__salt__['config.option'](extra_args_from_pillar, {})
	    )
	    __utils__['dictupdate.update'](combined_extra_args, extra_args)
	    if combined_extra_args:
		supported_args = STORED_EXTRA_ARGS | UPLOAD_ONLY_EXTRA_ARGS
		combined_extra_args_keys = frozenset(six.iterkeys(combined_extra_args))
		extra_keys = combined_extra_args_keys - supported_args
		if extra_keys:
		    msg = 'extra_args keys {0} are not supported'.format(extra_keys)
		    return {'error': msg}

	    # Get the hash of the local file
	    if not hash_type:
		hash_type = __opts__['hash_type']
	    try:
		digest = salt.utils.hashutils.get_hash(source, form=hash_type)
	    except IOError as e:
		ret['result'] = False
		ret['comment'] = "Could not read local file {0}: {1}".format(
		    source,
		    e,
		)
		return ret
	    except ValueError as e:
		# Invalid hash type exception from get_hash
		ret['result'] = False
		ret['comment'] = 'Could not hash local file {0}: {1}'.format(
		    source,
		    e,
		)
		return ret

	    HASH_METADATA_KEY = 'salt_managed_content_hash'
	    combined_extra_args.setdefault('Metadata', {})
	    if HASH_METADATA_KEY in combined_extra_args['Metadata']:
		# Be lenient, silently allow hash metadata key if digest value matches
		if combined_extra_args['Metadata'][HASH_METADATA_KEY] != digest:
		    ret['result'] = False
		    ret['comment'] = (
			'Salt uses the {0} metadata key internally,'
			'do not pass it to the boto_s3.object_present state.'
		    ).format(HASH_METADATA_KEY)
		    return ret
	    combined_extra_args['Metadata'][HASH_METADATA_KEY] = digest
	    # Remove upload-only keys from full set of extra_args
	    # to create desired dict for comparisons
	    desired_metadata = dict(
		(k, v) for k, v in six.iteritems(combined_extra_args)
		if k not in UPLOAD_ONLY_EXTRA_ARGS
	    )

	    # Some args (SSE-C, RequestPayer) must also be passed to get_metadata
	    metadata_extra_args = dict(
		(k, v) for k, v in six.iteritems(combined_extra_args)
		if k in GET_METADATA_EXTRA_ARGS
	    )
	    r = __salt__['boto_s3.get_object_metadata'](
		name,
		extra_args=metadata_extra_args,
		region=region,
		key=key,
		keyid=keyid,
		profile=profile,
	    )
	    if 'error' in r:
		ret['result'] = False
		ret['comment'] = 'Failed to check if S3 object exists: {0}.'.format(
		    r['error'],
		)
		return ret

	    if r['result']:
		# Check if content and metadata match
		# A hash of the content is injected into the metadata,
		# so we can combine both checks into one
		# Only check metadata keys specified by the user,
		# ignore other fields that have been set
		s3_metadata = dict(
		    (k, r['result'][k]) for k in STORED_EXTRA_ARGS
		    if k in desired_metadata and k in r['result']
		)
		if s3_metadata == desired_metadata:
		    ret['result'] = True
		    ret['comment'] = 'S3 object {0} is present.'.format(name)
		    return ret
		action = 'update'
	    else:
		s3_metadata = None
		action = 'create'

	    def _yaml_safe_dump(attrs):
		'''
		Safely dump YAML using a readable flow style
		'''
		dumper_name = 'IndentedSafeOrderedDumper'
		dumper = __utils__['yaml.get_dumper'](dumper_name)
		return __utils__['yaml.dump'](
		    attrs,
		    default_flow_style=False,
		    Dumper=dumper)

	    changes_diff = ''.join(difflib.unified_diff(
		_yaml_safe_dump(s3_metadata).splitlines(True),
		_yaml_safe_dump(desired_metadata).splitlines(True),
	    ))

	    if __opts__['test']:
		ret['result'] = None
		ret['comment'] = 'S3 object {0} set to be {1}d.'.format(name, action)
		ret['comment'] += '\nChanges:\n{0}'.format(changes_diff)
		ret['changes'] = {'diff': changes_diff}
		return ret

	    r = __salt__['boto_s3.upload_file'](
		source,
		name,
		extra_args=combined_extra_args,
		region=region,
		key=key,
		keyid=keyid,
		profile=profile,
	    )

	    if 'error' in r:
		ret['result'] = False
		ret['comment'] = 'Failed to {0} S3 object: {1}.'.format(
		    action,
		    r['error'],
		)
		return ret

	    ret['result'] = True
	    ret['comment'] = 'S3 object {0} {1}d.'.format(name, action)
	    ret['comment'] += '\nChanges:\n{0}'.format(changes_diff)
	    ret['changes'] = {'diff': changes_diff}
	    return ret

Idem State Function
-------------------

.. code-block:: python

    async def object_present(
        hub,
        ctx,
        name,
        source=None,
        hash_type=None,
        extra_args=None,
        region=None,
        key=None,
        keyid=None,
        profile=None):
        ret = {
            'name': name,
            'comment': '',
            'changes': {},
        }

        if extra_args is None:
            extra_args = {}
        # Pull out args for pillar

        # Get the hash of the local file
        if not hash_type:
            hash_type = hub.OPT['idem']['hash_type']  # Pull opts from hub.OPT
        try:
            # Some functions from utils will need to be ported over. Some general
            # Use functions should be sent upstream to be included in Idem.
            digest = hub.exec.utils.hashutils.get_hash(source, form=hash_type)
        except IOError as e:
            ret['result'] = False
            # Idem requires Python 3.6 and higher, use f-strings
            ret['comment'] = f'Could not read local file {source}: {e}'
            return ret
        except ValueError as e:
            # Invalid hash type exception from get_hash
            ret['result'] = False
            ret['comment'] = f'Could not hash local file {source}: {e}'
            return ret

        HASH_METADATA_KEY = 'idem_managed_content_hash'  # Change salt refs to idem
        combined_extra_args.setdefault('Metadata', {})
        if HASH_METADATA_KEY in combined_extra_args['Metadata']:
            # Be lenient, silently allow hash metadata key if digest value matches
            if combined_extra_args['Metadata'][HASH_METADATA_KEY] != digest:
                ret['result'] = False
                ret['comment'] = (
                    f'Salt uses the {HASH_METADATA_KEY} metadata key internally,'
                    'do not pass it to the boto_s3.object_present state.'
                return ret
        combined_extra_args['Metadata'][HASH_METADATA_KEY] = digest
        # Remove upload-only keys from full set of extra_args
        # to create desired dict for comparisons
        desired_metadata = dict(
            (k, v) for k, v in combined_extra_args.items()  # No need to six anymore
            if k not in UPLOAD_ONLY_EXTRA_ARGS
        )

        # Some args (SSE-C, RequestPayer) must also be passed to get_metadata
        metadata_extra_args = dict(
            (k, v) for k, v in combined_extra_args.items()  # No need for six anymore
            if k in GET_METADATA_EXTRA_ARGS
        )
        r = await hub.exec.boto.s3.get_object_metadata(
            name,
            extra_args=metadata_extra_args,
            region=region,
            key=key,
            keyid=keyid,
            profile=profile,
        )
        if 'error' in r:
            ret['result'] = False
            ret['comment'] = f'Failed to check if S3 object exists: {r["error"]}.' # Use fstrings
            return ret

        if r['result']:
            # Check if content and metadata match
            # A hash of the content is injected into the metadata,
            # so we can combine both checks into one
            # Only check metadata keys specified by the user,
            # ignore other fields that have been set
            s3_metadata = dict(
                (k, r['result'][k]) for k in STORED_EXTRA_ARGS
                if k in desired_metadata and k in r['result']
            )
            if s3_metadata == desired_metadata:
                ret['result'] = True
                ret['comment'] = f'S3 object {name} is present.'
                return ret
            action = 'update'
        else:
            s3_metadata = None
            action = 'create'

        # Some Salt code goes out of its way to use salt libs, often it
        # is more appropriate to just call the supporting lib directly
        changes_diff = ''.join(difflib.unified_diff(
            yaml.dump(s3_metadata, default_flow_style=False).splitlines(True),
            yaml.dump(desired_metadata, default_flow_style=False).splitlines(True),
        ))

        if ctx['test']:
            ret['result'] = None
            ret['comment'] = f'S3 object {name} set to be {action}d.'
            ret['comment'] += f'\nChanges:\n{changes_diff}'
            ret['changes'] = {'diff': changes_diff}
            return ret

        r = await hub.boto.s3.upload_file(
            source,
            name,
            extra_args=combined_extra_args,
            region=region,
            key=key,
            keyid=keyid,
            profile=profile,
        )

        if 'error' in r:
            ret['result'] = False
            ret['comment'] = f'Failed to {action} S3 object: {r["error"]}.'
            return ret

        ret['result'] = True
        ret['comment'] = f'S3 object {name} {action}d.'
        ret['comment'] += f'\nChanges:\n{changes_diff}'
        ret['changes'] = {'diff': changes_diff}
        return ret
