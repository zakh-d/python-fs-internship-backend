import re
from sqlite3 import IntegrityError
from typing import Union


def get_conflicting_field(err: IntegrityError) -> Union[tuple[str, str], None]:
    """
    Parses the IntegrityError message and returns tuple with conflicting field name and value.
    """
    pattern = re.compile(r'DETAIL\:\s+Key \((?P<field>.+?)\)=\((?P<value>.+?)\) already exists')
    match = pattern.search(str(err))
    if match is not None:
        return match['field'], match['value']
