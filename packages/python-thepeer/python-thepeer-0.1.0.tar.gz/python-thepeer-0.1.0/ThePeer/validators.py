import sys
sys.path.append("..")
from schema import Schema, And, Use, Optional, SchemaError
from dataclasses import dataclass

@dataclass
class Validator():

    conf : dict
    schema_conf : Schema

    def validate(self):
        try:
            self.schema_conf.validate(self.conf)
            return True
        except SchemaError:
            return False




