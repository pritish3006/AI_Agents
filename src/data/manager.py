from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
from datetime import datetime
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from src.config import AppConfig

class DataManager:
    """
    Manages all data operations including:
    - Document processing and storage
    - Vector store operations
    - State persistence
    - Data retrieval and updates
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY
        )
        self._initialize_vectorstore()
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def _initialize_vectorstore(self) -> None:
        """Initialize connection to vector store."""
        pinecone.init(
            api_key=self.config.PINECONE_API_KEY,
            environment=self.config.PINECONE_ENVIRONMENT
        )
        if self.config.PINECONE_INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.config.PINECONE_INDEX_NAME,
                dimension=1536,  # OpenAI embeddings dimension
                metric="cosine"
            )
        self.vectorstore = pinecone.Index(self.config.PINECONE_INDEX_NAME)
    
    async def process_document(
        self,
        content: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Process a document for storage and retrieval.
        
        Args:
            content: Document content or file path
            metadata: Additional document metadata
            
        Returns:
            List of chunk IDs
        """
        # Load content if it's a file path
        if isinstance(content, Path):
            with open(content, 'r') as f:
                content = f.read()
        
        # Split text into chunks
        chunks = self._text_splitter.split_text(content)
        
        # Create documents with metadata
        docs = []
        chunk_ids = []
        base_metadata = metadata or {}
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"chunk_{datetime.now().timestamp()}_{i}"
            chunk_metadata = {
                **base_metadata,
                "chunk_id": chunk_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            docs.append(Document(page_content=chunk, metadata=chunk_metadata))
            chunk_ids.append(chunk_id)
        
        # Generate embeddings and store in vector store
        await self.store_embeddings(docs)
        
        return chunk_ids
    
    async def store_embeddings(self, documents: List[Document]) -> None:
        """Store document embeddings in vector store."""
        # Generate embeddings
        texts = [doc.page_content for doc in documents]
        embeddings = await self.embeddings.aembed_documents(texts)
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            vectors.append((
                doc.metadata["chunk_id"],
                embedding,
                {"text": doc.page_content, **doc.metadata}
            ))
        
        # Upsert to Pinecone
        self.vectorstore.upsert(vectors=vectors)
    
    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity."""
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Search in vector store
        results = self.vectorstore.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        
        return [
            {
                "text": match.metadata["text"],
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
    
    async def store_agent_state(
        self,
        agent_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Store agent state for persistence."""
        # TODO: Implement proper state storage (e.g., in a database)
        state_file = Path(f"data/states/{agent_id}.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
    
    async def load_agent_state(
        self,
        agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """Load persisted agent state."""
        state_file = Path(f"data/states/{agent_id}.json")
        
        if not state_file.exists():
            return None
            
        with open(state_file, 'r') as f:
            return json.load(f)
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        # TODO: Implement proper cleanup
        pass 