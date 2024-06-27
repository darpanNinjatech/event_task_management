# Makefile

# Define the Python interpreter to use
PYTHON = python3

# Define the Django management command to run the server
MANAGE_CMD = manage.py

# Define the port to run the server on
PORT = 8000

# Install Python packages	
$(PYTHON) -m pip install -r requirements.txt

# Run to create cache table 
$(PYTHON) $(MANAGE_CMD) createcachetable

# Run Django database migrations command
$(PYTHON) $(MANAGE_CMD) migrate

# Run the custom command for load the data in the database
$(PYTHON) $(MANAGE_CMD) store_events

# Django project server
$(PYTHON) $(MANAGE_CMD) runserver $(PORT)
