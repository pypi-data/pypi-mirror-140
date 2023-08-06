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
import abc
from fpinpy.meta.decorators import overrides
from fpinpy.result import Result
from typing import Iterator, TypeVar, Generic, Callable, Dict
# Declare module-scoped type variables for generics
T = TypeVar('T')
U = TypeVar('U')

# TODO Make this meta class work with parameter T
class SinglyLinkedListMeta(type):
    """

        Meta classes propogate to all subclasses.
        This is here to affect subclasses only.

        Generic Types: https://www.python.org/dev/peps/pep-0560/
    """
    def __new__(cls, clsname, bases, clsdict):
        return super().__new__(cls, clsname, bases, clsdict)
    def __getitem__(self, index):
        return index
    def __class_getitem__(cls, item):
        return f"{cls.__name__}[{item.__name__}]"

class AbstractSinglyLinkedList(metaclass=SinglyLinkedListMeta):
    def __getitem__(self, index):
        return index
    def __class_getitem__(cls, item):
        return f"{cls.__name__}[{item.__name__}]"

class SinglyLinkedListIterator:
    """Forward and backward iterator

        This is intended to provide an iterative, performant way
        to implement exposed functions. The iterator itself
        is not intended to be exposed to the outside, although
        it can be used.
    """
    def __init__(self, singly_linked_list, reverse: bool=False):
        if reverse:
            self._state = self._make_reversed_state(singly_linked_list)
        else:
            self._state = singly_linked_list

    def __iter__(self):
        return self

    def __next__(self):
        """
            Does not return Nil
        """
        if not self._state.isEmpty():
            next_elem = self._state.head()
            self._state= self._state.tail()
            return next_elem
        else:
            raise StopIteration

    def _make_reversed_state(self, aList):
        """ Iterative implementation of traversing the list backwards.


            Recursive implementation

            def _reversed(acc, aList):
                if aList.isEmpty():
                    return acc
                else:
                    return _reversed(SinglyLinkedList.cons(internal_state.head(), accumulator), internal_state.tail())
            return _reversed(accumulator, aList)
        """
        internal_state = aList
        stack = [] # LIFO
        while not internal_state.isEmpty():
            head = internal_state.head()
            tail = internal_state.tail()
            internal_state = internal_state.tail()
            stack.append(head)
        return SinglyLinkedList.list(*reversed(stack))

