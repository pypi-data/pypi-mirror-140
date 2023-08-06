#!/usr/bin/env python3
"""Kamaji Static Website Generator: Logging module
Copyright (C) 2022 Frank Abelbeck <kamaji@abelbeck.info>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
Development soundtrack:
   BBC Proms - Last Night 2019,
   Pet Shop Boys - Always on My Mind
"""

# import standard modules ("batteries included")
import logging
import sys


NAME_LOG = "Kamaji"

BASH_NORMAL     = "\x1b[0m"

BASH_BOLD       = "\x1b[1m"
BASH_FAINT      = "\x1b[2m"
BASH_ITALICS    = "\x1b[3m"
BASH_UNDERLINED = "\x1b[4m"
BASH_BLINK      = "\x1b[5m"
BASH_STROKE     = "\x1b[9m"

BASH_FG_BLACK   = "\x1b[30m"
BASH_FG_RED     = "\x1b[31m"
BASH_FG_GREEN   = "\x1b[32m"
BASH_FG_YELLOW  = "\x1b[33m"
BASH_FG_BLUE    = "\x1b[34m"
BASH_FG_MAGENTA = "\x1b[35m"

BASH_BG_BLACK   = "\x1b[40m"
BASH_BG_RED     = "\x1b[41m"
BASH_BG_GREEN   = "\x1b[42m"
BASH_BG_YELLOW  = "\x1b[43m"
BASH_BG_BLUE    = "\x1b[44m"
BASH_BG_MAGENTA = "\x1b[45m"


MAP_STR_TO_LOGLEVEL = {
	"debug": logging.DEBUG,
	"info": logging.INFO,
	"warn": logging.WARNING,
	"err": logging.ERROR,
	"crit": logging.CRITICAL
}


class ColourFormatter(logging.Formatter):
	"""Custom logging formatter, adding coloured bash output.

Source of inspiration: https://stackoverflow.com/a/56944256
"""
	FORMAT = "%(message)s"
	
	FORMATS = {
		logging.DEBUG:    BASH_FAINT + FORMAT + BASH_NORMAL,
		logging.INFO:     BASH_NORMAL + FORMAT + BASH_NORMAL,
		logging.WARNING:  BASH_FG_YELLOW + FORMAT + BASH_NORMAL,
		logging.ERROR:    BASH_FG_RED + BASH_BOLD + FORMAT + BASH_NORMAL,
		logging.CRITICAL: BASH_FG_MAGENTA + BASH_BOLD + FORMAT + BASH_NORMAL,
	}
	
	def format(self,record):
		"""Return a formatted record wrapped it a log-level dependend formatting.
"""
		return logging.Formatter(self.FORMATS[record.levelno]).format(record)


class LogFilterCounting(logging.Filter):
	"""Logging filter: count errors and warning.
"""
	def __init__(self):
		"""Constructor: initialise a counting filter instance by calling reset().
"""
		self.reset()
	
	def reset(self):
		"""Set all counters to zero.
"""
		self._numMsg = {
			logging.DEBUG: 0,
			logging.INFO: 0,
			logging.WARNING: 0,
			logging.ERROR: 0,
			logging.CRITICAL: 0
		}
	
	def filter(self,record):
		"""Log message filter function: increase the counter corresponding to the given
record's log level and always return 1.
"""
		self._numMsg[record.levelno] = self._numMsg[record.levelno] + 1
		return 1 # always pass on record
	
	def getNumLevel(self,strLevel):
		"""Return the number of messages of a given log level.

Args:
   strLevel: a string, denoting a log level like "debug", "info" or "warning".

Returns:
   A number. If an invalid log level is specified, zero is returned.
"""
		try:
			return self._numMsg[MAP_STR_TO_LOGLEVEL[strLevel]]
		except KeyError:
			return 0
	
	def getNumWarnings(self):
		"""Return the number of WARNING messages issued.
"""
		return self._numMsg[logging.WARNING]
	
	def getNumErrors(self):
		"""Return the number of ERROR messages issued.
"""
		return self._numMsg[logging.ERROR]
	
	def getNumCritical(self):
		"""Return the number of CRITICAL messages issued.
"""
		return self._numMsg[logging.CRITICAL]


class LogFilterMaxLevel(logging.Filter):
	"""Logging filter: block records below a given level.
"""
	def __init__(self,logLevel=logging.WARNING):
		"""Constructor: initialise the instance by setting the maximal permissive log level.

Args:
   logLevel: the maximal log level that is not blocked;
             every message of a level below will be dropped.
"""
		self._logLevel = logLevel
	
	def filter(self,record):
		"""Return True if record's log level is below the defined log level;
False otherwise (which will drop the message).
"""
		return record.levelno < self._logLevel


def debug(msg,*args,**kwargs):
	"""Pass-through method to the internal logger instance."""
	logging.getLogger(NAME_LOG).debug(msg,*args,**kwargs)

def info(msg,*args,**kwargs):
	"""Pass-through method to the internal logger instance."""
	logging.getLogger(NAME_LOG).info(msg,*args,**kwargs)

def warning(msg,*args,**kwargs):
	"""Pass-through method to the internal logger instance."""
	logging.getLogger(NAME_LOG).warning(msg,*args,**kwargs)

def error(msg,*args,**kwargs):
	"""Pass-through method to the internal logger instance."""
	logging.getLogger(NAME_LOG).error(msg,*args,**kwargs)

def critical(msg,*args,**kwargs):
	"""Pass-through method to the internal logger instance."""
	logging.getLogger(NAME_LOG).critical(msg,*args,**kwargs)

def setLevel(strLevel):
	"""Set the logging level.

Args:
   strLevel: a string, one of "debug", "info", "warn", "err", or "crit".
"""
	logging.getLogger(NAME_LOG).setLevel(MAP_STR_TO_LOGLEVEL[strLevel])

def getNumLevel(strLevel):
	"""Get the number of message per given logging level.

Args:
   strLevel: a string, one of "debug", "info", "warn", "err", or "crit".

Returns:
   An integer.
"""
	return logging.getLogger(NAME_LOG).filters[0].getNumLevel(strLevel)

def getNumWarnings():
	"""Get the number of warning messages.

Returns:
   An integer.
"""
	return logging.getLogger(NAME_LOG).filters[0].getNumWarnings()

def getNumErrors():
	"""Get the number of error messages.

Returns:
   An integer.
"""
	return logging.getLogger(NAME_LOG).filters[0].getNumErrors()

def getNumCritical():
	"""Get the number of critical messages.

Returns:
   An integer.
"""
	return logging.getLogger(NAME_LOG).filters[0].getNumCritical()


#
# module initialisation: configure Kamaji logger
#
# get logger for given name and add counting filter
logger = logging.getLogger(NAME_LOG)
logger.addFilter(LogFilterCounting())
# prepare custom bash formatter
formatter = ColourFormatter()
# add stream handler for stdout; ignore everything below DEBUG, filter everything above WARNING
logHandlerStdout = logging.StreamHandler(sys.stdout)
logHandlerStdout.addFilter(LogFilterMaxLevel(logging.WARNING))
logHandlerStdout.setLevel(logging.DEBUG)
logHandlerStdout.setFormatter(formatter)
logger.addHandler(logHandlerStdout)
# add stream handler for stderr; ignore everything below WARNING
logHandlerStderr = logging.StreamHandler(sys.stderr)
logHandlerStderr.setLevel(logging.WARNING)
logHandlerStderr.setFormatter(formatter)
logger.addHandler(logHandlerStderr)
# set inital logging level
logger.setLevel(logging.INFO)
