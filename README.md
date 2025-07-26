# Deploy Flask on Seenode in seconds

This is a repo for deploying a minimal but production-ready Python Flask application for deployment on [Seenode](https://seenode.com).

This example demonstrates how to deploy a simple Flask app using Gunicorn as the WSGI server for a robust production environment.

### Deploy in minutes
View our [guide on deploying flask apps](https://seenode.com/docs/frameworks/python/flask/) on [seenode](https://seenode.com) in seconds.


## How to Deploy on Seenode

1.  **Connect Your Repository**: Go to the [Seenode dashboard](https://cloud.seenode.com), select **New Web Service**, and choose this Git repository.
2.  **Confirm Settings**: Seenode will detect the Python environment and suggest the correct commands.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app --bind 0.0.0.0:80`
3.  **Deploy**: Click **Create Web Service**.

That's it! Your Flask app will be deployed and available at a public URL.

### Key Features on Seenode

*   **Production-Ready**: By using Gunicorn in the start command, you are running a production-grade server without any complex configuration.
*   **Port Binding**: This example is configured to listen on port 80. Ensure your application code binds to this port, or whatever port you set when deploying your application.
*   **Seamless Scaling**: Scale your service horizontally or vertically with a few clicks from the Seenode dashboard as your traffic grows.
