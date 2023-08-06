# -*- coding: utf-8 -*-
#
# K2hash Python Driver
#
# Copyright (c) 2022 Yahoo Japan Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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
# AUTHOR:   Hirotaka Wakabayashi
# CREATE:   Tue Feb 08 2022
# REVISION:
#
"""K2hash Python Driver"""
from __future__ import absolute_import

import logging
from ctypes import c_ubyte, c_size_t, c_int, c_uint64, c_char_p, pointer, POINTER, cast
import copy
from k2hash import K2hash, AttrPack

LOG = logging.getLogger(__name__)


class Queue:
    """
    Queue class provides methods to handle key/value pairs in k2hash hash database.
    """
    def __init__(self,
                 k2h,
                 fifo=True,
                 prefix=None,
                 password=None,
                 expire_duration=None):
        """
        Initialize a new Queue instnace.
        """
        if not isinstance(k2h, K2hash):
            raise TypeError("k2h should be a K2hash object")
        self._k2h_handle = k2h.handle
        self._libc = k2h.libc
        self._libk2hash = k2h.libk2hash

        if fifo and not isinstance(fifo, bool):
            raise TypeError("fifo should be a boolean object")
        self._fifo = fifo
        if prefix and not isinstance(prefix, str):
            raise TypeError("prefix should be a string object")
        self._prefix = prefix
        if password and not isinstance(password, str):
            raise TypeError("password should be a string object")
        self._password = password
        if expire_duration and not isinstance(expire_duration, int):
            raise TypeError("expire_duration should be a boolean object")
        if expire_duration and expire_duration <= 0:
            raise ValueError("expire_duration should not be positive")
        self._expire_duration = expire_duration

        handle = self._libk2hash.k2h_q_handle_str_prefix(
            self._k2h_handle, self._fifo,
            (c_char_p(self._prefix.encode()) if self._prefix else None))

        if handle == K2hash.K2H_INVALID_HANDLE:
            raise RuntimeError("handle should not be K2H_INVALID_HANDLE")
        self._handle = handle

    def put(self, obj, attrs=None):
        """Inserts an element into the tail of this queue.
        """
        value = []
        if not isinstance(obj, list) and not isinstance(obj, str):
            raise TypeError("obj should be a str or list object")
        if not obj:
            raise ValueError("obj should not be empty")
        if isinstance(obj, list):
            value += copy.deepcopy(obj)
        elif isinstance(obj, str):
            value.append(obj)

        if attrs and not isinstance(attrs, dict):
            raise TypeError("attrs should be a dict")
        ap_array_pointer = None
        ap_array = None
        if attrs:
            attrpack_len = len(attrs)
            ap_array = AttrPack * attrpack_len
            ap_list = []
            for key, val in attrs.items():
                attr_pack = AttrPack()
                key_bin = key.encode()
                attr_pack.pkey = cast(key_bin, POINTER(c_ubyte))
                attr_pack.keylength = c_size_t(len(key_bin))
                val_bin = val.encode()
                attr_pack.pval = cast(val_bin, POINTER(c_ubyte))
                attr_pack.vallength = c_size_t(len(val_bin))
                ap_list.append(attr_pack)
            ap_array_pointer = pointer(ap_array()[0])

        res = self._libk2hash.k2h_q_str_push_wa(
            self._handle, c_char_p(obj.encode()),
            (ap_array_pointer if ap_array else None), 0,
            (c_char_p(self._password.encode()) if self._password else None),
            (pointer(c_uint64(self._expire_duration))
             if self._expire_duration else None))
        return res

    def clear(self):
        """Removes all of the elements from this collection (optional operation).
        """
        count = self.qsize()
        if count > 0:
            res = self._libk2hash.k2h_q_remove(self._handle, c_int(count))
            return res
        return True

    def close(self):
        """
        Free QueueHandle
        """
        res = self._libk2hash.k2h_q_free(self._handle)
        return res

    def qsize(self):
        """Returns the number of queue.
        """
        res = self._libk2hash.k2h_q_count(self._handle)
        return res

    def element(self, position=0):
        """Finds and gets a object from the head of this queue.
        """
        if not isinstance(position, int):
            raise TypeError("position should be a int object")
        if (position < 0):
            raise ValueError("count should be positive")

        ppdata = pointer(c_char_p("".encode()))
        pdatalen = pointer(c_size_t(0))
        self._libk2hash.k2h_q_read_wp(
            self._handle, ppdata, pdatalen, c_int(position),
            (c_char_p(self._password.encode()) if self._password else None))
        datalen = pdatalen.contents.value
        if datalen > 0:
            pdata = ppdata.contents.value.decode()
            self._libc.free(ppdata.contents)
            return pdata
        return ""

    @property
    def handle(self):
        """Returns a Queue handle.
        """
        return self._handle

    def empty(self):
        """Returns true if, and only if, queue size is 0.
        """
        res = self._libk2hash.k2h_q_empty(self._handle)
        return res

    def get(self):
        """Finds and gets a object from the head of this queue.
        """
        ppval = pointer(c_char_p("".encode()))
        res = self._libk2hash.k2h_q_str_pop_wp(
            self._handle, ppval,
            (c_char_p(self._password.encode()) if self._password else None))

        if res and ppval.contents.value:
            pval = ppval.contents.value.decode()
            if ppval.contents:
                self._libc.free(ppval.contents)
            return pval
        return ""

    def print(self):
        """Print the objects in this queue.
        """
        res = self._libk2hash.k2h_q_dump(self._handle, None)
        return res

    def remove(self, count=1):
        """Removes objects from this queue.
        """
        if not isinstance(count, int):
            raise TypeError("count should be a int object")
        if count <= 0:
            raise ValueError("count should be positive")

        vals = []
        for _ in range(count):
            val = self._libk2hash.k2h_q_remove(self._handle, 1)
            if val:
                vals.append(val)
        return vals

    def __repr__(self):
        """Returns full of members as a string.
        """
        attrs = []
        for attr in [
                '_handle', '_k2h_handle', '_libk2hash', '_fifo', '_prefix',
                '_expire_duration'
        ]:  # should be hardcoded.
            val = getattr(self, attr)
            if val:
                attrs.append((attr, repr(val)))
            else:
                attrs.append((attr, ''))
            values = ', '.join(['%s=%s' % i for i in attrs])
        return '<_Queue ' + values + '>'


#
# Local variables:
# tab-width: 4
# c-basic-offset: 4
# End:
# vim600: expandtab sw=4 ts=4 fdm=marker
# vim<600: expandtab sw=4 ts=4
#
