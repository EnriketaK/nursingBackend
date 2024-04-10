## Installation of AI library

Create a virtual environment:
```
python3 -m venv venv
```

In the `venv` directory, create a `pip.conf` file with the following content.

```
[global]
extra-index-url = [RECEIVE FROM SAP]
trusted-host = [RECEIVE FROM SAP]
```

Activate the virtual environment via `source venv/bin/activate`. Now run:
```
pip install "sap-llm-commons[all]"
```

## Further installations

pip install djangorestframework

pip install pymysql

pip install django-cors-headers


## Download source code

As a zip file or by git

## Get into the nursingHelper folder path and run this project

python manage.py runserver 8080






