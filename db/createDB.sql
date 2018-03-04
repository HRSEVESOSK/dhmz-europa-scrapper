CREATE TABLE IF NOT EXISTS
    "meteoeudb"."public".foi
    (
        oid bigserial NOT NULL,
        id CHARACTER VARYING(256) NOT NULL,
        geom geometry NOT NULL,
        metadata jsonb,
        PRIMARY KEY (oid),
        CONSTRAINT foi_id_ix1 UNIQUE (id)
    )
;
CREATE TABLE IF NOT EXISTS
    "meteoeudb"."public".observation
    (
        oid bigserial NOT NULL,
        time timestamp NOT NULL,
        foi_ref bigint NOT NULL,
        data jsonb NOT NULL,
        PRIMARY KEY (oid),
        CONSTRAINT observation_fk1 FOREIGN KEY (foi_ref) REFERENCES
        "meteoeudb"."public"."foi" ("oid")
    )
;