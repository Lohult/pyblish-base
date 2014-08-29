"""Entry-point of Pyblish"""

from __future__ import absolute_import

# Standard library
import logging

# Local library
import pyblish.backend.config
import pyblish.backend.plugin

log = logging.getLogger('pyblish.main')


__all__ = ['process',
           'select',
           'validate',
           'extract',
           'conform',
           'publish_all']


def process(process, context):
    """Perform process step `process` upon context `context`

    Arguments:
        process (str): Type of process to apply
        context (Context): Context upon which to appy process

    """

    assert isinstance(process, basestring)
    assert isinstance(context, pyblish.backend.plugin.Context)

    for plugin in pyblish.backend.plugin.discover(type=process):
        if not pyblish.backend.plugin.current_host() in plugin.hosts:
            continue

        for instance, error in plugin().process(context):
            yield instance, error


def process_all(process, context):
    """Convenience function of the above :meth:process"""
    for instance, error in process(process, context):
        if error is not None:
            raise error


def select(context):
    """Convenience function for selecting using all available plugins"""
    for instance, error in process('selectors', context):
        log.info("Selecting {0}".format(getattr(instance, 'name', None)))
        if error is not None:
            log.error(error)


def validate(context):
    """Convenience function for validation"""
    for instance, error in process('validators', context):
        log.info("Validating {0}".format(getattr(instance, 'name', None)))

        if error is not None:
            # Stop immediately if any validation fails
            raise error


def extract(context):
    """Convenience function for extraction"""
    for instance, error in process('extractors', context):
        log.info("Extracting {0}".format(getattr(instance, 'name', None)))

        if error is not None:
            # Continue regardless
            log.error(error)


def conform(context):
    """Perform conform upon context `context`"""
    for instance, error in process('conforms', context):
        log.info("Conforming {0}".format(getattr(instance, 'name', None)))

        if error is not None:
            # Continue regardless
            log.error(error)


def publish_all(context=None):
    """Convenience method for executing all steps in sequence

    Arguments:
        context (Context): Optional context

    """

    log.info("Publishing everything..")

    if not context:
        context = pyblish.backend.plugin.Context()

    select(context)

    if not context:
        return log.info("No instances found.")

    validate(context)  # Will raise exception at failure
    extract(context)
    conform(context)

    log.info("Finished successfully")

    return context


def validate_all(context=None):
    if not context:
        context = pyblish.backend.plugin.Context()

    select(context)
    validate(context)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
