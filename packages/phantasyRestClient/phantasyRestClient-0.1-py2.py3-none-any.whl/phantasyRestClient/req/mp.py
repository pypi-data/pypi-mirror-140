#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Request for resources from mp (MachinePortal) router.
"""


class MachinePortalResources:
    SESSION = None
    URL = None

    def __init__(self):
        pass

    @staticmethod
    def _get_attr(name: str, attr: str):
        # Return the attribute value of an high-level element.
        r = MachinePortalResources.SESSION.get(
            f"{MachinePortalResources.URL}/devices/attr/{name}",
            params={'attr': attr})
        if not r.ok:
            return None
        return r.json()['value']

    # all devices
    @staticmethod
    def getElements(name_pattern='*', type_pattern='*'):  # -> List[str]
        r = MachinePortalResources.SESSION.get(
            f"{MachinePortalResources.URL}/devices",
            params={
                'name': name_pattern,
                'type': type_pattern
            })
        if not r.ok:
            return None
        return [[i] for i in r.json()]

    # attributes
    @staticmethod
    def getElemPos1(name: str) -> float:
        return MachinePortalResources._get_attr(name, 'sb')

    @staticmethod
    def getElemPos2(name: str) -> float:
        return MachinePortalResources._get_attr(name, 'se')

    @staticmethod
    def getElemPos(name: str):  # -> List[float, float]:
        return [(MachinePortalResources._get_attr(name, 'sb'),
                 MachinePortalResources._get_attr(name, 'se'))]

    @staticmethod
    def getElemType(name: str) -> str:
        return MachinePortalResources._get_attr(name, 'family')

    @staticmethod
    def getElemLength(name: str) -> float:
        return MachinePortalResources._get_attr(name, 'length')

    @staticmethod
    def getElemNameAlias(name: str) -> str:
        return MachinePortalResources._get_attr(name, 'phy_name')

    @staticmethod
    def getElemTypeAlias(name: str) -> str:
        return MachinePortalResources._get_attr(name, 'phy_type')

    # methods
    @staticmethod
    def getElemFields(name: str):  # -> List[str]
        r = MachinePortalResources.SESSION.get(
            f"{MachinePortalResources.URL}/devices/fields/{name}")
        if not r.ok or r.json() == "Non-existing device":
            return [[]]
        return [r.json()]

    @staticmethod
    def getElemPVs(name: str, field: str, handle: str):  # -> List[str]
        r = MachinePortalResources.SESSION.get(
            f"{MachinePortalResources.URL}/devices/pv/{name}",
            params={
                'field': field,
                'handle': handle
            })
        if not r.ok or r.json() == "Non-existing device":
            return [[]]
        return [r.json()]

    @staticmethod
    def convert(name: str, value: float, field: str) -> float:
        r = MachinePortalResources.SESSION.post(
            f"{MachinePortalResources.URL}/devices/convert/{name}",
            params={
                'value': value,
                'field': field
            })
        if not r.ok or r.json() == 'Non-existing device':
            return None
        return r.json()['value']

    @staticmethod
    def getSetting(name: str, field: str) -> float:
        r = MachinePortalResources.SESSION.get(
            f"{MachinePortalResources.URL}/devices/value/{name}",
            params={
                'handle': 'setpoint',
                'field': field
            })
        if not r.ok or r.json()['value'] in ('Non-existing device',
                                             'Non-existing field'):
            return None
        return r.json()['value']

    @staticmethod
    def getReading(name: str, field: str) -> float:
        r = MachinePortalResources.SESSION.get(
            f"{MachinePortalResources.URL}/devices/value/{name}",
            params={
                'handle': 'readback',
                'field': field
            })
        if not r.ok or r.json()['value'] in ('Non-existing device',
                                             'Non-existing field'):
            return None
        return r.json()['value']

    @staticmethod
    def getLattice() -> dict:
        """Return a dict of machine/segment: {'machine': <machine-name>, 'segment': <segment-name>}
        """
        r = MachinePortalResources.SESSION.get(
                f"{MachinePortalResources.URL}/lattice")
        if not r.ok:
            return None
        return r.json()
