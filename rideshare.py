class User:
    def __init__(self, user_id: int, username: str, password: str):
        self.user_id = user_id
        self.username = username
        self.password = password

    def validate_password(self, password: str) -> bool:
        return self.password == password

class Rider(User):
    def __init__(self, user_id: int, username: str, password: str):
        super().__init__(user_id, username, password)

class Driver(User):
    def __init__(self, user_id: int, username: str, password: str, name: str):
        super().__init__(user_id, username, password)
        self.name = name
        self.current_trip = None
        self.is_accepting_rider = True

    def get_id(self):
        return self.user_id

    def set_current_trip(self, trip):
        self.current_trip = trip

    def get_current_trip(self):
        return self.current_trip

    def set_accepting_rider(self, is_accepting):
        self.is_accepting_rider = is_accepting

    def is_available(self):
        return self.is_accepting_rider and self.current_trip is None

class Admin(User):
    pass

class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user: User):
        self.users[user.user_id] = user

    def authenticate(self, username: str, password: str) -> User:
        for user in self.users.values():
            if user.username == username and user.validate_password(password):
                return user
        return None

class Trip:
    def __init__(self, trip_id: str, rider: Rider, driver: Driver, origin: str, destination: str, seats: int, fare: float):
        self.trip_id = trip_id
        self.rider = rider
        self.driver = driver
        self.origin = origin
        self.destination = destination
        self.seats = seats
        self.fare = fare
        self.status = "IN_PROGRESS"

    def update_trip(self, origin: str, destination: str, seats: int):
        self.origin = origin
        self.destination = destination
        self.seats = seats

    def withdraw_trip(self):
        self.status = "WITHDRAWN"

    def end_trip(self):
        self.status = "COMPLETED"

    def get_id(self):
        return self.trip_id

    def get_status(self):
        return self.status

    def get_rider(self):
        return self.rider

    def get_driver(self):
        return self.driver

    def get_fare(self):
        return self.fare

class RiderManager:
    def __init__(self):
        self.riders = {}

    def create_rider(self, rider: Rider):
        self.riders[rider.user_id] = rider

    def get_rider(self, rider_id: int) -> Rider:
        return self.riders.get(rider_id, None)

class DriverManager:
    def __init__(self):
        self.drivers = {}

    def create_driver(self, driver: Driver):
        self.drivers[driver.user_id] = driver

    def update_driver_availability(self, driver_id: int, is_available: bool):
        driver = self.get_driver(driver_id)
        if driver:
            driver.set_accepting_rider(is_available)

    def get_driver(self, driver_id: int) -> Driver:
        return self.drivers.get(driver_id, None)

    def get_available_drivers(self) -> list:
        return [driver for driver in self.drivers.values() if driver.is_available()]

class TripManager:
    def __init__(self, rider_manager: RiderManager, driver_manager: DriverManager):
        self.trips = {}
        self.rider_manager = rider_manager
        self.driver_manager = driver_manager
        self.trip_counter = 0

    def create_trip(self, rider_id: int, origin: str, destination: str, seats: int) -> str:
        rider = self.rider_manager.get_rider(rider_id)
        available_drivers = self.driver_manager.get_available_drivers()

        if not rider or not available_drivers:
            return None

        self.trip_counter += 1
        trip_id = str(self.trip_counter)
        driver = available_drivers[0]  # Assign the first available driver
        fare = self.calculate_fare(origin, destination, seats)
        trip = Trip(trip_id, rider, driver, origin, destination, seats, fare)
        self.trips[trip_id] = trip
        driver.set_current_trip(trip)
        return trip_id

    def withdraw_trip(self, trip_id: str):
        trip = self.trips.get(trip_id, None)
        if trip:
            trip.withdraw_trip()
            trip.driver.set_current_trip(None)

    def end_trip(self, trip_id: str):
        trip = self.trips.get(trip_id, None)
        if trip:
            trip.end_trip()
            trip.driver.set_current_trip(None)

    def trip_history(self, rider: Rider) -> list:
        return [trip for trip in self.trips.values() if trip.get_rider() == rider]

    def calculate_fare(self, origin: str, destination: str, seats: int) -> float:
        # Implement a simple fare calculation based on string lengths for illustration
        return abs(len(destination) - len(origin)) * seats * 1.5

