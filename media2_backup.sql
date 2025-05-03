--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

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

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: announcements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcements (
    id integer NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.announcements OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.announcements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.announcements_id_seq OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.announcements_id_seq OWNED BY public.announcements.id;


--
-- Name: event_code; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_code (
    code character varying(10) NOT NULL,
    description text,
    examples text,
    id integer NOT NULL
);


ALTER TABLE public.event_code OWNER TO postgres;

--
-- Name: event_code_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_code_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_code_id_seq OWNER TO postgres;

--
-- Name: event_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_code_id_seq OWNED BY public.event_code.id;


--
-- Name: event_venue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_venue (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.event_venue OWNER TO postgres;

--
-- Name: event_venue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_venue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_venue_id_seq OWNER TO postgres;

--
-- Name: event_venue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_venue_id_seq OWNED BY public.event_venue.id;


--
-- Name: job_detail; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_detail (
    photoid integer NOT NULL,
    eventcode character varying(50) NOT NULL,
    r_type character varying(255) NOT NULL,
    photographer_selection text,
    event_title character varying(255) NOT NULL,
    event_venue character varying(255) NOT NULL,
    event_dt_fm date,
    event_dt_to date,
    event_ti_fm time without time zone,
    event_ti_to time without time zone,
    requester_name character varying(255) NOT NULL,
    request_phone character varying(20) NOT NULL,
    request_email character varying(255) NOT NULL,
    request_div character varying(255),
    remarks text,
    is_deleted boolean NOT NULL,
    jobcode character varying(255),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.job_detail OWNER TO postgres;

--
-- Name: job_detail_photoid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_detail_photoid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.job_detail_photoid_seq OWNER TO postgres;

--
-- Name: job_detail_photoid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_detail_photoid_seq OWNED BY public.job_detail.photoid;


--
-- Name: job_photographers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_photographers (
    id integer NOT NULL,
    photoid integer,
    event_date date NOT NULL,
    photographer_name text NOT NULL
);


ALTER TABLE public.job_photographers OWNER TO postgres;

--
-- Name: job_photographers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.job_photographers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.job_photographers_id_seq OWNER TO postgres;

--
-- Name: job_photographers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.job_photographers_id_seq OWNED BY public.job_photographers.id;


--
-- Name: keyword_entry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.keyword_entry (
    path text NOT NULL,
    jobcode character varying(50) NOT NULL,
    filename character varying(255) NOT NULL,
    keyword text,
    entry_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    mody_date timestamp without time zone,
    "user" character varying(50) NOT NULL,
    keyno integer NOT NULL,
    keyword_id integer[],
    keywords text[]
);


ALTER TABLE public.keyword_entry OWNER TO postgres;

--
-- Name: keyword_entry_keyno_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.keyword_entry_keyno_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.keyword_entry_keyno_seq OWNER TO postgres;

--
-- Name: keyword_entry_keyno_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.keyword_entry_keyno_seq OWNED BY public.keyword_entry.keyno;


--
-- Name: keywords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.keywords (
    id integer NOT NULL,
    keyword character varying(100) NOT NULL
);


ALTER TABLE public.keywords OWNER TO postgres;

--
-- Name: keywords_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.keywords_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.keywords_id_seq OWNER TO postgres;

--
-- Name: keywords_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.keywords_id_seq OWNED BY public.keywords.id;


--
-- Name: photographers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.photographers (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    status character varying(10) NOT NULL
);


ALTER TABLE public.photographers OWNER TO postgres;

--
-- Name: photographers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.photographers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.photographers_id_seq OWNER TO postgres;

--
-- Name: photographers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.photographers_id_seq OWNED BY public.photographers.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: announcements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements ALTER COLUMN id SET DEFAULT nextval('public.announcements_id_seq'::regclass);


--
-- Name: event_code id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_code ALTER COLUMN id SET DEFAULT nextval('public.event_code_id_seq'::regclass);


--
-- Name: event_venue id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_venue ALTER COLUMN id SET DEFAULT nextval('public.event_venue_id_seq'::regclass);


--
-- Name: job_detail photoid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_detail ALTER COLUMN photoid SET DEFAULT nextval('public.job_detail_photoid_seq'::regclass);


--
-- Name: job_photographers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_photographers ALTER COLUMN id SET DEFAULT nextval('public.job_photographers_id_seq'::regclass);


--
-- Name: keyword_entry keyno; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.keyword_entry ALTER COLUMN keyno SET DEFAULT nextval('public.keyword_entry_keyno_seq'::regclass);


--
-- Name: keywords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.keywords ALTER COLUMN id SET DEFAULT nextval('public.keywords_id_seq'::regclass);


--
-- Name: photographers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photographers ALTER COLUMN id SET DEFAULT nextval('public.photographers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: announcements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcements (id, message, created_at) FROM stdin;
1	Stay tuned for our upcoming features and updates!	2025-02-04 15:34:20.335557
2	Dont forget to check our documentation for more information.	2025-02-04 15:34:20.335557
3	Database is connected	2025-02-04 15:36:48.158534
4	helooooo	2025-02-04 16:46:50.64078
\.


--
-- Data for Name: event_code; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_code (code, description, examples, id) FROM stdin;
MVIS	VVIP Visits of delegates in BARC	Presidents of India and other countries PM, CM, Ministers, IAEA delegates, etc.	1
NVIS	Visits of delegates in BARC	Visits from various organizations, institute, defence personal, etc.	2
TRAF	Traffic Cell Request	Vehicles accidents cases	3
TECH	Technology transfer	Tech. Transfers, Tech. MoUs Signing, tech. Inaugurations	4
SIMP	Symposium	International and National Symposium, Seminar, Theme Meeting, Workshop etc.	5
EVNM	Social and Community Events and Functions	Songs, Drama, Hindi programmes, Library day, quiz, etc.	6
SEND	Send off parties	Superannuation / Facilitation of employee	7
EVNS	Scientific and Technical Events and Functions	Trombay Colloquium, Independence day, Republic day, Bhabha Day, tech. Day, etc.	8
PORT	Portraits Photography	Portraits of distinguished authorities, Chairman DAE, Director BARC, etc.	9
MISC	Miscellaneous	Miscellaneous Events	10
LAND	Landscape and outside building	Dhruva, Cirus, Divisional building, views form Bhabha Point, etc.	11
INDU	Industrial Photography	Divisional equipment and materials, instruments, workshop machines etc.	12
GARD	Gardens, Trees view	Close photography of Flowers, buds, trees, etc.	13
CONF	Confidential	Confidential Coverage of event, setup, equipments etc.	14
\.


--
-- Data for Name: event_venue; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_venue (id, name) FROM stdin;
1	Conference Hall A
2	Main Auditorium
3	Outdoor Garden
4	Banquet Hall
5	Boardroom 1
\.


--
-- Data for Name: job_detail; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job_detail (photoid, eventcode, r_type, photographer_selection, event_title, event_venue, event_dt_fm, event_dt_to, event_ti_fm, event_ti_to, requester_name, request_phone, request_email, request_div, remarks, is_deleted, jobcode, created_at) FROM stdin;
3	NVIS	Videography	Photographer 2	Flower Festival	Indoor	2025-03-31	2025-03-31	10:00:00	17:00:00	ammu	1234567899	nishi@gmail.com	rhd		f	NVIS/2025/2	2025-03-24 16:32:38.853986
5	MVIS	Photography	Photographer 1, Photographer 2	Flower Festival	Outdoor	2025-03-26	2025-03-26	10:00:00	10:30:00	ammu	1234567899	sam@gmail.com	CC		f	MVIS/2025/4	2025-03-24 16:37:55.481763
7	NVIS	Videography	Photographer 2	April Fools day celebration	Outside BARC	2025-04-01	2025-04-01	10:00:00	05:00:00	nishi	1234567899	sam@gmail.com	SIRD		f	NVIS/2025/7	2025-03-24 16:42:18.780677
8	TECH	Both	Photographer 1, Photographer 2	SIRD hackathon	Indoor	2025-03-27	2025-03-29	10:00:00	05:00:00	Pranali	9372433107	baviskarpranali04@gmail.com	SIRD		f	TECH/2025/8	2025-03-25 10:16:08.480868
9	CONF	Photography	Photographer 1	TRD papert publishing	Outside BARC	2025-04-01	2025-04-01	10:00:00	20:00:00	Pranali	9372433107	nishi@gmail.com	PILLAI		f	CONF/2025/9	2025-03-25 11:41:17.612646
10	EVNM	Photography	Photographer 1, Photographer 2	Holi Celebration paret 2	Indoor	2025-04-01	2025-04-04	10:00:00	14:00:00	Ajith sir	1234567899	nishi@gmail.com	SIRD		f	EVNM/2025/10	2025-03-25 11:47:31.485057
11	MVIS	Videography		Flower Festival	Main Auditorium	2025-03-28	2025-03-28	13:00:00	16:00:00	fghjk	24687441248	sam@gmail.com	CC		f	MVIS/2025/11	2025-03-27 11:10:36.879372
12	TECH	Videography	John Doe\r\n                            	Hackathon 1	Banquet Hall	2025-03-28	2025-03-28	10:00:00	14:00:00	sam	9863546365	sam@gmail.com	cdm		f	TECH/2025/12	2025-03-27 11:12:35.541647
18	PORT	Photography	\N	fsdf	Outdoor Garden	2025-03-29	2025-03-31	12:00:00	13:40:00	sam	9863546365	baviskarpranali04@gmail.com	SIRD		f	PORT/2025/13	2025-03-27 13:32:10.527874
19	PORT	Photography	John Doe, Jane Smith	fsdf1`gvftftygh	Outdoor Garden	2025-03-29	2025-03-31	12:00:00	13:40:00	sam	9863546365	baviskarpranali04@gmail.com	SIRD		f	PORT/2025/19	2025-03-27 13:37:21.760647
20	GARD	Photography	John Doe, Jane Smith, Emily Johnson	alegria	Outdoor Garden	2025-03-11	2025-03-15	13:00:00	16:00:00	nishi	1243658792	sam@gmail.com	SIRD		f	GARD/2025/20	2025-03-27 13:39:55.642224
21	PORT	Photography	John Doe, Jane Smith, Emily Johnson	qwededed	Outdoor Garden	2025-03-16	2025-03-22	14:00:00	17:00:00	ammu	1234567899	cbgdxfglktg@gmail.com	a		f	PORT/2025/21	2025-03-27 13:50:31.581688
25	MVIS	Videography	Jane Smith, Emily Johnson	retirement	Main Auditorium	2025-03-28	2025-03-29	12:00:00	16:00:00	shreya	9863546365	sam@gmail.com	SIRD		f	MVIS/2025/25	2025-03-27 15:48:19.987969
26	TRAF	Videography	John Doe, Emily Johnson	retirement	Conference Hall A	2025-04-02	2025-04-04	10:00:00	18:50:00	ammu	9863546365	baviskarpranali04@gmail.com	CC	rdtfyghkj	f	TRAF/2025/26	2025-03-27 16:00:15.866389
22	SIMP	Photography	John Doe, Emily Johnson, Jane Smith	qwededed1	Main Auditorium	2025-03-27	2025-03-28	10:00:00	12:00:00	shreya	9863546365	doseidli@gmail.com	CC		f	SIMP/2025/22	2025-03-27 14:14:01.407136
23	TECH	Both	John Doe, Emily Johnson	DataMeet	Conference Hall A	2025-04-02	2025-04-04	10:00:00	12:00:00	ammu	9863546365	cbgdxfglktg@gmail.com	SIRD		f	TECH/2025/23	2025-03-27 15:33:55.337102
24	LAND	Videography	Emily Johnson, Jane Smith	Random photos	Outdoor Garden	2025-04-01	2025-04-03	12:00:00	15:00:00	shreya	9372433108	baviskarpranali04@gmail.com	cdm	dfhewr9pyherd	f	LAND/2025/24	2025-03-27 15:42:14.201902
27	TRAF	Videography	Jane Smith, Emily Johnson	dance	Outdoor Garden	2025-04-04	2025-04-07	15:00:00	16:00:00	sam	9863546365	sam@gmail.com	SIRD		f	TRAF/2025/27	2025-03-27 16:04:33.819515
28	MVIS	Videography	Jane Smith, Emily Johnson	Flower Festival	Conference Hall A	2025-04-03	2025-04-05	15:00:00	16:00:00	ammu	9863546365	cbgdxfglktg@gmail.com	CC		f	MVIS/2025/28	2025-03-27 16:08:55.104632
29	EVNS	Videography	John Doe, Emily Johnson	qwededed	Outdoor Garden	2025-12-04	2025-12-05	15:00:00	16:00:00	ammu	9863546365	nishi@gmail.com	sd		f	EVNS/2025/29	2025-03-27 16:13:58.337595
32	EVNM	Photography		gudi padwa	Outdoor Garden	2025-03-30	2025-03-31	10:00:00	14:00:00	sam	9863546365	sam@gmail.com	cdm	zwxedcrfvtgyhuunjkm	f	EVNM/2025/32	2025-03-28 11:02:28.666231
33	SIMP	Videography	John Doe, Jane Smith	vishu	Main Auditorium	2025-04-14	2025-04-15	10:00:00	12:00:00	sam	1234567899	sam@gmail.com	cdm		f	SIMP/2025/33	2025-03-28 11:05:31.005331
35	SEND	Photography	John Doe, Emily Johnson	retirement	Conference Hall A	2025-03-25	2025-03-26	10:00:00	12:00:00	shreya	9372433108	nishi@gmail.com	cdm		f	SEND/2025/34	2025-03-28 11:41:39.150285
30	MISC	Photography		birthday	Outdoor Garden	2025-04-03	2025-04-05	13:00:00	15:00:00	Pranali	9863546365	nishi@gmail.com	CC		f	MISC/2025/30	2025-03-27 16:28:42.726828
31	SIMP	Photography		Lallentines day	Main Auditorium	2025-04-10	2025-04-13	14:00:00	17:00:00	hnjhfgjhk,ggf	1234567899	baviskarpranali04@gmail.com	cdm	qa2ws4ed5rf6tgyhuji	f	SIMP/2025/31	2025-03-28 10:49:52.53546
39	EVNM	Photography	Jane Smith, Emily Johnson	alegria	Boardroom 1	2025-04-02	2025-04-03	10:00:00	13:00:00	ammu	9863546365	nishi@gmail.com	cdm		f	EVNM/2025/39	2025-03-28 13:42:39.801405
36	NVIS	Photography	Emily Johnson	qwededed	Conference Hall A	2025-03-28	2025-03-29	10:00:00	12:00:00	Pranali	9372433108	baviskarpranali04@gmail.com	sd		f	NVIS/2025/36	2025-03-28 11:45:19.399932
37	EVNM	Photography	John Doe, Emily Johnson	Flower Festival	Outdoor Garden	2025-03-25	2025-03-26	10:00:00	10:00:00	Pranali	1234567899	nishi@gmail.com	a		f	EVNM/2025/37	2025-03-28 11:55:17.98852
38	NVIS	Photography	John Doe, Jane Smith, Emily Johnson	halloween	Outdoor Garden	2025-03-31	2025-04-02	22:00:00	01:00:00	Pranali	9372433108	baviskarpranali04@gmail.com	SIRD		f	NVIS/2025/38	2025-03-28 13:40:18.568735
40	LAND	Photography	John Doe, Jane Smith	asd	Main Auditorium	2025-04-02	2025-04-03	10:00:00	12:00:00	asas	1234567899	baviskarpranali04@gmail.com	CC		f	LAND/2025/40	2025-04-01 11:08:48.69645
41	SIMP	Photography	John Doe, Jane Smith	qwededed	Main Auditorium	2025-04-16	2025-04-17	10:00:00	12:00:00	shreya	9372433108	cbgdxfglktg@gmail.com	SIRD	6tf7yg8u9ijpo	f	SIMP/2025/41	2025-04-01 15:07:20.786174
42	SIMP	Videography	Emily Johnson, John Doe	safgvrtu	Main Auditorium	2025-04-23	2025-04-24	10:00:00	14:00:00	ammu	9863546365	baviskarpranali04@gmail.com	SIRD	t70oiuj	f	SIMP/2025/42	2025-04-01 15:18:54.7318
43	TRAF	Photography	John Doe, Emily Johnson	qwededed	Main Auditorium	2025-04-15	2025-04-17	10:00:00	12:00:00	ammu	9372433108	sam@gmail.com	SIRD	werawehuhj6rfl	f	TRAF/2025/43	2025-04-01 15:29:14.375906
44	SEND	Videography	Jane Smith, Emily Johnson	OFF AND DIE	Main Auditorium	2025-04-09	2025-04-10	10:00:00	12:00:00	shreya	9372433107	nishi@gmail.com	SIRD	cvhm  	f	SEND/2025/44	2025-04-01 15:34:38.942853
45	NVIS	Videography	Jane Smith	Flower Festival	Conference Hall A	2025-04-08	2025-04-09	10:00:00	12:00:00	shreya	9863546365	baviskarpranali04@gmail.com	SIRD		f	NVIS/2025/45	2025-04-01 15:42:22.74182
46	INDU	Photography	Jane Smith, John Doe	farewell for ps	Outdoor Garden	2025-04-09	2025-04-10	12:00:00	15:00:00	sam	9863546365	sam@gmail.com	SIRD	r43u87p	f	INDU/2025/46	2025-04-03 10:28:22.847165
1	MVIS	Photography	Jane Smith, John Doe	retirement	Main Auditorium	2025-03-26	2025-03-26	09:00:00	14:00:00	shreya	9863546365	baviskarpranali04@gmail.com	sd		f	MVIS/2025/1	2025-03-24 16:32:38.853986
6	MVIS	Photography	Photographer 1, Photographer 2	Roadies Double cross	Outdoor	2025-03-25	2025-03-25	10:00:00	01:00:00	Phweyfdwev	93724333894	cbgdxfglktg@gmail.com	a		t	MVIS/2025/6	2025-03-24 16:39:45.157386
49	TRAF	Photography	John Doe, Emily Johnson, Jane Smith	gudi padwa	Outdoor Garden	2025-04-03	2025-04-05	12:00:00	15:00:00	sam	9372433107	baviskarpranali04@gmail.com	CC		f	TRAF/2025/47	2025-04-03 14:29:24.070361
50	SEND	Photography	Emily Johnson	ShevPuri Talks witth aswini	Conference Hall A	2025-04-08	2025-04-09	15:00:00	17:00:00	ammusyudweiu	9372433107	cbgdxfglktg@gmail.com	sd		t	SEND/2025/50	2025-04-04 08:45:12.330807
51	NVIS	Videography	Jane Smith, John Doe	gudi padwa	Main Auditorium	2025-04-15	2025-04-16	10:00:00	05:00:00	Pranali	1234567899	sam@gmail.com	cdm		f	NVIS/2025/51	\N
\.


--
-- Data for Name: job_photographers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.job_photographers (id, photoid, event_date, photographer_name) FROM stdin;
1	19	2025-03-29	John Doe
2	19	2025-03-30	Jane Smith
3	19	2025-03-31	John Doe
4	19	2025-03-31	Jane Smith
5	19	2025-03-29	John Doe
6	19	2025-03-30	Jane Smith
7	19	2025-03-31	John Doe
8	19	2025-03-31	Jane Smith
9	19	2025-03-29	John Doe
10	19	2025-03-30	Jane Smith
11	19	2025-03-31	John Doe
12	19	2025-03-31	Jane Smith
13	20	2025-03-11	John Doe
14	20	2025-03-12	Jane Smith
15	20	2025-03-13	Emily Johnson
16	20	2025-03-14	Jane Smith
17	20	2025-03-14	Emily Johnson
18	20	2025-03-15	John Doe
19	20	2025-03-15	Jane Smith
20	20	2025-03-15	Emily Johnson
21	20	2025-03-11	John Doe
22	20	2025-03-12	Jane Smith
23	20	2025-03-13	Emily Johnson
24	20	2025-03-14	Jane Smith
25	20	2025-03-14	Emily Johnson
26	20	2025-03-15	John Doe
27	20	2025-03-15	Jane Smith
28	20	2025-03-15	Emily Johnson
29	20	2025-03-11	John Doe
30	20	2025-03-12	Jane Smith
31	20	2025-03-13	Emily Johnson
32	20	2025-03-14	Jane Smith
33	20	2025-03-14	Emily Johnson
34	20	2025-03-15	John Doe
35	20	2025-03-15	Jane Smith
36	20	2025-03-15	Emily Johnson
37	20	2025-03-11	John Doe
38	20	2025-03-12	Jane Smith
39	20	2025-03-13	Emily Johnson
40	20	2025-03-14	Jane Smith
41	20	2025-03-14	Emily Johnson
42	20	2025-03-15	John Doe
43	20	2025-03-15	Jane Smith
44	20	2025-03-15	Emily Johnson
45	20	2025-03-11	John Doe
46	20	2025-03-12	Jane Smith
47	20	2025-03-13	Emily Johnson
48	20	2025-03-14	Jane Smith
49	20	2025-03-14	Emily Johnson
50	20	2025-03-15	John Doe
51	20	2025-03-15	Jane Smith
52	20	2025-03-15	Emily Johnson
53	21	2025-03-16	John Doe
54	21	2025-03-17	Jane Smith
55	21	2025-03-18	Emily Johnson
56	21	2025-03-19	John Doe
57	21	2025-03-19	Jane Smith
58	21	2025-03-20	John Doe
59	21	2025-03-20	Emily Johnson
61	21	2025-03-21	Emily Johnson
62	21	2025-03-22	John Doe
63	21	2025-03-22	Jane Smith
64	21	2025-03-22	Emily Johnson
95	30	2025-04-04	
96	30	2025-04-05	
94	30	2025-04-03	
97	31	2025-04-10	Jane Smith
98	31	2025-04-11	Jane Smith
99	31	2025-04-12	Jane Smith
100	31	2025-04-13	John Doe
101	31	2025-04-13	Emily Johnson
102	32	2025-03-30	John Doe
103	32	2025-03-31	Emily Johnson
104	33	2025-04-14	John Doe
105	33	2025-04-15	Jane Smith
106	36	2025-03-28	John Doe
107	36	2025-03-29	John Doe
108	37	2025-03-25	John Doe
109	37	2025-03-26	Emily Johnson
60	21	2025-03-21	Sarah Jones
110	38	2025-03-31	John Doe
111	38	2025-03-31	Jane Smith
112	38	2025-04-01	Jane Smith
113	38	2025-04-01	Emily Johnson
114	38	2025-04-02	John Doe
115	38	2025-04-02	Emily Johnson
116	39	2025-04-02	Emily Johnson
117	39	2025-04-03	Jane Smith
118	40	2025-04-02	John Doe
119	40	2025-04-03	John Doe
120	40	2025-04-03	Jane Smith
121	41	2025-04-16	John Doe
122	41	2025-04-17	Jane Smith
123	42	2025-04-23	Emily Johnson
124	42	2025-04-24	John Doe
125	43	2025-04-15	John Doe
126	43	2025-04-16	Emily Johnson
127	44	2025-04-09	Jane Smith
128	44	2025-04-10	Emily Johnson
129	45	2025-04-08	Jane Smith
130	45	2025-04-09	Jane Smith
137	1	2025-03-26	Jane Smith
138	1	2025-03-26	John Doe
143	49	2025-04-03	Emily Johnson
144	49	2025-04-03	Jane Smith
145	49	2025-04-04	Jane Smith
146	49	2025-04-05	Jane Smith
157	50	2025-04-08	Emily Johnson
158	50	2025-04-09	Emily Johnson
166	51	2025-04-17	Emily Johnson
167	51	2025-04-15	Jane Smith
\.


--
-- Data for Name: keyword_entry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.keyword_entry (path, jobcode, filename, keyword, entry_date, mody_date, "user", keyno, keyword_id, keywords) FROM stdin;
D:/destination_path	NVIS/2025/7	sample.jpg	\N	2025-03-25 07:56:46.694958	2025-03-25 07:56:46.694958	admin	1	\N	\N
D:/destination_path	NVIS/2025/7	sample.jpg	\N	2025-03-25 07:57:16.858757	2025-03-25 07:57:16.858757	admin	2	\N	\N
D:/2025/04/MVIS-03-shreya-28	MVIS/2025/28	sample.jpg	\N	2025-04-02 09:31:53.699288	2025-04-02 09:31:53.699288	shreya	3	\N	\N
D:/2025/04/MVIS-03-shreya-28	MVIS/2025/28	sample.jpg	\N	2025-04-02 09:31:53.699288	2025-04-02 09:31:53.699288	shreya	4	\N	\N
D:/2025/04/MVIS-03-shreya-28	MVIS/2025/28	sample.jpg	\N	2025-04-02 09:37:23.883581	2025-04-02 09:37:23.883581	shreya	5	\N	\N
D:/2025/04/MVIS-03-shreya-28	MVIS/2025/28	sample.jpg	\N	2025-04-02 09:37:23.887487	2025-04-02 09:37:23.887487	shreya	6	\N	\N
D:/2025/04/TECH-02-shreya-23	TECH/2025/23	sample.jpg	\N	2025-04-02 09:52:02.092497	2025-04-02 09:52:02.092497	shreya	7	\N	\N
D:/2025/04/TECH-02-shreya-23	TECH/2025/23	sample.jpg	\N	2025-04-02 09:52:02.098336	2025-04-02 09:52:02.098336	shreya	8	\N	\N
D:/2025/04/LAND-02-shreya-40	LAND/2025/40	sample.jpg	\N	2025-04-02 10:02:37.359047	2025-04-02 10:02:37.359047	shreya	9	\N	\N
D:/2025/04/LAND-02-shreya-40	LAND/2025/40	sample.jpg	\N	2025-04-02 10:02:37.362941	2025-04-02 10:02:37.362941	shreya	10	\N	\N
D:/2025/04/TECH-02-shreya-23	TECH/2025/23	sample.jpg	\N	2025-04-02 10:27:30.885145	2025-04-02 10:27:30.885145	shreya	11	\N	\N
D:/2025/03/TECH-28-shreya-12	TECH/2025/12	sample.jpg	\N	2025-04-02 10:32:51.24726	2025-04-02 10:32:51.24726	shreya	12	\N	\N
D:/2025/03/TECH-28-shreya-12	TECH/2025/12	sample.jpg	\N	2025-04-02 10:32:51.251166	2025-04-02 10:32:51.251166	shreya	13	\N	\N
D:/2025/03/TECH-28-shreya-12	TECH/2025/12	sample.jpg	\N	2025-04-02 10:32:51.251166	2025-04-02 10:32:51.251166	shreya	14	\N	\N
D:/2025/04/MVIS-03-shreya-28	MVIS/2025/28	sample.jpg	\N	2025-04-02 10:56:40.05059	2025-04-02 10:56:40.05059	shreya	15	{54,55,56}	\N
D:/2025/04/SIMP-23-shreya-42	SIMP/2025/42	sample.jpg	\N	2025-04-02 11:04:32.645035	2025-04-02 11:04:32.645035	shreya	16	{57,58}	\N
D:/2025/04/EVNM-01-shreya-10	EVNM/2025/10	sample.jpg	\N	2025-04-02 11:11:44.180779	2025-04-02 11:11:44.180779	shreya	17	{47,59}	\N
D:/2025/04/MVIS-03-shreya-28	MVIS/2025/28	sample.jpg	\N	2025-04-02 11:23:49.157973	2025-04-02 11:23:49.157973	shreya	18	{60,61,62}	{aedhtyy,dil,day}
D:/2025/04/INDU-09-shreya-46	INDU/2025/46	sample.jpg	\N	2025-04-03 05:00:26.169568	2025-04-03 05:00:26.169568	shreya	19	{63,64}	{bye,farewell}
D:/2025/04/TRAF-03-shreya-47	TRAF/2025/47	sample.jpg	\N	2025-04-03 09:02:01.410016	2025-04-03 09:02:01.410016	shreya	20	{65,66}	{family,gudi}
D:/2025/04/TRAF-04-shreya-27	TRAF/2025/27	sample.jpg	\N	2025-04-03 09:04:29.211562	2025-04-03 09:04:29.211562	shreya	21	{47}	{"data science"}
D:/2025/04/EVNM-01-shreya-10	EVNM/2025/10	sample.jpg	\N	2025-04-03 09:07:56.528879	2025-04-03 09:07:56.528879	shreya	22	{67}	{shreya}
D:/2025/04/TRAF-04-shreya-27	TRAF/2025/27	sample.jpg	\N	2025-04-03 09:10:21.282956	2025-04-03 09:10:21.282956	shreya	23	{41}	{dad}
D:/2025/04/TRAF-15-shreya-43	TRAF/2025/43	sample.jpg	\N	2025-04-03 09:11:12.12559	2025-04-03 09:11:12.12559	shreya	24	{67}	{shreya}
D:\\2025\\04\\NVIS-08-shreya-45	NVIS/2025/45	N/A	\N	2025-04-07 04:31:12.671816	2025-04-07 04:31:12.671816	shreya	25	{54,68,69}	{Rose,lilly,dandelions}
D:\\2025\\04\\NVIS-15-shreya-51	NVIS/2025/51	N/A	\N	2025-04-07 09:33:53.550483	2025-04-07 09:33:53.550483	shreya	26	{70,47,13,42}	{celebrate,"data science","Slow Motion",S}
\.


--
-- Data for Name: keywords; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.keywords (id, keyword) FROM stdin;
1	Portrait
2	Landscape
3	Macro
4	Aerial
5	Street
6	Wildlife
7	Fashion
8	Event
9	Candid
10	Black & White
11	Documentary
12	Cinematic
13	Slow Motion
14	Time-lapse
15	4K
16	Drone Shot
17	B-roll
18	Short Film
19	Editing
20	VFX
21	Flash
22	Softbox
23	Tripod
24	Gimbal
25	Lens
26	DSLR
27	Mirrorless
28	Telephoto
29	Wide Angle
30	Prime Lens
31	Wedding
32	Conference
33	Sports
34	Concert
35	Graduation
36	Birthday
37	Festival
38	Corporate
39	Workshop
40	Press Meet
41	dad
42	S
43	sa
44	asd
45	aw
46	flag
47	data science
48	AI
49	ML
50	samay
51	estgdsw6t
52	ewtg563eg
53	DIE
54	Rose
55	lily
56	mexico
57	nandu
58	bday
59	machne learning
60	aedhtyy
61	dil
62	day
63	bye
64	farewell
65	family
66	gudi
67	shreya
68	lilly
69	dandelions
70	celebrate
\.


--
-- Data for Name: photographers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.photographers (id, name, status) FROM stdin;
1	John Doe	active
2	Jane Smith	active
3	Robert Brown	inactive
4	Emily Johnson	active
5	Michael White	inactive
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password) FROM stdin;
1	shreya	shreya12
\.


--
-- Name: announcements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcements_id_seq', 4, true);


--
-- Name: event_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_code_id_seq', 14, true);


--
-- Name: event_venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_venue_id_seq', 5, true);


--
-- Name: job_detail_photoid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_detail_photoid_seq', 51, true);


--
-- Name: job_photographers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.job_photographers_id_seq', 167, true);


--
-- Name: keyword_entry_keyno_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.keyword_entry_keyno_seq', 26, true);


--
-- Name: keywords_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.keywords_id_seq', 70, true);


--
-- Name: photographers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.photographers_id_seq', 5, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: announcements announcements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);


--
-- Name: event_code event_code_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_code
    ADD CONSTRAINT event_code_pkey PRIMARY KEY (id);


--
-- Name: event_venue event_venue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_venue
    ADD CONSTRAINT event_venue_pkey PRIMARY KEY (id);


--
-- Name: event_venue event_venue_venue_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_venue
    ADD CONSTRAINT event_venue_venue_key UNIQUE (name);


--
-- Name: job_detail job_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_detail
    ADD CONSTRAINT job_detail_pkey PRIMARY KEY (photoid);


--
-- Name: job_photographers job_photographers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_photographers
    ADD CONSTRAINT job_photographers_pkey PRIMARY KEY (id);


--
-- Name: keyword_entry keyword_entry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.keyword_entry
    ADD CONSTRAINT keyword_entry_pkey PRIMARY KEY (keyno);


--
-- Name: keywords keywords_keyword_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_keyword_key UNIQUE (keyword);


--
-- Name: keywords keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_pkey PRIMARY KEY (id);


--
-- Name: photographers photographers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photographers
    ADD CONSTRAINT photographers_name_key UNIQUE (name);


--
-- Name: photographers photographers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.photographers
    ADD CONSTRAINT photographers_pkey PRIMARY KEY (id);


--
-- Name: event_code unique_event_code; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_code
    ADD CONSTRAINT unique_event_code UNIQUE (code);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: job_photographers job_photographers_photoid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_photographers
    ADD CONSTRAINT job_photographers_photoid_fkey FOREIGN KEY (photoid) REFERENCES public.job_detail(photoid) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

