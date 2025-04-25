from pydantic import BaseModel
from app.schemas.dental_schema import (
    ToothNumber,
    ToothConditions,
    ToothSurface,
    Jaw,
    JawSide,
)


class Tooth(BaseModel):
    position: ToothNumber
    side: JawSide
    jaw: Jaw
    condition: ToothConditions
    surface: ToothSurface


tooth_mapping = {
    Jaw.UP: {
        JawSide.L: [9, 10, 11, 12, 13, 14, 15, 16],
        JawSide.R: [1, 2, 3, 4, 5, 6, 7, 8],
    },
    Jaw.DOWN: {
        JawSide.L: [17, 18, 19, 20, 21, 22, 23, 24],
        JawSide.R: [25, 26, 27, 28, 29, 30, 31, 32],
    },
}
