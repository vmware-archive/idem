==============
How Idem Works
==============

Idem works by taking input of configuration data in a renderable language. Takes
the rendered data, compiles it to a dataset called "low data" which is used to
execute the idempotent runtime.

Each phase of the process is encapsulated inside of a plugin subsystem, and each
subsystem defines a specific interface for additions.

Idem Subsystem
==============

The idem subsystem is the spine subsystem.
