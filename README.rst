logging_subprocess
==================

Variant of subprocess.call that accepts a logger instead of stdout/stderr,
and logs stdout messages via logger.debug and stderr messages via
logger.error.


Usage
-----

.. code-block:: pycon

    >>> import logging_subprocess
    >>> logging_subprocess.call(['ls'])

Credit
------

I found this as a gist_, and it is cool.

.. _gist: https://gist.github.com/hangtwenty/6390750