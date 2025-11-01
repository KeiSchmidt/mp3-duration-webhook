from fastapi import FastAPI, Request, HTTPException
from mutagen.mp3 import MP3
import tempfile, requests, os

app = FastAPI()
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET", "changeme")

@app.post("/get-duration")
async def get_duration(request: Request):
    headers = request.headers
    token = headers.get("X-Webhook-Token", "")
    if token != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    file_url = data.get("file_url")
    if not file_url:
        raise HTTPException(status_code=400, detail="file_url missing")

    try:
        resp = requests.get(file_url, stream=True, timeout=20)
        resp.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
            tmp_path = f.name

        duration = int(MP3(tmp_path).info.length)
        try:
            os.remove(tmp_path)
        except:
            pass
        return { "duration": duration }
    except Exception as e:
        return { "error": str(e) }
