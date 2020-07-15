CREATE SCHEMA IF NOT EXIST ringring;

CREATE TABLE IF NOT EXIST ringring.alarms
(
    session_id text,
    alarm_time text,
    alarm_text text
);

CREATE TABLE IF NOT EXIST ringring.sessions
(
    session_id text,
    started     timestamptz DEFAULT now(),
    is_billable boolean CHECK ( is_billable != is_vip ) DEFAULT TRUE,
    is_vip     boolean DEFAULT FALSE
);

CREATE INDEX IF NOT EXIST ON ringring.sessions(session_id);
CREATE INDEX IF NOT EXIST ON ringring.alarms(session_id);
