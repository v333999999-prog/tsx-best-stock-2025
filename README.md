# TSX Top Momentum Web App

## How to run locally

1. Install Python 3.9+ and pip
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   streamlit run main_streamlit.py
4. Open your browser at http://localhost:8501

## Deployment

Use Render.com (Free plan) or any cloud hosting:
- Build command: pip install -r requirements.txt
- Start command: streamlit run main_streamlit.py --server.port $PORT --server.address 0.0.0.0
