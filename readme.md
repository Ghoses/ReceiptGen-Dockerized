# ReceiptGen Dockerized

A web application to generate receipts, packaged for Docker.

## Prerequisites

*   **Git:** Must be installed to clone the repository.
*   **Docker:** Must be installed and running on your system. (See [Docker installation guide](https://docs.docker.com/engine/install/))
*   **GitHub Personal Access Token (PAT):** If cloning via HTTPS and the repository is private, or if your GitHub account requires it for HTTPS operations, you'll need a PAT with `repo` scope. (See [GitHub PAT documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens))

## Setup and Run

1.  **Clone the Repository:**

    Open your terminal or command prompt and navigate to the directory where you want to clone the project. Then run:

    ```bash
    git clone [https://github.com/Ghoses/ReceiptGen-Dockerized.git](https://github.com/Ghoses/ReceiptGen-Dockerized.git) ReceiptGen
    cd ReceiptGen
    ```
    When prompted for username and password for `https://github.com`:
    *   **Username:** Your GitHub username (e.g., `Ghoses`)
    *   **Password:** Your GitHub Personal Access Token (PAT)

2.  **Build the Docker Image:**

    In the root directory of the cloned project (where the `Dockerfile` is located), run the following command to build the Docker image. This might take a few minutes, especially on the first run, as it downloads the base image and installs dependencies.

    ```bash
    docker build -t receiptgen-app .
    ```

3.  **Run the Docker Container:**

    Once the image is built, you can start the container using the following command:

    ```bash
    docker run -d \
      --name receiptgen \
      -p 5000:5000 \
      -v "$(pwd)":/app \
      --restart always \
      receiptgen-app
    ```
    *   `-d`: Runs the container in detached mode (in the background).
    *   `--name receiptgen`: Assigns a name to your container for easier management.
    *   `-p 5000:5000`: Maps port 5000 of your host machine to port 5000 of the container.
    *   `-v "$(pwd)":/app`: **For Development/Live Changes:** Mounts the current directory (your project code on the host) into the `/app` directory in the container. This means changes you make to the code locally will be reflected live in the running container (may require a server restart within the app, or the app might handle it if it's Flask/Django in debug mode). For a "production" deployment where code doesn't change, you might omit this volume mount if the code is fully baked into the image.
    *   `--restart always`: Ensures the container restarts automatically if it stops or if the Docker daemon restarts.
    *   `receiptgen-app`: The name of the Docker image to use.

    **Note for Windows users:** `$(pwd)` in Git Bash or WSL resolves to the current directory. In Windows CMD, you might need to use `%cd%` like so: `-v "%cd%":/app`. In PowerShell, use `${PWD}`: `-v "${PWD}:/app"`. The most robust cross-platform way for local development is to specify the full absolute path to your project directory.

4.  **Access the Application:**

    Once the container is running, you should be able to access ReceiptGen in your web browser at:

    [http://localhost:5000](http://localhost:5000)

    If you are running Docker on a remote machine (like a Raspberry Pi), replace `localhost` with the IP address of that machine.

## Managing the Container

*   **Check running containers:**
    ```bash
    docker ps
    ```
*   **View container logs:**
    ```bash
    docker logs receiptgen
    ```
*   **Stop the container:**
    ```bash
    docker stop receiptgen
    ```
*   **Start a stopped container:**
    ```bash
    docker start receiptgen
    ```
*   **Remove the container (if stopped and no longer needed):**
    ```bash
    docker rm receiptgen
    ```

## Development Notes

*   The application uses Python and may rely on frameworks like Flask or similar (as suggested by `app.py` and `templates`).
*   Dependencies are listed in `requirements.txt`.
*   The `Dockerfile` installs `chromium` and `chromium-driver`, suggesting the use of web scraping or browser automation libraries (e.g., Selenium) for receipt generation.

## .gitignore

It is recommended to add a `.gitignore` file to this repository to exclude build artifacts (like `build/`, `dist/`, `*.pyc`, `__pycache__/`) and potentially local configuration files or secrets that shouldn't be committed.
