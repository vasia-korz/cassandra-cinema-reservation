from cassandra.cluster import Cluster
import uuid
import time

SEATS = [f"{row}{col}" for row in "ABCDE" for col in range(1, 11)]

def connect(keyspace=None):
    cluster = Cluster(['127.0.0.1', '127.0.0.2'], port=9042)
    session = cluster.connect(keyspace) if keyspace else cluster.connect()
    return cluster, session

def insert_movie(session, title, timestamp):
    movie_id = uuid.uuid4()
    session.execute(
        "INSERT INTO movies (title, screening_timestamp, movie_id) VALUES (%s, %s, %s)",
        (title, timestamp, movie_id)
    )
    session.execute(
        "INSERT INTO movie_lookup (movie_id, title, screening_timestamp) VALUES (%s, %s, %s)",
        (movie_id, title, timestamp)
    )
    return movie_id

def insert_reservation(session, movie_id, seat, user):
    for _ in range(3):  # max 3 tries
        try:
            result = session.execute("""
                INSERT INTO reservations (movie_id, seat, user)
                VALUES (%s, %s, %s)
                IF NOT EXISTS
            """, (movie_id, seat, user))
            row = result.one()
            if row.applied:
                session.execute("""
                    INSERT INTO reservations_by_user (user, movie_id, seat)
                    VALUES (%s, %s, %s)
                """, (user, movie_id, seat))
                return True
            return False
        except Exception as e:
            if "CAS operation result is unknown" in str(e):
                print(f"Unknown CAS result on seat {seat}, retrying...")
                time.sleep(0.1)
                continue
            raise

    return False



def delete_reservation(session, movie_id, user, seat):
    applied = session.execute("""
        DELETE FROM reservations WHERE movie_id = %s AND seat = %s
    """, (movie_id, seat))
    if applied:
        session.execute("""
            DELETE FROM reservations_by_user WHERE user = %s AND movie_id = %s AND seat = %s
        """, (user, movie_id, seat))
    
    return applied

def cleanup_test_reservations(session, movie_id, users):
    for seat in SEATS:
        session.execute("""
            DELETE FROM reservations WHERE movie_id = %s AND seat = %s
        """, (movie_id, seat))

    for user in users:
        for seat in SEATS:
            session.execute("""
                DELETE FROM reservations_by_user WHERE user = %s AND movie_id = %s AND seat = %s
            """, (user, movie_id, seat))

    result = session.execute("""
        SELECT title, screening_timestamp FROM movie_lookup WHERE movie_id = %s
    """, (movie_id,)).one()

    session.execute("""
        DELETE FROM movie_lookup WHERE movie_id = %s
    """, (movie_id,))

    if result:
        session.execute("""
            DELETE FROM movies WHERE title = %s AND screening_timestamp = %s
        """, (result.title, result.screening_timestamp))
