This repository is structured for modularity: `app.py` orchestrates views; `tippelaget/core` contains Cognite client, config, and data helpers; `tippelaget/ui` centralizes plotting theme/helpers; `tippelaget/views` holds metrics visualizations and LLM assistants; `.streamlit/config.toml` defines theme/server settings.

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
└── .streamlit/
    └── config.toml
```
