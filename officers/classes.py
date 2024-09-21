from dataclasses import dataclass

@dataclass
class SheetConfig:
    model_class: type
    fields: dict