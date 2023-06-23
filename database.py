import sqlite3

conn = sqlite3.connect('database.db')

c = conn.cursor()

c.execute("""CREATE TABLE status_text(
    check_usb text,
    get_file text,
    download_status text,
    ind text,
    choice text,
    spotify_playlist text
)""")

c.execute("""CREATE TABLE users(
    user text,
    add_user text
)""")

c.execute("""CREATE TABLE chosen_id(
    chosen_id text
)""")

conn.commit()
conn.close()