# CLI Functions

def rider_cli(user: User, rider_manager: RiderManager, driver_manager: DriverManager, trip_manager: TripManager):
    rider = user
    while True:
        print("\nRider Menu:")
        print("1. Request Ride")
        print("2. View Trip History")
        print("3. Withdraw Ride Request")
        print("4. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            origin = input("Enter origin: ")
            destination = input("Enter destination: ")
            seats = int(input("Enter number of seats: "))
            trip_id = trip_manager.create_trip(rider.get_id(), origin, destination, seats)
            if trip_id:
                print(f"Ride requested successfully with Trip ID: {trip_id}")
            else:
                print("Failed to request ride.")
        elif choice == '2':
            trips = trip_manager.trip_history(rider)
            if trips:
                for trip in trips:
                    print(f"Trip ID: {trip.get_id()}, Status: {trip.get_status()}")
            else:
                print("No trip history.")
        elif choice == '3':
            trip_id = input("Enter Trip ID to withdraw: ")
            trip_manager.withdraw_trip(trip_id)
        elif choice == '4':
            break
        else:
            print("Invalid option!")

def driver_cli(user: User, driver_manager: DriverManager, trip_manager: TripManager):
    driver = user
    while True:
        print("\nDriver Menu:")
        print("1. View Current Trip")
        print("2. Complete Current Trip")
        print("3. Set Availability")
        print("4. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            trip = driver.get_current_trip()
            if trip:
                print(f"Current Trip ID: {trip.get_id()}, Status: {trip.get_status()}")
            else:
                print("No current trip.")
        elif choice == '2':
            trip = driver.get_current_trip()
            if trip:
                trip_manager.end_trip(trip.get_id())
                print(f"Trip ID: {trip.get_id()} completed.")
            else:
                print("No trip to complete.")
        elif choice == '3':
            is_available = input("Set availability (y/n): ").lower() == 'y'
            driver.set_accepting_rider(is_available)
            print(f"Driver availability set to {is_available}.")
        elif choice == '4':
            break
        else:
            print("Invalid option!")

def admin_cli(user: User, trip_manager: TripManager):
    while True:
        print("\nAdmin Menu:")
        print("1. Manage Users (Mockup)")
        print("2. Monitor Rides (Mockup)")
        print("3. Generate Reports (Mockup)")
        print("4. Enforce Policy (Mockup)")
        print("5. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            print("Manage Users: This feature is a placeholder.")
        elif choice == '2':
            print("Monitor Rides: This feature is a placeholder.")
        elif choice == '3':
            print("Generate Reports: This feature is a placeholder.")
        elif choice == '4':
            print("Enforce Policy: This feature is a placeholder.")
        elif choice == '5':
            break
        else:
            print("Invalid option!")

def main():
    # Setup
    user_manager = UserManager()
    rider_manager = RiderManager()
    driver_manager = DriverManager()
    trip_manager = TripManager(rider_manager, driver_manager)
    admin = Admin(user_id=1, username="admin", password="admin123")
    user_manager.add_user(admin)

    # Create Users
    rider1 = Rider(user_id=2, username="rider1", password="pass123")
    driver1 = Driver(user_id=3, username="driver1", password="pass123", name="Driver 1")
    rider_manager.create_rider(rider1)
    driver_manager.create_driver(driver1)
    user_manager.add_user(rider1)
    user_manager.add_user(driver1)

    while True:
        print("\nWelcome to RideShare!")
        print("1. Login")
        print("2. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = user_manager.authenticate(username, password)
            if user:
                if isinstance(user, Rider):
                    rider_cli(user, rider_manager, driver_manager, trip_manager)
                elif isinstance(user, Driver):
                    driver_cli(user, driver_manager, trip_manager)
                elif isinstance(user, Admin):
                    admin_cli(user, trip_manager)
            else:
                print("Authentication failed.")
        elif choice == '2':
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
