## 🎬 Distributed Cinema Reservation System

This is a distributed console-based cinema reservation system using Apache Cassandra. It supports:
- Viewing available movies and screenings
- Selecting seats from a visual grid
- Making, viewing, and canceling reservations
- Stress testing concurrent bookings across distributed nodes

## 🚀 How to Run

### 1. Start the Cassandra cluster

```bash
docker compose up -d
```

The nodes will be ready to be used when the following script returns corresponding output:

```bash
docker exec -ti cas2 nodetool status  # should be run on working node e.g., cas2
```

### 2. Set up Python environment

```bash
python -m venv venv

venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
```

### 3. Initialize and populate the database

```bash
python main.py
```

### 4. Run the application

```bash
python user_console.py --user alice
```

Run it in another terminal for a second user:

```bash
python user_console.py --user bob
```

### 5. Run stress tests (optional)

```bash
python stress_tests.py
```