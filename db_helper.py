import psycopg2
import os
from psycopg2 import sql


def get_alarms(session_id):
    conn = psycopg2.connect(f"dbname='postgres' user='postgres' host='localhost' password={os.environ['PGPASSWORD']}")
    cur = conn.cursor()
    query = sql.SQL("""
    SELECT alarm_text, alarm_time FROM ringring.alarms
    WHERE session_id = {session_id}
    """).format(session_id=sql.Literal(session_id))
    cur.execute(query)
    data = []
    for result in cur.fetchall():
        data.append({'text': result[0],
                     'time': result[1]})
    conn.commit()
    conn.close()

    return data


def insert_alarm(session_id, time, text):
    conn = psycopg2.connect(f"dbname='postgres' user='postgres' host='localhost' password={os.environ['PGPASSWORD']}")
    cur = conn.cursor()
    query = sql.SQL("""
    INSERT INTO ringring.alarms (session_id, alarm_time, alarm_text) 
    VALUES (%s, %s, %s);
    """)
    cur.execute(query, (session_id, time, text))
    conn.commit()
    conn.close()
