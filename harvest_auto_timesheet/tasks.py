from enum import IntEnum


class ProjectEnum(IntEnum):
    """Enum for project IDs."""

    FM_INTERNAL = 41555778
    EYECUE_GENERAL = 43607407
    SOC2 = 43333287


class TaskEnum(IntEnum):
    """Enum for task IDs."""

    LEAVE = 22157760
    PUBLIC_HOLIDAY = 22157761
    SCRUM_CEREMONIES = 22157752
    ENGINEERING = 22157391
    INTERNAL_MEETING = 22157751
    L3_ON_CALL = 22688670
