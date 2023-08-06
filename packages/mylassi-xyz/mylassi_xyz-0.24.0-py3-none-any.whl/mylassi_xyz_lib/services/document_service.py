__all__ = ['DocumentService']

from ..api_client import MyLassiApiClient
from ..schemas.documents import *


class DocumentService(MyLassiApiClient):
    def create_document(self, data: CreateDocumentOptionData) -> DocumentData:
        request_data = CreateDocumentOptionSchema.dump(data)

        response = self.post('/api/v2/documents', request_data)

        return DocumentSchema.load(response)

    def get_document(self, doc_id: str) -> DocumentData:
        response = self.get(f'/api/v2/documents/{doc_id}')

        return DocumentSchema.load(response)

    def update_document(self, doc_id: str, data: UpdateDocumentOptionData) -> DocumentData:
        request_data = UpdateDocumentOptionSchema.dump(data)
        response = self.post(f'/api/v2/documents/{doc_id}', request_data)

        return DocumentSchema.load(response)
