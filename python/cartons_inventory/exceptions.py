# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class Cartons_inventoryError(Exception):
    """A custom core Cartons_inventory exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(Cartons_inventoryError, self).__init__(message)


class Cartons_inventoryNotImplemented(Cartons_inventoryError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(Cartons_inventoryNotImplemented, self).__init__(message)


class Cartons_inventoryAPIError(Cartons_inventoryError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from Cartons_inventory API'
        else:
            message = 'Http response error from Cartons_inventory API. {0}'.format(message)

        super(Cartons_inventoryAPIError, self).__init__(message)


class Cartons_inventoryApiAuthError(Cartons_inventoryAPIError):
    """A custom exception for API authentication errors"""
    pass


class Cartons_inventoryMissingDependency(Cartons_inventoryError):
    """A custom exception for missing dependencies."""
    pass


class Cartons_inventoryWarning(Warning):
    """Base warning for Cartons_inventory."""


class Cartons_inventoryUserWarning(UserWarning, Cartons_inventoryWarning):
    """The primary warning class."""
    pass


class Cartons_inventorySkippedTestWarning(Cartons_inventoryUserWarning):
    """A warning for when a test is skipped."""
    pass


class Cartons_inventoryDeprecationWarning(Cartons_inventoryUserWarning):
    """A warning for deprecated features."""
    pass
