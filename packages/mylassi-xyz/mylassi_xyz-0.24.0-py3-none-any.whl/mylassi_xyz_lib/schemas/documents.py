__all__ = [
    'CreateDocumentOptionData', 'CreateDocumentOptionSchema',
    'UpdateDocumentOptionData', 'UpdateDocumentOptionSchema',
    'DocumentData', 'DocumentSchema'
]

from dataclasses import dataclass, field
from typing import Optional

import marshmallow_dataclass

from .users import UserData


@dataclass
class CreateDocumentOptionData:
    name: str = field()
    text: str = field()


@dataclass
class UpdateDocumentOptionData:
    name: str = field()
    text: str = field()


@dataclass
class DocumentData(UpdateDocumentOptionData):
    id: str = field()
    name: str = field()
    text: str = field()

    owner: Optional[UserData] = field()


CreateDocumentOptionSchema = marshmallow_dataclass.class_schema(CreateDocumentOptionData)()
UpdateDocumentOptionSchema = marshmallow_dataclass.class_schema(UpdateDocumentOptionData)()

DocumentSchema = marshmallow_dataclass.class_schema(DocumentData)()
