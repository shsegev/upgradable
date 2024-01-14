from fabric.operations import sudo
from fabric.api import env
import logging
import os
import signal
from distutils.version import StrictVersion

import fastapi
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import docker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

upgrade_requested = False


@app.get("/hello_world")
def hello_world():
    logger.info("Received request for hello_world")
    return {"message": "Hello, World!"}


@app.get("/bye_world")
def bye_world():
    logger.info("Received request for bye_world")
    return {"message": "Goodbye, World!"}


@app.post("/upload_new")
async def upload_new(file: UploadFile = File(...)):
    # try:
    #     logger.info(f"Received request for upload_new with file: {file.filename}")
    #
    #     # Save the uploaded file to /tmp folder in the container
    #     file_path = f"/tmp/{file.filename}"
    #     with open(file_path, "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
    # finally:
    #     file.file.close()
    global upgrade_requested
    logger.info(f"File loaded")
    client = docker.from_env()
    client.images.load(file.file)
    logger.info(f"Image loaded")
    # os.remove(file_path)
    # search images for the one we just loaded
    images = client.images.list(name="upservice")
    highest_version = None
    highest_version_tag = None
    for image in images:
        for tag in image.tags:
            # Extract version number from the tag
            version_str = tag.split(':')[-1]

            try:
                version = StrictVersion(version_str)
                if highest_version is None or version > highest_version:
                    highest_version = version
                    highest_version_tag = tag
            except ValueError:
                # Ignore tags that are not valid version numbers
                pass

    logger.info(f"highest version tag: {highest_version_tag}")
    last_image = client.images.get(highest_version_tag)
    last_image.tag("upservice:latest")
    upgrade_requested = True
    os.kill(os.getpid(), signal.SIGTERM)
    return JSONResponse(content={"message": "File uploaded successfully!"})


def my_shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')


@app.on_event('shutdown')
def on_shutdown():
    global upgrade_requested
    print('Server shutting down...')
    if upgrade_requested:
        env.host_string = os.getenv("UNIT_HOST",'nvidia@localhost:6122')
        env.password = os.getenv('UNIT_PASSWORD', 'nvidia')
        sudo("docker rename upservice upservice_old")
        sudo("docker update --restart=no upservice_old")
        sudo("docker run --restart always --privileged --network host -d   \
         -v /var/run/docker.sock:/var/run/docker.sock\
         --name upservice upservice:latest")


app.add_api_route('/shutdown', my_shutdown, methods=['GET'])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)
    print("Server exiting...")

