#!/usr/bin/env python3

import os
import pymysql
from dotenv import load_dotenv
from uuid import uuid4
import datetime

# Load environment variables from a .env file
load_dotenv()

class DatabaseConnection:
    """
    A class-based context manager to handle database connections.
    Automatically opens and closes connections to ensure safe
    resource management.
    """
    def __init__(self, DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE):
        """
        Initializes the context manager.
        """
        self.DB_HOST = DB_HOST
        self.DB_USER = DB_USER
        self.DB_PASSWORD = DB_PASSWORD
        self.DB_NAME = DB_DATABASE

    def __enter__(self):
        """
        Opens the database connection when entering the context.
        """
        self.conn = pymysql.connect(
            host=self.DB_HOST,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection when exiting the context.
        """
        if self.conn:
            self.conn.close()

        if exc_type:
            print(f"Error: {exc_type}, {exc_val}")
            return False  # Propagate the exception

        return True  # Suppress exceptions if none occurred


def insert_listing(cursor, start_location, destination, total_price):
    """
    Insert a new listing into the database.
    """
    listing_id = str(uuid4())  # Generate a unique listing ID
    created_at = updated_at = datetime.datetime.now()

    query = """
    INSERT INTO listings_listing (listing_id, start_location, destination, total_price, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (listing_id, start_location, destination, total_price, created_at, updated_at))
    return listing_id  # Return the listing ID for further use (e.g., in Booking or Review)


def insert_booking(cursor, listing_id, start_date, end_date, status):
    """
    Insert a new booking for a specific listing into the database.
    """
    booking_id = str(uuid4())  # Generate a unique booking ID
    created_at = datetime.datetime.now()

    query = """
    INSERT INTO listings_booking (booking_id, listing_id, start_date, end_date, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (booking_id, listing_id, start_date, end_date, status, created_at))


def insert_review(cursor, listing_id, rating, comment):
    """
    Insert a new review for a specific listing.
    """
    review_id = str(uuid4())  # Generate a unique review ID
    created_at = datetime.datetime.now()

    query = """
    INSERT INTO listings_review (review_id, listing_id, rating, comment, created_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (review_id, listing_id, rating, comment, created_at))


# Using the DatabaseConnection context manager to interact with the DB
with DatabaseConnection(DB_HOST=os.getenv('DB_HOST'),
                        DB_USER=os.getenv('DB_USER'),
                        DB_PASSWORD=os.getenv('DB_PASSWORD'),
                        DB_DATABASE=os.getenv('DB_NAME')) as connection:
    # Create a cursor object to execute queries
    cursor = connection.cursor()

    # Insert new listings (example data)
    listing_1_id = insert_listing(cursor, start_location="New York", destination="Paris", total_price=1500.00)
    listing_2_id = insert_listing(cursor, start_location="London", destination="Tokyo", total_price=2000.00)

    # Insert bookings for those listings
    insert_booking(cursor, listing_id=listing_1_id, start_date="2024-01-15", end_date="2024-01-22", status="confirmed")
    insert_booking(cursor, listing_id=listing_2_id, start_date="2024-02-10", end_date="2024-02-17", status="pending")

    # Insert reviews for those listings
    insert_review(cursor, listing_id=listing_1_id, rating=5, comment="Fantastic experience!")
    insert_review(cursor, listing_id=listing_2_id, rating=4, comment="Great place, but a bit too expensive.")

    # Commit the changes to the database
    connection.commit()

    print("Data inserted successfully.")
