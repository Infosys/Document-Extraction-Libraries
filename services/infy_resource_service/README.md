# Infy Resource Service

## Setup

1. Create a virtual environment:

   ```
   python -m venv venv
   ```

2. Install the requirements:

   ```
   pip install -r requirements.txt
   ```

3. Run the service:
   - If you want to run the service using a script, follow the below steps:

     **NOTE:** Make sure you have bash installed on your system.
      Go through the script `infy_resource_service.sh` and make changes to the paths for your:
     - Resource service server directory.(Directory path you want to serve.)
     - Resource service port number, username and password
     - Virtual environment.(If running on Windows, change `bin` to `Scripts` in the path.)

     - You can run the service via script by opening the bash terminal in the directory and running the below command:
       ```
       ./infy_resource_service.sh start
       ```
     - You can stop the service by running the below command:
       ```
       ./infy_resource_service.sh stop
       ```
