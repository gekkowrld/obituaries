#!/usr/bin/env python3

import argparse
import random
import sqlite3

from faker import Faker

fake = Faker()


def f_init(conn):
    """Initialize database schema"""
    cur = conn.cursor()
    with open("init.sql", "r") as isql_file:
        sql_script = isql_file.read()
        cur.executescript(sql_script)
        conn.commit()


def generate_fake_content():
    """Generate fake markdown-like content"""
    content = ""
    for _ in range(random.randint(4, 30)):
        subheading = fake.sentence(nb_words=8, variable_nb_words=True)
        subheading = f"## {subheading}\n"
        paras = ""
        for _ in range(random.randint(3, 20)):
            paras += fake.paragraph(
                nb_sentences=random.randint(3, 10), variable_nb_sentences=True
            )
            paras += "\n\n"
        content += f"{subheading}{paras}\n"
    return content


def lie(table_name: str, database_file: str, rounds: int, flash: bool = False):
    """Insert fake records into database"""
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()

    if flash:
        f_init(conn)

    for _ in range(rounds):
        name = fake.name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
        dod = fake.date_between(start_date="-90y", end_date="today")
        content = f"# {fake.sentence(nb_words=7, variable_nb_words=True)}\n\n{generate_fake_content()}"
        author = fake.name()
        slug = fake.slug()

        cur.execute(
            f"""
            INSERT INTO {table_name} (name, date_of_birth, date_of_death, content, author, slug)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (name, dob, dod, content, author, slug),
        )

    conn.commit()
    conn.close()
    print(
        f"Inserted {rounds} record(s) into the '{table_name}' table in '{database_file}'."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and insert fake records into SQLite database."
    )
    parser.add_argument(
        "--table",
        type=str,
        default="obituaries",
        help="Name of the table to insert records into (default: 'obituaries')",
    )
    parser.add_argument(
        "--database",
        type=str,
        default="obituary_platform",
        help="Path to the SQLite database file (default: 'obituary_platform')",
    )
    parser.add_argument(
        "--num",
        type=int,
        default=1,
        help="Number of fake entries to generate and insert (default: 1)",
    )
    parser.add_argument(
        "--flash",
        action="store_true",
        help="Initialize database schema before inserting",
    )

    args = parser.parse_args()

    lie(args.table, args.database, args.num, args.flash)
