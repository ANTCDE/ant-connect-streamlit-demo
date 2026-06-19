# ant-connect-streamlit-demo

Demo Streamlit app that runs inside ANT-OS, showcasing the full `ant-connect-streamlit` API.

## Features demonstrated

- **Context** — reads user, license, project, task from the ANT-OS host
- **Signals** — toggle notepad, show overlay, navigate to routes/apps
- **Notifications** — success, error, warning, info toasts via host
- **Toolbar** — set title, subtitle, menu items with actions
- **HTTP proxy** — fetch project data through the host's authenticated Axios

## Quick start

```bash
# Clone
git clone https://github.com/ANTCDE/ant-connect-streamlit-demo.git
cd ant-connect-streamlit-demo

# Install (requires uv — https://docs.astral.sh/uv/)
uv sync

# Run
uv run streamlit run app.py
```

The app runs on `http://localhost:8501` by default. In ANT-OS, load it via Developer mode at `/developer/8501`.

## Requirements

- Python >= 3.11
- ANT-OS host (the app runs inside an ANT-OS iframe)
