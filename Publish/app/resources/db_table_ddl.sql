-- public.login_details definition

-- Drop table

-- DROP TABLE public.login_details;

CREATE TABLE public.login_details (
	user_id varchar(255) NOT NULL,
	hashed_password varchar(255) NOT NULL,
	last_reset_time timestamptz NULL,
	CONSTRAINT login_details_pkey PRIMARY KEY (user_id)
);


-- public.patient_details definition

-- Drop table

-- DROP TABLE public.patient_details;

CREATE TABLE public.patient_details (
	id text DEFAULT 'APC'::text || lpad(nextval('your_table_id_seq'::regclass)::text, 4, '0'::text) NOT NULL,
	"name" varchar(255) NOT NULL,
	registeration_date timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	phone_number varchar(10) NOT NULL,
	age int4 NOT NULL,
	address varchar(500) NOT NULL,
	city varchar(50) NOT NULL,
	pincode varchar(6) NOT NULL,
	mode_of_referral varchar(100) NULL,
	CONSTRAINT patient_details_phone_number_check CHECK (((phone_number)::text ~ '^[0-9]{10}$'::text)),
	CONSTRAINT patient_details_pkey PRIMARY KEY (id)
);


-- public.security_index definition

-- Drop table

-- DROP TABLE public.security_index;

CREATE TABLE public.security_index (
	id serial4 NOT NULL,
	security_name varchar(100) NULL,
	security_short_desc varchar(100) NULL,
	CONSTRAINT security_index_pkey PRIMARY KEY (id)
);


-- public.test definition

-- Drop table

-- DROP TABLE public.test;

CREATE TABLE public.test (
	id serial4 NOT NULL,
	num int4 NULL,
	"data" text NULL,
	CONSTRAINT test_pkey PRIMARY KEY (id)
);


-- public.treatment_details definition

-- Drop table

-- DROP TABLE public.treatment_details;

CREATE TABLE public.treatment_details (
	id serial4 NOT NULL,
	patient_id varchar(10) NOT NULL,
	treatment_date timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	diagnosis varchar(500) NOT NULL,
	treatment_plan varchar(1000) NULL,
	doctor_name varchar(100) NULL,
	notes varchar(2000) NULL,
	CONSTRAINT treatment_details_pkey PRIMARY KEY (id),
	CONSTRAINT fk_patient FOREIGN KEY (patient_id) REFERENCES public.patient_details(id) ON DELETE CASCADE
);


-- public.payment_details definition

-- Drop table

-- DROP TABLE public.payment_details;

CREATE TABLE public.payment_details (
	id serial4 NOT NULL,
	patient_id varchar(10) NOT NULL,
	treatment_id int4 NOT NULL,
	payment_date timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	amount numeric(10, 2) NOT NULL,
	payment_method varchar(50) NOT NULL,
	transaction_id varchar(100) NULL,
	notes varchar(500) NULL,
	CONSTRAINT payment_details_amount_check CHECK ((amount > (0)::numeric)),
	CONSTRAINT payment_details_pkey PRIMARY KEY (id),
	CONSTRAINT payment_details_transaction_id_key UNIQUE (transaction_id),
	CONSTRAINT fk_payment_patient FOREIGN KEY (patient_id) REFERENCES public.patient_details(id) ON DELETE CASCADE,
	CONSTRAINT fk_payment_treatment FOREIGN KEY (treatment_id) REFERENCES public.treatment_details(id) ON DELETE CASCADE
);


CREATE TABLE login (
    -- id: An auto-incrementing integer that serves as the unique primary key.
    -- SERIAL is a convenient PostgreSQL type for this purpose.
    id SERIAL PRIMARY KEY,

    -- username: The user's unique login name. It cannot be empty.
    -- VARCHAR(255) is a common choice for usernames.
    username VARCHAR(255) UNIQUE NOT NULL,

    -- password_hash: Stores the hashed version of the user's password.
    -- It's crucial to store hashes and not plain-text passwords for security.
    -- Storing as TEXT allows for flexibility with different hashing algorithms.
    password_hash TEXT NOT NULL,

    -- password_reset_time: A timestamp to track when a password reset was requested.
    -- This field can be NULL, indicating no active password reset request.
    -- TIMESTAMPTZ stores the timestamp with time zone information.
    password_reset_time TIMESTAMPTZ NULL
);