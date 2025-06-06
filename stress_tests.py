import threading
import random
from datetime import datetime
from utils import connect, insert_movie, insert_movie, insert_reservation, cleanup_test_reservations, SEATS

# Stress test 1: Single user spamming same seat
def stress_test_1():
    print("Stress test 1: Single user spamming same seat")
    cluster, session = connect('cinema')
    movie_id = insert_movie(session, "StressTest1", datetime(2025, 6, 20, 10, 0))
    user = "tester1"
    seat = "A1"
    success = 0

    for _ in range(50):
        if insert_reservation(session, movie_id, seat, user):
            success += 1

    print(f"{user} successfully reserved {success}/50 times (should be 1)")
    cleanup_test_reservations(session, movie_id, [user])
    cluster.shutdown()

# Stress test 2: Multiple users reserving random seats
def stress_test_2():
    print("Stress test 2: Multiple users reserving random seats")
    cluster, session = connect('cinema')
    movie_id = insert_movie(session, "StressTest2", datetime(2025, 6, 20, 11, 0))

    def reserve_random_seats(user):
        reserved = 0
        for _ in range(25):
            seat = random.choice(SEATS)
            if insert_reservation(session, movie_id, seat, user):
                reserved += 1
        print(f"{user} reserved {reserved} seat(s)")

    threads = [
        threading.Thread(target=reserve_random_seats, args=("random1",)),
        threading.Thread(target=reserve_random_seats, args=("random2",)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    cleanup_test_reservations(session, movie_id, ["random1", "random2"])
    cluster.shutdown()

# Stress test 3: Two users race to book all seats
def stress_test_3():
    print("Stress test 3: Two users racing to book all seats")
    cluster, session = connect('cinema')
    movie_id = insert_movie(session, "StressTest3", datetime(2025, 6, 20, 12, 0))

    def book_all_seats(user):
        reserved = 0
        for seat in SEATS:
            if insert_reservation(session, movie_id, seat, user):
                reserved += 1
        print(f"{user} reserved {reserved} seat(s)")

    threads = [
        threading.Thread(target=book_all_seats, args=("speedy1",)),
        threading.Thread(target=book_all_seats, args=("speedy2",)),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    cleanup_test_reservations(session, movie_id, ["speedy1", "speedy2"])
    cluster.shutdown()


if __name__ == "__main__":
    print("Running all stress tests...\n")
    stress_test_1()
    print("\n" + "-"*50 + "\n")
    stress_test_2()
    print("\n" + "-"*50 + "\n")
    stress_test_3()
    print("\nAll tests completed.")
