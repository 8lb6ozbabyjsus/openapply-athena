from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# def get_directory_structure(rootdir):
#     rootdir = Path(rootdir)
#     dir_structure = []
#     for path in sorted(rootdir.rglob('*')):
#         dir_structure.append(str(path))
#     return dir_structure

@app.get("/files")
def read_files():
    return JSONResponse(200) 
    # files = get_directory_structure(".")
    # return JSONResponse(content=files)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