class SinglyLinkedList(Generic[T]): # Generic[T] is a subclass of metaclass=ABCMeta (ABC)
    """The base class for singly-linked list objects
    """

    @staticmethod
    def list(*args):
        if len(args) == 0:
            return SinglyLinkedList.nil()
        else:
            output = SinglyLinkedList.nil()
            for i in range(len(args)-1, -1, -1):
                output = Cons(args[i], output)
            return output

    @classmethod
    def nil(cls):
        """Returns singleton Nil.

        """
        return Nil()

    @classmethod
    def cons(cls, head: T, tail):# Tail is Cons[T]
        return Cons(head, tail)

    def __iter__(self):
        """ Non-functional iterator for performance in some cases.

            This is not intended for use outside of this class, but
            was added here for ease of iterating the list using data
            sharing.
        """
        return SinglyLinkedListIterator(self)

    def __reversed__(self):
        return SinglyLinkedListIterator(self, reverse=True)

    @staticmethod
    def flattenResult(aList):# : SinglyLinkedList[Result[T]]):
        """ Takes a list of Result and returns a list of their raw values.

            Failure or Empty will be converted into an empty list.
        """
        tmp = []
        for elem in aList:
            tmp.append(elem.getOrElse(SinglyLinkedList.list()))
        return SinglyLinkedList.list(*tmp)

    @staticmethod
    def foldRightStatic(aList, identity, function):
        #if aList.isEmpty():
        #    return identity
        #else:
        #    return function(aList.head())(SinglyLinkedList.foldRight(aList.tail(), identity, function))
        accumulator = identity
        tmp_list = aList.reverse()
        while not tmp_list.isEmpty():
            next_elem = tmp_list.head()
            accumulator = function(next_elem)(accumulator)
            tmp_list = tmp_list.tail()
        return accumulator

    @staticmethod
    def concat(list1, list2): # -> SinglyLinkedList
        """ Requires  static foldRight or foldLeft """
        return SinglyLinkedList.foldRightStatic(list1, list2, lambda x: lambda y: SinglyLinkedList.cons(x, y))

    @staticmethod
    def traverse(aList, function, ignoreFailure=False, emptyIsFailure=True, successOfFailure=False): # SinglyLinkedList[T], Callable[[T], Result[U]] -> Result[List[U]]:
        """ Applies function and collects Result.Success raw values.

            Input:
            aList: SinglyLinkedList[T]; a list to process
            function: T -> Result[U]; a function
            ignoreFailure: Bool; any occurrance of Failure is not included in output
            emptyIsFailure: Bool; any occurance of Empty is considered a Failure 

            Output:
            Result[List[U]]
        """
        arr = []
        failure_recognized = False
        for elem in aList:
            tmp = function(elem)
            if tmp.isSuccess():
                arr.append(tmp.getOrElse("Could not extract Success"))
            if tmp.isEmpty():
                if emptyIsFailure:
                    # reassign Empty as Failure
                    tmp = Result.failure(RuntimeError("Empty was considered Failure."))
            if tmp.isFailure():
                if ignoreFailure:
                    continue
                failure_recognized = True
                if successOfFailure:
                    arr.append(tmp.forEachOrFail(lambda x: x).getOrElse("Failure"))
        return Result.failure(RuntimeError(SinglyLinkedList.list(*arr))) if failure_recognized \
            else Result.success(SinglyLinkedList.list(*arr))

    @staticmethod
    def sequence(aList, ignoreFailure=False, emptyIsFailure=True, successOfFailure=False): # List[Result[T]]) -> Result[List[T]]:
        """ Converts List[Result[T]]) into Result[List[T]]

            The default configuration: Any occurrance of Failure or Empty will yield Failure[List[T]]
        """
        return SinglyLinkedList.traverse(aList, lambda x: x)

    @abc.abstractmethod
    def head(self):
        raise NotImplementedError

    @abc.abstractmethod
    def tail(self):# -> SinglyLinkedList[T]
        raise NotImplementedError

    @abc.abstractmethod
    def isEmpty(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def setHead(self, head: T):# -> SinglyLinkedList[T]
        """Instance method to replace first element

            of list with a new value.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def length(self) -> int:
        raise NotImplementedError

    def reverse(self):
        return SinglyLinkedList.list(*reversed(self))

    @abc.abstractmethod
    def foldLeft(self, identity: U, function: Callable[[U], Callable[[T], U]]):
        raise NotImplementedError

    @abc.abstractmethod
    def foldRight(self, identity: U, function: Callable[[U], Callable[[T], U]]):
        raise NotImplementedError
    #    return self.reverse().foldLeft(identity, lambda x: lambda y: function(y)(x))

    def map(self, function: Callable[[T], U]):# -> SinglyLinkedList[U]:
        """ Map a function T -> U to each element in a list.

            Map can be defined here in the superclass for both subclasses,
            because the implementation is abstracted enough to allow for this.
        """
        #return self.foldLeft(self.list(), lambda h: lambda t: self.cons(function(h), t))
        accumulator = []
        for elem in self:
            accumulator.append(function(elem))
        return SinglyLinkedList.list(*accumulator)

    @abc.abstractmethod
    def drop(self, n: int):
        """Remove n elements from the front of the list.
        """
        raise NotImplementedError

    def filter(self, predicate: Callable[[T], bool]):
        """ Removes elements from the lst that do not satisfy a given predicate.
        """
        return self.foldRight(SinglyLinkedList.list(), \
            lambda h: lambda t: SinglyLinkedList.cons(h, t) if predicate(h) else t
        )

    def forEach(self, effect: Callable[[T], None]):
        worklist = self
        while not worklist.isEmpty():
            effect(worklist.head())
            worklist = worklist.tail()
        return None

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

class Nil(SinglyLinkedList[T]):
    """Represents empty list.
    """

    def __init__(self):
        pass

    _instances: Dict[object, object] = {}
    import threading
    lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls.lock:
                # another thread could have created the lock
                # between the check and acquiring lock, so check again.
                if cls not in cls._instances:
                    cls._instances[cls] = super().__new__(Nil, *args, **kwargs)
        return cls._instances[cls]

    @overrides(SinglyLinkedList)
    def head(self) -> T:
        raise RuntimeError("head called on empty list")

    @overrides(SinglyLinkedList)
    def tail(self) -> SinglyLinkedList[T]:
        raise RuntimeError("tail called on empty list")

    @overrides(SinglyLinkedList)
    def isEmpty(self) -> bool:
        return True

    @overrides(SinglyLinkedList)
    def setHead(self, head: T):# -> SinglyLinkedList[T]
        raise RuntimeError("setHead called on empty list.")

    @overrides(SinglyLinkedList)
    def length(self) -> int:
        return 0

    @overrides(SinglyLinkedList)
    def foldLeft(self, identity: U, function: Callable[[U, T], U]):# TODO add out type
        """ Nil implementation returns the identity element (Neutral). """
        return identity

    @overrides(SinglyLinkedList)
    def foldRight(self, identity: U, function: Callable[[U, T], U]):
        return identity

    @overrides(SinglyLinkedList)
    def drop(self, n: int) -> SinglyLinkedList[T]:
        return self

    #@overrides(SinglyLinkedList)
    #def filter(self, predicate: Callable[[T], bool]):
    #    return self

    @overrides(SinglyLinkedList)
    def __str__(self):
        return "[NIL]"

    def __repr__(self):
        return "Nil"

    def __eq__(self, o):
        return isinstance(o, Nil)

    def __hash__(self):
        return hash(repr(self))

class Cons(SinglyLinkedList[T]):
    """Represents non-empty list.
    """

    def __init__(self,
                 head: T,
                 tail: SinglyLinkedList[T]):
        self._head = head
        assert isinstance(tail, Cons) or isinstance(tail, Nil), f"Type was {type(tail)} but should have been Cons or Nil"
        self._tail = tail
        self._length = tail.length() + 1

    @overrides(SinglyLinkedList)
    def head(self) -> T:
        return self._head

    @overrides(SinglyLinkedList)
    def tail(self) -> SinglyLinkedList[T]:
        return self._tail

    @overrides(SinglyLinkedList)
    def isEmpty(self) -> bool:
        return False

    @overrides(SinglyLinkedList)
    def setHead(self, head: T) -> SinglyLinkedList[T]:
        return SinglyLinkedList.cons(head, self.tail())

    @overrides(SinglyLinkedList)
    def length(self):
        return self._length

    @overrides(SinglyLinkedList)
    def drop(self, n: int) -> SinglyLinkedList[T]:
        if n <= 0:
            """Case 0 or negative"""
            return self
        else:
            """Case >0 until 0 or list is Nil"""
            def _drop_iterative(n: int) -> SinglyLinkedList[T]:
                # init state
                output = self
                while n != 0 and not output.isEmpty():
                    # next state
                    output = output.tail()
                    n -= 1
                return output
            return _drop_iterative(n)

    #@overrides(SinglyLinkedList)
    #def filter(self, predicate: Callable[[T], bool]):
    #    return self.foldLeft(SinglyLinkedList.list(), lambda h: lambda t: \
    #        SinglyLinkedList.list(h, t) if predicate(h) else t)

    @overrides(SinglyLinkedList)
    def foldLeft(self, identity: U, function: Callable[[U], Callable[[T], U]]) -> U:
        """ Implemented imperatively as technique to avoid too many stack calls.

            Alternatively, an iterator could be defined for this list so that a for loop
            can be used.

            Usage: folderLeft(list(), lambda head: lambda tail: Cons(function(h), t)

            Effective recursive implementation

            def _foldLeft(acc: U, lst: SinglyLinkedList[T]):
                if lst.isEmpty():
                    return acc
                else:
                    return _foldLeft(function(acc)(lst.head()), lst.tail())
            return _foldLeft(identity, self)

        """
        accumulator = identity # (empty/Nil)
        for elem in self:
           accumulator = function(accumulator)(elem)
        return accumulator

    @overrides(SinglyLinkedList)
    def foldRight(self, identity: U, function: Callable[[T], Callable[[U], U]]) -> U:
        accumulator = identity
        tmp_list = self.reverse()
        while not tmp_list.isEmpty():
            next_elem = tmp_list.head()
            accumulator = function(next_elem)(accumulator)
            tmp_list = tmp_list.tail()
        return accumulator

    @overrides(SinglyLinkedList)
    def __str__(self) -> str:
        accumulator = ""
        def toString(accumulator: str, aList: SinglyLinkedList) -> str:
            if aList.isEmpty():
                return accumulator
            else:
                accumulator = accumulator.__add__(str(aList.head())).__add__(", ")
                return toString(accumulator , aList.tail())
        return f"[{toString(accumulator, self)}NIL]"

    def __repr__(self) -> str:
        accumulator = ""
        def toString(accumulator: str, aList: SinglyLinkedList) -> str:
            if aList.isEmpty():
                # Cons(accumulator, Nil)
                return accumulator + repr(aList) + ")"
            else:
                accumulator = accumulator + "Cons(" + repr(aList.head()) + ", "
                return toString(accumulator, aList.tail())
        return f"{toString(accumulator, self)}"
