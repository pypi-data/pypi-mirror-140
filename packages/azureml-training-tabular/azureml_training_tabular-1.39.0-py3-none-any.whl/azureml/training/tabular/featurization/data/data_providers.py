# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""IoC container for data providers."""
from typing import Any

from .pretrained_dnn_provider import PretrainedDNNProvider
from .word_embeddings_info import EmbeddingInfo
from .wordembeddings_provider import WordEmbeddingsProvider


class DataProviders:
    """IoC container for data providers."""

    @classmethod
    def get(cls, embeddings_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Get data provider based on embedding name.

        :param embeddings_name: Name of the embeddings.
        """
        if embeddings_name in EmbeddingInfo._all_ or kwargs.get("model_name") in EmbeddingInfo._all_:
            factory_method = getattr(cls, embeddings_name)
            if factory_method:
                return factory_method(*args, **kwargs)
        return None

    @classmethod
    def wiki_news_300d_1M_subword(cls, *args: Any, **kwargs: Any) -> WordEmbeddingsProvider:
        """Create fast text based word embeddings provider."""
        kwargs["embeddings_name"] = "wiki_news_300d_1M_subword"
        return WordEmbeddingsProvider(*args, **kwargs)

    @classmethod
    def glove_6B_300d_word2vec(cls, *args: Any, **kwargs: Any) -> WordEmbeddingsProvider:
        """Create GloVe based word embeddings provider."""
        kwargs["embeddings_name"] = "glove_6B_300d_word2vec"
        return WordEmbeddingsProvider(*args, **kwargs)

    @classmethod
    def pretrained_text_dnn(cls, *args: Any, **kwargs: Any) -> PretrainedDNNProvider:
        """Create BERT/XNET/etc provider."""
        return PretrainedDNNProvider(*args, **kwargs)
