from datetime import datetime
from utils import connect, insert_movie

# Connect to the cluster
cluster, session = connect()

# Create Keyspace
KEYSPACE = "cinema"
session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '2' }}
""")

# Connect to the keyspace
session.set_keyspace(KEYSPACE)

# Re-create tables
session.execute("DROP TABLE IF EXISTS reservations;")
session.execute("DROP TABLE IF EXISTS movies;")
session.execute("DROP TABLE IF EXISTS users;")
session.execute("DROP TABLE IF EXISTS reservations_by_user;")
session.execute("DROP TABLE IF EXISTS movie_lookup;")

session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username text PRIMARY KEY
    );
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        title text,
        screening_timestamp timestamp,
        movie_id uuid,
        PRIMARY KEY ((title), screening_timestamp)
    );
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        movie_id uuid,
        seat text,
        user text,
        PRIMARY KEY ((movie_id), seat)
    );
""")

session.execute("""
    CREATE TABLE reservations_by_user (
        user text,
        movie_id uuid,
        seat text,
        PRIMARY KEY ((user), movie_id, seat)
    );
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS movie_lookup (
        movie_id uuid PRIMARY KEY,
        title text,
        screening_timestamp timestamp
    );
""")

print("Keyspace and tables created successfully.")

# Populate movies
sample_data = [
    ("Inception", datetime(2025, 6, 15, 17, 0)),
    ("Inception", datetime(2025, 6, 15, 20, 0)),
    ("Dark Knight", datetime(2025, 6, 16, 17, 0)),
    ("Dark Knight", datetime(2025, 6, 16, 21, 0)),
    ("Interstellar", datetime(2025, 6, 17, 18, 30)),
]

for title, timestamp in sample_data:
    _ = insert_movie(session, title, timestamp)

print("Sample movie data loaded.")
cluster.shutdown()
