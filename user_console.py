import argparse
from utils import connect, insert_reservation, delete_reservation

# Get username from command line
parser = argparse.ArgumentParser()
parser.add_argument("--user", required=True)
args = parser.parse_args()
username = args.user

# Connect to the cluster
cluster, session = connect('cinema')

def make_reservation():
    # Step 1: List all movie titles
    titles = session.execute("SELECT DISTINCT title FROM movies")
    titles = [row.title for row in titles]
    if not titles:
        print("No movies available.")
        return

    print("\nAvailable movies:")
    for idx, title in enumerate(titles, 1):
        print(f"{idx}. {title}")
    try:
        choice = int(input("Choose a movie (number): ").strip())
        title = titles[choice - 1]
    except:
        print("Invalid selection.")
        return

    # Step 2: List screening times for selected movie
    times = session.execute(
        "SELECT screening_timestamp, movie_id FROM movies WHERE title = %s",
        (title,)
    )
    times = list(times)
    if not times:
        print("No screenings found for this movie.")
        return

    print(f"\nScreenings for {title}:")
    for idx, row in enumerate(times, 1):
        print(f"{idx}. {row.screening_timestamp.strftime('%Y-%m-%d %H:%M')}")
    try:
        choice = int(input("Choose a time (number): ").strip())
        screening = times[choice - 1]
    except:
        print("Invalid selection.")
        return

    movie_id = screening.movie_id

    # Step 3: Show available seats
    all_seats = [f"{row}{col}" for row in "ABCDE" for col in range(1, 11)]
    reserved = session.execute(
        "SELECT seat FROM reservations WHERE movie_id = %s", (movie_id,)
    )
    taken = {row.seat for row in reserved}

    print("\nSeat map (XX - taken)")
    for row in "ABCDE":
        row_display = ""
        for col in range(1, 11):
            seat = f"{row}{col}"
            row_display += " XX " if seat in taken else f" {seat} "
            if col < 10:
                row_display += "|"
        print(row_display)

    # Step 4: User chooses a seat
    seat = input("\nEnter seat to reserve (e.g., A1): ").strip().upper()
    if seat not in all_seats:
        print("Invalid seat.")
        return
    if seat in taken:
        print("Seat already taken.")
        return

    # Step 5: Try to reserve it
    applied = insert_reservation(session, movie_id, seat, username)
    if applied:
        print(f":) Reservation successful: seat {seat}")
    else:
        print(":( Someone just took that seat.")

def update_reservation():
    rows = list(session.execute(
        "SELECT movie_id, seat FROM reservations_by_user WHERE user = %s",
        (username,)
    ))
    if not rows:
        print("You have no reservations to update.")
        return

    print("\nYour Reservations:")
    for i, row in enumerate(rows):
        lookup = session.execute(
            "SELECT title, screening_timestamp FROM movie_lookup WHERE movie_id = %s",
            (row.movie_id,)
        ).one()
        if lookup:
            print(f"{i + 1}. {lookup.title} on {lookup.screening_timestamp.strftime('%Y-%m-%d %H:%M')} - Seat {row.seat}")
        else:
            print(f"{i + 1}. Unknown movie - Seat {row.seat}")

    try:
        choice = int(input("Select reservation to update (number): ").strip())
        selected = rows[choice - 1]
    except:
        print("Invalid choice.")
        return

    movie_id = selected.movie_id
    old_seat = selected.seat

    success = delete_reservation(session, movie_id, username, old_seat)
    if not success:
        print("Failed to cancel.")
        return
    else:
        print(f"Choose a new seat:")

    all_seats = [f"{row}{col}" for row in "ABCDE" for col in range(1, 11)]
    reserved = session.execute(
        "SELECT seat FROM reservations WHERE movie_id = %s", (movie_id,)
    )
    taken = {row.seat for row in reserved}

    print("\nSeat map (XX - taken)")
    for row in "ABCDE":
        row_display = ""
        for col in range(1, 11):
            seat = f"{row}{col}"
            row_display += " XX " if seat in taken else f" {seat} "
            if col < 10:
                row_display += "|"
        print(row_display)

    seat = input("\nEnter new seat to reserve (e.g., A1): ").strip()
    if seat not in all_seats:
        print("Invalid seat.")
        return
    if seat in taken:
        print("Seat already taken.")
        return

    applied = insert_reservation(session, movie_id, seat, username)
    if applied:
        print(f":) Updated reservation successful: seat {seat}")
    else:
        print(":( Someone just took that seat. Try again.")

def view_all_reservations():
    rows = list(session.execute("SELECT movie_id, seat, user FROM reservations"))
    print("\nAll reservations:")
    if len(rows):
        for row in rows:
            lookup = session.execute(
                "SELECT title, screening_timestamp FROM movie_lookup WHERE movie_id = %s",
                (row.movie_id,)
            ).one()
            if lookup:
                print(f"{lookup.title} on {lookup.screening_timestamp.strftime('%Y-%m-%d %H:%M')} - Seat {row.seat} - User {row.user}")
            else:
                print(f"Unknown movie (ID: {row.movie_id}) - Seat {row.seat} - User {row.user}")
    else:
        print("There are no reservations yet.")
    print()

def view_my_reservations():
    query = "SELECT movie_id, seat FROM reservations_by_user WHERE user = %s"
    rows = list(session.execute(query, (username,)))
    print(f"\nReservations for {username}:")
    if len(rows):
        for row in rows:
            lookup = session.execute(
                "SELECT title, screening_timestamp FROM movie_lookup WHERE movie_id = %s",
                (row.movie_id,)
            ).one()
            if lookup:
                print(f"{lookup.title} on {lookup.screening_timestamp.strftime('%Y-%m-%d %H:%M')} - Seat {row.seat}")
            else:
                print(f"Unknown movie (ID: {row.movie_id}) - Seat {row.seat}")
    else:
        print("You've got no reservations yet.")
    print()

def cancel_reservation():
    # Load reservations
    rows = session.execute(
        "SELECT movie_id, seat FROM reservations_by_user WHERE user = %s",
        (username,)
    )
    rows = list(rows)
    if not rows:
        print("You have no reservations to cancel.")
        return

    print("\nYour Reservations:")
    for i, row in enumerate(rows):
        lookup = session.execute(
            "SELECT title, screening_timestamp FROM movie_lookup WHERE movie_id = %s",
            (row.movie_id,)
        ).one()
        if lookup:
            print(f"{i + 1}. {lookup.title} on {lookup.screening_timestamp.strftime('%Y-%m-%d %H:%M')} - Seat {row.seat}")
        else:
            print(f"{i + 1}. Unknown movie - Seat {row.seat}")

    try:
        choice = int(input("Select reservation to cancel (number): ").strip())
        selected = rows[choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    # Delete from both tables
    applied = delete_reservation(session, selected.movie_id, username, selected.seat)
    if applied:
        print(f":) Reservation for seat {selected.seat} canceled.")
    else:
        print(":( Could not cancel reservation (maybe already deleted or owned by someone else).")


def menu():
    while True:
        print("\nCinema Reservation")
        print("1. Make reservation")
        print("2. View all reservations")
        print("3. View my reservations")
        print("4. Cancel reservation")
        print("5. Update reservation")
        print("6. Exit")
        choice = input("Choose option: ").strip()
        if choice == '1':
            make_reservation()
        elif choice == '2':
            view_all_reservations()
        elif choice == '3':
            view_my_reservations()
        elif choice == '4':
            cancel_reservation()
        elif choice == '5':
            update_reservation()
        elif choice == '6':
            print("Bye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    print(f"Logged in as: {username}")
    menu()
    cluster.shutdown()
