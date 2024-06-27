# Fever Providers API

### Technology Used
 
- Python 3.10.9
- Django
- Rest API
- Django Rest Framework
- SQLite Database
- Swagger (for API documentation)


### Steps to setup the project


* To update the dependencies of the project (i.e. packages)
```
python3 -m pip install -r requirements.txt
```

* To create cache table to store last event records and update
```
python3 manage.py createcachetable
```

* Migrate the changes to the database
```
python3 manage.py migrate
```

* To run the server in your machine
```
python3 manage.py runserver 8000
```

* Run this command in another terminal to get all events data
```
python3 manage.py store_events
```

* The API is developed as per the requrement, please check below information
* Swagger documentation: ```https://localhost:PORT/swagger/```
* Django Admin Panel: ```https://localhost:PORT/admin/``` Username: ```admin``` Password: ```admin```