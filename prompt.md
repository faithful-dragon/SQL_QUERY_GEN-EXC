# Prompt 1
Generate a PostgreSQL `CREATE TABLE` statement for a table named `Reviews` with columns: `review_id` as a `SERIAL` primary key, `member_id` and `book_id` as foreign keys referencing `Members(member_id)` and `Books(book_id)` respectively, `rating` as an integer with a `CHECK` constraint between 1 and 5, `review` as text, and `review_date` with a default of `CURRENT_DATE`. Include all constraints using proper PostgreSQL syntax.

# Prompt 2
Generate a PostgreSQL CREATE TYPE statement to define an ENUM named status with values `pending`, `approved`, and `rejected`. Then, modify the existing Reviews table to add a column named status of type status with a default value of `pending`.

