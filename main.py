from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path

app = FastAPI()

def get_directory_structure(rootdir):
    rootdir = Path(rootdir)
    dir_structure = []
    for path in sorted(rootdir.rglob('*')):
        dir_structure.append(str(path))
    return dir_structure

@app.get("/files")
def read_files():
    files = get_directory_structure(".")
    return JSONResponse(content=files)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
