__author__ = 'zak'
from rest_framework import serializers

from tincan.statement_base import StatementBase
from tincan.statement import Statement

class CLRecipe(Statement):

    _props_req = [

    ]

    _props = [
        "result",
        "timestamp",
        "clrecipe_version"
    ]