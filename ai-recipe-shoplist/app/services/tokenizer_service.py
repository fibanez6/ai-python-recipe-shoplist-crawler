import tiktoken

from typing import Optional
from ..config.logging_config import get_logger
from ..config.pydantic_config import (
    TIKTOKEN_MODEL,
    TIKTOKEN_ENCODER
)

# Get module logger
logger = get_logger(__name__)

class TokenizerService:
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the tokenizer service."""

        self.model = model_name or TIKTOKEN_MODEL

        if self.model is None:
            logger.debug(f"[TokenizerService] Initializing tokenizer for encoder: {TIKTOKEN_ENCODER}")
            self.tokenizer = tiktoken.get_encoding(TIKTOKEN_ENCODER)
        else:
            logger.debug(f"[TokenizerService] Initializing tokenizer for model: {self.model}")
            self.tokenizer = tiktoken.encoding_for_model(self.model)

        logger.info(f"[TokenizerService] Tokenizer initialized for model: {self.model}")

    def get_tokens(self, text: str) -> str:
        """Count the number of tokens in the given text."""

        return self.tokenizer.encode(text)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the given text."""
        
        tokens = self.tokenizer.encode(text)
        return len(tokens)
    
    def truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within the specified token limit."""

        tokens = self.get_tokens(text)
        num_tokens = len(tokens)

        logger.debug(f"[TokenizerService] Counting tokens: {num_tokens} (limit: {max_tokens})")

        if num_tokens <= max_tokens:
            return text
        truncated_tokens = tokens[:max_tokens]

        logger.info(f"[TokenizerService] Text truncated from {num_tokens} to {max_tokens} tokens")
        return self.tokenizer.decode(truncated_tokens)  
    
    def __repr__(self) -> str:
        return f"<TokenizerService(model={self.model}, encoder={TIKTOKEN_ENCODER})>"