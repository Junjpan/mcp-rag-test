Run Docker to interact with vector database:
1. Run docker desktop and play the container that is related to this app
2. Run below command if you don't have a container that is already set up for this app. 
For window bash
```
docker run -p 6333:6333 -p 6334:6334 \
    -v /$(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```
For mac or linux terminal, or if using Git Bash
```
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```
**Port 6333** → Qdrant’s main REST API endpoint. Human-readable JSON over HTTP.
***Go to Qdrant dashboard***
http://localhost:6333/dashboard
***Go to Qdrant collection***
http://localhost:6333/collections

**Port 6334** → Qdrant’s gRPC API endpoint. gRPC is a binary protocol from Google. Faster, more efficient than REST. You don't directly use it directly in a browser - instead, you connect to if from a client library (like Python, Node.js or Go).

3. run the below command if you have have docker-compose.yaml set up, this file is doing the same thing like the docker run command above [Only apply to when you first set up] 
```
docker compose up 
```

**Correct way to stop Qdrant and Docker**:

1. Stop the Qdrant container gracefully:
Open a terminal and run:
```
docker stop <qdrant_container_name>
```
This command tells Qdrant to finish any writing and shut down cleanly.

2. Wait a few seconds to ensure all data is flushed to disk.

3. After all containers are stopped, you can safely stop Docker Desktop or shut down your computer.

**Do NOT**:

- Force quit Docker Desktop while containers are running.
- Shut down your computer without stopping containers first.


---
Setting Up Python Environment with pyenv
This project uses pyenv to manage Python versions and virtual environments. Follow these steps to set up your environment:

1. Install pyenv

Follow the [pyenv installation|https://github.com/pyenv/pyenv#installation] guide
 for your system.
For Windows, use [pyenv-win|https://github.com/pyenv-win/pyenv-win].

2. Install the required Python version

The project is configured to use Python 3.10.4 (or update to another version if needed).
```
pyenv install 3.10.4
```

3. Set local Python version

Inside the project folder, set the Python version:
```
cd myproject
pyenv local 3.10.4
```

This will create a .python-version file in the project.

4. Create a virtual environment

If you have pyenv-virtualenv installed, create a named environment:
```
pyenv virtualenv 3.10.4 myproject-env
pyenv local myproject-env
```

If you prefer the built-in venv:
```
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv/Scripts/activate    # Windows
```

5. Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

6. Running the project
```
python mcp_server.py
```

How to Safely Stop Qdrant/Docker (Prevent Data Corruption)
Why:
If you stop Docker or the Qdrant container abruptly (such as by closing Docker Desktop or shutting down your computer while Qdrant is running), you risk corrupting the Qdrant database files. This can lead to errors like ```OutputTooSmall { expected: 4, actual: 0 }``` and loss of your vector data.

