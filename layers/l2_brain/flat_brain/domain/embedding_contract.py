from pydantic import BaseModel, Field
from typing import List

class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="The raw string to be vectorized")
    model_name: str = Field("BAAI/bge-small-en-v1.5", description="The local model to use for embeddings")

class EmbeddingResponse(BaseModel):
    vector: List[float] = Field(..., description="The mathematical representation of the text")
    dimensions: int = Field(..., description="The length of the vector array")
    model_used: str = Field(..., description="Confirmation of the model used")

class CompressionRequest(BaseModel):
    raw_text: str = Field(..., description="Large body of text to compress")
    max_tokens: int = Field(4000, description="Strict budget constraint for the context window")
    priority_query: str = Field(None, description="Optional query to prioritize semantic chunks")

class CompressionResponse(BaseModel):
    compressed_text: str = Field(..., description="The truncated or summarized text")
    tokens_used: int = Field(..., description="Actual token count of the compressed string")
    loss_ratio: float = Field(0.0, description="Percentage of original text discarded (0.0 to 1.0)")
