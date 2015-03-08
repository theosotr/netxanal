"""
This module contains a dictionary which describes the graph object which being
currently analyzed by a user.

For example, if there are two users A and B which are simultaneously using system
the keys of this dictionary will be A and B with values the graph object which
each user is analyzing corresponding.
"""
__author__ = 'Thodoris Sotiropoulos'
global graphfile
graphfile = {}