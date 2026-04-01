This repository is structured for modularity: `app.py` orchestrates views; `tippelaget/core` contains Cognite client, config, and data helpers; `tippelaget/ui` centralizes plotting theme/helpers; `tippelaget/views` holds metrics visualizations and LLM assistants; `.streamlit/config.toml` defines theme/server settings.

A separate React + FastAPI UI lives under `tippelaget-web/`. Python dependencies for that API are optional extras on the same Poetry project: `poetry install --extras web`. Deployment target: **GitHub Pages** (frontend) + **Google Cloud Run** (API); see `tippelaget-web/README.md`.

```
.
├── app.py
├── tippelaget/
│   ├── core/
│   │   ├── client.py
│   │   ├── config.py
│   │   └── data.py
│   ├── ui/
│   │   └── plotting.py
│   └── views/
│       ├── metrics.py
│       └── assistants.py
├── tippelaget-web/
│   ├── api/
│   └── frontend/
└── .streamlit/
    └── config.toml
```
