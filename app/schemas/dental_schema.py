from enum import Enum


class ToothNumber(Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8


class ToothConditions(Enum):
    healthy = "healthy"
    fill = "filling"
    decay = "decay/caries"
    crown = "crown"
    canal = "root canal"
    bridge = "bridge"
    implant = "implant"
    missing = "missing tooth"


class ToothSurface(Enum):
    mesial = "mesial"
    buccal = "buccal"
    occlusal = "occlusal"
    labial = "labial/facial"
    distal = "distal"
    lingual = "lingual"
    incisal = "incisal"
    full = "full"


class Jaw(Enum):
    UP = "upper"
    DOWN = "lower"


class JawSide(Enum):
    L = "left"
    R = "right"
