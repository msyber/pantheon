from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.observability import logger


class LongTermMemory:
    def __init__(self, mission_id):
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store_path = f"memory_store/{mission_id}"
        self.vector_store = None

    def add_lesson(self, lesson: str):
        """Adds a new lesson to the memory."""
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(texts=[lesson], embedding=self.embedding_model)
        else:
            self.vector_store.add_texts(texts=[lesson])

        # In a real system, you'd save to a persistent location
        # self.vector_store.save_local(self.vector_store_path)
        logger.info(f"[LTM] Lesson added: '{lesson}'")

    def recall_lessons(self, query: str, num_lessons: int = 2) -> list:
        """Recalls relevant lessons based on a query."""
        if self.vector_store is None:
            return []

        results = self.vector_store.similarity_search(query, k=num_lessons)
        return [doc.page_content for doc in results]
