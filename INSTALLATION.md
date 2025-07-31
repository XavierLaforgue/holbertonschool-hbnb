# HBnB Evolution - Installation
## 0. Use python 3.13.3 and sqlite 3.37.2
This application has been tested on python 3.13.3.
If you try to use a different python version results are not
guaranteed.
If your system's python version is different, the use of a `pyenv` with
python 3.13.3 is highly recommended.

## 1. Clone the repository
```
git clone https://github.com/XavierLaforgue/holbertonschool-hbnb.git desired_folder_name
```
then
```
cd desired_folder_name/part4/hbnb/
```

## 2. Create and activate a virtual environment
Use the `python` call approppriate to your system (typically `python` or `python3`)
```
python3 -m venv venv
```
then
```
source venv/bin/activate
```

## 3. Install dependencies
```
pip install -r requirements.txt
```

## 4. Initialize the database
On your terminal, type down the following command:
```
mkdir instance; sqlite3 instance/development.db < create_tables.sql
```

## 5. Application utilisation
From the hbnb directory (within part4), run:
```
python run.py
```
The web client will be available at http://127.0.0.1:5000/ while the
api Swagger documentation lies at http://127.0.0.1:5000/api/v1.
