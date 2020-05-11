CREATE SCHEMA ringring;

CREATE TABLE ringring.alarms (session_id text, alarm_time text, alarm_text text);

CREATE TABLE ringring.sessions (sessions_id text, started timestamptz);


