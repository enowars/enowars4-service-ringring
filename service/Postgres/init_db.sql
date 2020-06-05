CREATE SCHEMA ringring;

CREATE TABLE ringring.alarms
(
    session_id text,
    alarm_time text,
    alarm_text text
);

CREATE TABLE ringring.sessions
(
    session_id text,
    started     timestamptz DEFAULT now(),
    is_billable boolean CHECK ( is_billable != is_vip ) DEFAULT TRUE,
    is_vip     boolean DEFAULT FALSE
);
