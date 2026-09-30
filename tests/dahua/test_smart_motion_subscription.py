"""Smart-motion codes are only subscribed to on devices that support them.

IPC-HDW4631C-A on firmware 2.800.0000015.0.R (build 2020-04-30) keeps an
eventManager attach open and heartbeating when its codes list names
SmartMotionHuman/SmartMotionVehicle, but then delivers no events at all --
not even VideoMotion. Verified live: the same attach without those two codes
delivered VideoMotion Start/Stop immediately.
"""
from custom_components.dahua import (
    DahuaHostEventStream,
    subscribable_event_codes,
)

ALL = [
    "VideoMotion", "CrossLineDetection", "AlarmLocal", "VideoLoss", "VideoBlind",
    "AudioMutation", "CrossRegionDetection", "SmartMotionHuman", "SmartMotionVehicle",
]


class FakeCoordinator:
    def __init__(self, events, smart=False, model="IPC-HDW4631C-A", channel=0):
        self.events = events
        self._supports_smart_motion_detection = smart
        self.model = model
        self._channel = channel

    def supports_smart_motion_detection_amcrest(self):
        m = self.model.upper()
        return m.startswith("AD410") or m.startswith("DB61")

    def get_address(self):
        return "10.0.0.1"

    def get_channel(self):
        return self._channel


def test_unsupported_device_drops_smart_motion_codes():
    codes = subscribable_event_codes(FakeCoordinator(ALL, smart=False))
    assert "SmartMotionHuman" not in codes
    assert "SmartMotionVehicle" not in codes
    assert "VideoMotion" in codes and "CrossLineDetection" in codes
    assert len(codes) == len(ALL) - 2


def test_supported_device_keeps_them():
    assert subscribable_event_codes(FakeCoordinator(ALL, smart=True)) == ALL


def test_amcrest_doorbell_keeps_them():
    assert subscribable_event_codes(FakeCoordinator(ALL, smart=False, model="AD410")) == ALL


def test_none_events_is_empty():
    assert subscribable_event_codes(FakeCoordinator(None)) == []


def test_host_union_uses_filtered_codes():
    stream = DahuaHostEventStream(None, "10.0.0.1")
    stream._by_channel = {0: [FakeCoordinator(ALL, smart=False)]}
    union = stream._union()
    assert "VideoMotion" in union
    assert "SmartMotionHuman" not in union and "SmartMotionVehicle" not in union
