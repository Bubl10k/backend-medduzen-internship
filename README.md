# backend-medduzen-internship

## Requirements

- Python 3.10 or higher
- `pip` (Python package installer)
- Docker


## Installation

#### 1. Clone the Repository:


```bash
  git clone https://github.com/Bubl10k/backend-medduzen-internship.git
```

#### 2. Create a virtual environment:

```bash
  python3 -m venv venv
```

#### 3. Build the Docker Image
  ```bash
    docker build --tag django-medduzen .
  ```

#### 4. Run the Application:
 ```bash
    docker run --publish 8000:8000 django-medduzen
  ```

## Running Migrations

To create migrations manually, run the following command

```bash
  docker run --rm django-medduzen python3 manage.py makemigrations
```

To migrate, run the following command

```bash
  docker run --rm django-medduzen python3 manage.py migrate
```

## Running Tests

To run tests, run the following command

```bash
  docker run --rm django-medduzen python3 manage.py test
```

