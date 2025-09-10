from typing import Optional

import streamlit as st
from cognite.client import CogniteClient, ClientConfig

from .config import get_cognite_client_config


@st.cache_resource
def get_client() -> CogniteClient:
    """Create and cache a CogniteClient instance."""
    client_config_dict = get_cognite_client_config()
    client_config = ClientConfig.load(client_config_dict)
    return CogniteClient(config=client_config)


