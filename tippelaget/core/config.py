import streamlit as st


def get_cognite_client_config() -> dict:
    """Load Cognite client configuration from Streamlit secrets."""
    return {
        "client_name": "tippelaget_app",
        "project": st.secrets["cognite"]["project"],
        "base_url": st.secrets["cognite"]["base_url"],
        "credentials": {
            "client_credentials": {
                "client_id": st.secrets["cognite"]["client_id"],
                "client_secret": st.secrets["cognite"]["client_secret"],
                "token_url": st.secrets["cognite"]["token_url"],
                "scopes": [
                    "https://bluefield.cognitedata.com/.default",
                ],
            }
        },
    }


# Default Data Model View identifiers
DEFAULT_SPACE = "tippelaget_space_name"
DEFAULT_VIEW = "Bet"
DEFAULT_VIEW_VERSION = "fcb537cee9eba5"


# OpenAI models
OPENAI_PROPhet_MODEL = "gpt-4.1-mini"
OPENAI_KING_MODEL = "gpt-5-mini"


