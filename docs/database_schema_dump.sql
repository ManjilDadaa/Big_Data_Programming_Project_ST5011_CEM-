--
-- PostgreSQL database dump
--

\restrict chNhhK8gOJM0UPSySemyCBGkzhT9gPTjgK9fnxybBcU1OeQckTxyuErj1GL3Z69

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.10 (Ubuntu 17.10-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: trips_with_disruptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trips_with_disruptions (
    operator_name character varying,
    line_name character varying,
    origin character varying,
    destination character varying,
    trip_date date,
    weekday_name character varying,
    departure_time character varying,
    scheduled_datetime timestamp without time zone,
    service_code character varying,
    is_disrupted integer,
    reason character varying,
    planned boolean,
    severity character varying,
    overlap_duration_minutes double precision
);


--
-- PostgreSQL database dump complete
--

\unrestrict chNhhK8gOJM0UPSySemyCBGkzhT9gPTjgK9fnxybBcU1OeQckTxyuErj1GL3Z69

