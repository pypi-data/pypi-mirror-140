from typing import TYPE_CHECKING, Dict, List

from nawah.enums import Event

if TYPE_CHECKING:
    from nawah.classes import EXTN, NAWAH_QUERY


def _extn_list(
    extns: Dict[str, 'EXTN'],
    skip_events: List[Event],
    query: 'NAWAH_QUERY',
):
    if Event.EXTN in skip_events or '$extn' in query and query['$extn'] is False:
        return []

    extn_list = [attr_name.split(':')[0].split('.')[0] for attr_name in extns]

    if '$extn' in query and isinstance(query['$extn'], list):
        extn_list = [
            attr_name
            for attr_name in query['$extn']
            if attr_name.split(':')[0].split('.')[0] in extn_list
        ]

    if '$attrs' in query:
        extn_list = [
            attr_name for attr_name in extn_list if attr_name in query['$attrs']
        ]

    return extn_list
