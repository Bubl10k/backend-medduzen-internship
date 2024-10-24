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
    docker-compose build
  ```

#### 4. Run the Application:
 ```bash
    docker-compose up
  ```
## Running Tests

To run tests, run the following command

```bash
  docker run --rm django-medduzen python3 manage.py test
```

