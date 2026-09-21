from typing import Literal
from typing_extensions import TypedDict


HRCategory = Literal[
    "PAPERWORK",
    "ACCESS",
    "BENEFITS",
    "PAYROLL",
]


class HRState(TypedDict, total=False):
    question: str
    category: HRCategory
    response: str