import io
from typing import NamedTuple, Optional, Union, List
from datetime import datetime

import numpy as np

from ..custom_exceptions import EmbeddingError
from ..models.annotation import Annotation
from ..tools.misc import get_md5_from_json_object, hash_string_into_positive_integer_reproducible
from ..tools.naming import get_similarity_index_name


class Image(NamedTuple):
    image_path: Optional[str] = None
    id: Optional[str] = None
    image_url: Optional[str] = None
    image_uri: Optional[str] = None
    image_bytes: Optional[Union[io.BytesIO, bytes, str]] = None
    sensor: Optional[str] = None
    timestamp: Optional[Union[str, datetime]] = None
    session_uid: Optional[str] = None
    annotations: Optional[List[Annotation]] = None
    aux_metadata: Optional[dict] = None


class Embedding(object):
    def __init__(self,
                 data: Union[io.BytesIO, bytes, np.array, List[float]],
                 model: str,
                 version: str,
                 asset_id: str,
                 asset_type: str,
                 set_ids: Optional[Union[str, List[str]]] = None,
                 layer: Optional[Union[int, str]] = None,
                 dtype: Optional[Union[type(np.float32), type(np.float64), type(float)]] = np.float32,
                 ndim: Optional[int] = None,
                 ):

        if not isinstance(data, io.BytesIO) and not isinstance(data, bytes):
            raise NotImplementedError("Currently only embedding bytes are supported")

        # Enforce a cast to float32
        embedding_array = np.float32(np.frombuffer(data, dtype=dtype))
        self.ndim = embedding_array.reshape(1, -1).shape[1]

        if ndim and self.ndim != ndim:
            raise EmbeddingError("ndim passed {} does not match the ndim in data {}".format(ndim, self.ndim))

        self.sets = []
        if set_ids:
            if isinstance(set_ids, str):
                self.sets = [set_ids]
            elif isinstance(set_ids, list):
                self.sets = set_ids

        self.bytes = embedding_array.tobytes()
        self.timestamp = datetime.utcnow()
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.model = model
        self.version = version
        self.layer = layer

        json_object_for_embedding_id = {
            'model': self.model,
            'version': self.version,
            'asset_id': self.asset_id,
            'ndim': self.ndim,
            'layer': self.layer}

        embeddings_hash = get_md5_from_json_object(
            json_object=json_object_for_embedding_id)

        self.id = str(
            hash_string_into_positive_integer_reproducible(embeddings_hash))
        self.metadata = {
                'id': self.id,
                'timestamp': self.timestamp,
                'sets': self.sets,
                'tags': [self.layer] if self.layer else [],
                'media_type': self.asset_type,
                'asset_id': self.asset_id,
                'model': self.model,
                'version': self.version,
                'ndim': self.ndim,
                'index_name': get_similarity_index_name(
                    media_type=self.asset_type,
                    model=self.model,
                    version=self.version)}
