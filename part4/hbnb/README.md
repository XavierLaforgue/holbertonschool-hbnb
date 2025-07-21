# HBnB Evolution

## Installation
#### 0. Install python 3.10.12 and sqlite 3.37.2
#### 1. Clone the repository
```
git clone https://github.com/Delphes1980/holbertonschool-hbnb.git desired_folder_name
```
then
```
cd desired_folder_name/part3/hbnb/
```

#### 2. Create and activate a virtual environment
```
python3 -m venv venv
```
then
```
source venv/bin/activate
```

#### 3. Install dependencies
```
pip install -r requirements.txt
```

#### 4. Initialize the database
On your terminal, type down the following command:
```
mkdir instance; sqlite3 instance/development.db < create_tables.sql
```

#### 5. Application utilisation
From the hbnb directory (within part3), run:
```
python run.py
```
The API will be available at http://127.0.0.1:5000/api/v1.
