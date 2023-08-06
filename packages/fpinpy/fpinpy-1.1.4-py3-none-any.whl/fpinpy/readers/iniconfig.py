#!/usr/bin/env python3
#
# Copyright 2022 Jonathan L. Komar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from fpinpy.result import Result
from fpinpy.collections import SinglyLinkedList
from typing import Dict, Tuple
from pathlib import Path
import configparser
import logging
logger = logging.getLogger('IniConfigReader')

class IniConfigReader():
  """Functional wrapper of imperative configparser lib
  """
  @staticmethod
  def of(config, errorMsg:str="An error occurred.") -> Result:
    """Functional (safe) factory

        Inputs:
        config: str | Path |Dict 
        errorMsg: str
    """
    return Result.of(IniConfigReader(config, errorMsg))

  def __init__(self, config:str, errorMsg:str="An error occurred."):
    """ Prefer a static function to create instances """
    if isinstance(config, str):
       self.config = self._readConfigString(config, errorMsg)
    elif isinstance(config, Path):
       self.config = self._readConfigFile(config, errorMsg)
    elif isinstance(config, Dict):
       self.config = self._readConfigDict(config, errorMsg)
    else:
       raise RuntimeError(errorMsg)

  def _readConfigDict(self, config: Dict, errorMsg: str) -> Result:
    try:
      parser = configparser.ConfigParser()
      parser.read_dict(config)
      return Result.of(parser, errorMsg=errorMsg)
    except Exception as e:
      return Result.failure(RuntimeError(f"{repr(e)}. {errorMsg}"))

  def _readConfigString(self, config:str, errorMsg:str) -> Result:
    try:
      parser = configparser.ConfigParser()
      parser.read_string(config)
      return Result.of(parser, errorMsg=errorMsg)
    except Exception as e:
      return Result.failure(RuntimeError(f"{repr(e)}. {errorMsg}"))

  def _readConfigFile(self, config:Path, errorMsg:str):
    try:
      parser = configparser.ConfigParser()
      parser.read(config)
      return Result.of(parser, errorMsg=errorMsg)
    except Exception as e:
      return Result.failure(RuntimeError(f"{repr(e)}. {errorMsg}"))

  def getProperty(self, section:str, key:str) -> Result:
    try:
      return self.config.map(lambda parser: parser.get(section, key))
    except Exception as e:
      return Result.failure("Could not get value for section {} key {}".format(section, key))

  def getSection(self, name:str) -> SinglyLinkedList[Result[Tuple]]:
    """ (k, v) for all {k,v} under section with name
    """
    # because python lambdas do not support multiline expressions
    # I used a named function
    def _parse_items(aParser, aSection):
        # body of would-be lambda
        try:
            entries = aParser.items(aSection)
            if entries is not None:
                return Result.success(SinglyLinkedList.list(*entries))
            else:
                return Result.success(SinglyLinkedList.list())
        except Exception as e:
            return Result.failure(f"Failed to get entries under section \"{sSection}\", because: {repr(e)}")
    rName = Result.of(name)
    return rName.flatMap(lambda sec: self.config\
                        .flatMap(lambda parser: _parse_items(parser, sec)))

  def __str__(self):
    return "{}({})".format(__name__, self.config)
