-- Create tables
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "firstName" VARCHAR(255) NOT NULL,
    "lastName" VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE client (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "idUser" UUID NOT NULL REFERENCES "user"(id),
    name VARCHAR(255) NOT NULL,
    note TEXT,
    "contactName" VARCHAR(255),
    "contactPhone" VARCHAR(255),
    "contactEmail" VARCHAR(255)
);

CREATE TABLE project (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "idUser" UUID NOT NULL REFERENCES "user"(id),
    "idClient" UUID NOT NULL REFERENCES client(id),
    name VARCHAR(255) NOT NULL,
    note TEXT
);

CREATE TABLE task (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "idUser" UUID NOT NULL REFERENCES "user"(id),
    title VARCHAR(255) NOT NULL
);

CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "idUser" UUID NOT NULL REFERENCES "user"(id),
    title VARCHAR(255) NOT NULL
);

CREATE TABLE contract (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "idUser" UUID NOT NULL REFERENCES "user"(id),
    "idProject" UUID NOT NULL REFERENCES project(id),
    name VARCHAR(255) NOT NULL,
    note TEXT,
    rate NUMERIC(10,2),
    "rateUnit" VARCHAR(50),
    "startDate" DATE,
    "endDate" DATE
);

CREATE TABLE report (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "idUser" UUID NOT NULL REFERENCES "user"(id),
    "idContract" UUID NOT NULL REFERENCES contract(id),
    note TEXT,
    billable BOOLEAN DEFAULT TRUE,
    "startTimestamp" TIMESTAMP NOT NULL,
    "endTimestamp" TIMESTAMP NOT NULL,
    "breakTime" INTERVAL DEFAULT '0 minutes'
);

CREATE TABLE assign (
    "idProject" UUID NOT NULL REFERENCES project(id),
    "idTask" UUID NOT NULL REFERENCES task(id),
    PRIMARY KEY ("idProject", "idTask")
);

CREATE TABLE "locatedAt" (
    "idReport" UUID NOT NULL REFERENCES report(id),
    "idLocation" UUID NOT NULL REFERENCES location(id),
    PRIMARY KEY ("idReport", "idLocation")
);

CREATE TABLE expenses (
    "idReport" UUID NOT NULL REFERENCES report(id),
    price NUMERIC(10,2) NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY ("idReport", price, note)
);