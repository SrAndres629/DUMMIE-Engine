import tiktoken
from ..domain.embedding_contract import (
    EmbeddingRequest, EmbeddingResponse,
    CompressionRequest, CompressionResponse
)
from ..domain.semantic_ports import IEmbeddingAdapter, IContextCompressor

class FastEmbedAdapter(IEmbeddingAdapter):
    """
    Adaptador Físico (Infrastructure) usando `fastembed`.
    """
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self.model_name)
            except ImportError:
                raise RuntimeError("fastembed package is not installed. Run: pip install fastembed")
        return self._model

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = self._get_model()
        embeddings_gen = model.embed([request.text])
        vector_np = next(embeddings_gen)
        vector_list = vector_np.tolist()
        
        return EmbeddingResponse(
            vector=vector_list,
            dimensions=len(vector_list),
            model_used=request.model_name
        )

class LocalContextCompressor(IContextCompressor):
    """
    Compresor Físico (Infrastructure) basado en `tiktoken`.
    """
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding_name = encoding_name
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            try:
                self._encoder = tiktoken.get_encoding(self.encoding_name)
            except ImportError:
                raise RuntimeError("tiktoken is not installed. Run: pip install tiktoken")
        return self._encoder

    def compress(self, request: CompressionRequest) -> CompressionResponse:
        encoder = self._get_encoder()
        tokens = encoder.encode(request.raw_text)
        original_count = len(tokens)
        
        if original_count <= request.max_tokens:
            return CompressionResponse(
                compressed_text=request.raw_text,
                tokens_used=original_count,
                loss_ratio=0.0
            )
            
        truncated_tokens = tokens[:request.max_tokens]
        compressed_str = encoder.decode(truncated_tokens)
        
        marker = "\n...[CONTEXT TRUNCATED BY TOKEN BUDGET]..."
        if request.max_tokens > 20:
            compressed_str += marker
            
        loss = float(original_count - request.max_tokens) / float(original_count)
        
        return CompressionResponse(
            compressed_text=compressed_str,
            tokens_used=len(truncated_tokens),
            loss_ratio=loss
        )
