DO $$ BEGIN
    CREATE TYPE expensestatus AS ENUM ('PENDING', 'APPROVED', 'PAID', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE expenseevent AS ENUM ('CREATED', 'APPROVED', 'PAID', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE paymentstatus AS ENUM ('PENDING', 'APPROVED', 'EXECUTED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE paymentevent AS ENUM ('CREATED', 'APPROVED', 'EXECUTED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS roles (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS funcionalidades (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    ruta   VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rol_funcionalidades (
    id               SERIAL PRIMARY KEY,
    id_rol           INTEGER NOT NULL REFERENCES roles (id),
    id_funcionalidad INTEGER NOT NULL REFERENCES funcionalidades (id)
);
CREATE INDEX IF NOT EXISTS index_rol_funcionalidades_id_rol ON rol_funcionalidades (id_rol);
CREATE INDEX IF NOT EXISTS index_rol_funcionalidades_id_funcionalidad ON rol_funcionalidades (id_funcionalidad);

CREATE TABLE IF NOT EXISTS usuarios (
    id               SERIAL PRIMARY KEY,
    id_rol           INTEGER NOT NULL REFERENCES roles (id),
    correo           VARCHAR(120) NOT NULL,
    password         VARCHAR(255) NOT NULL,
    nombre           VARCHAR(80) NOT NULL,
    apellido_paterno VARCHAR(80) NOT NULL,
    apellido_materno VARCHAR(80)
);
CREATE UNIQUE INDEX IF NOT EXISTS index_usuarios_correo ON usuarios (correo);

CREATE TABLE IF NOT EXISTS logger_funcionalidades (
    id               SERIAL PRIMARY KEY,
    id_funcionalidad INTEGER NOT NULL REFERENCES funcionalidades (id),
    id_usuario       INTEGER NOT NULL REFERENCES usuarios (id),
    fecha_registro   TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS index_logger_funcionalidades_id_funcionalidad ON logger_funcionalidades (id_funcionalidad);
CREATE INDEX IF NOT EXISTS index_logger_funcionalidades_id_usuario ON logger_funcionalidades (id_usuario);

CREATE TABLE IF NOT EXISTS cuentas_bancarias (
    id            SERIAL PRIMARY KEY,
    nombre_banco  VARCHAR(80) NOT NULL,
    numero_cuenta VARCHAR(30) NOT NULL UNIQUE,
    saldo         NUMERIC(14, 2) NOT NULL,
    moneda        VARCHAR(3) NOT NULL
);

CREATE TABLE IF NOT EXISTS gastos (
    id                SERIAL PRIMARY KEY,
    codigo_referencia VARCHAR(40) NOT NULL UNIQUE,
    concepto          VARCHAR(120) NOT NULL,
    descripcion       TEXT,
    monto_total       NUMERIC(14, 2) NOT NULL,
    saldo_pendiente   NUMERIC(14, 2) NOT NULL,
    estado            expensestatus NOT NULL,
    creado_por        INTEGER NOT NULL REFERENCES usuarios (id),
    aprobado_por      INTEGER REFERENCES usuarios (id),
    fecha_gasto       TIMESTAMPTZ NOT NULL,
    fecha_aprobacion  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS index_gastos_estado ON gastos (estado);

CREATE TABLE IF NOT EXISTS gasto_registros (
    id             SERIAL PRIMARY KEY,
    id_gasto       INTEGER NOT NULL REFERENCES gastos (id),
    tipo_evento    expenseevent NOT NULL,
    realizado_por  INTEGER NOT NULL REFERENCES usuarios (id),
    detalle        TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS index_gasto_registros_id_gasto ON gasto_registros (id_gasto);

CREATE TABLE IF NOT EXISTS pagos (
    id                 SERIAL PRIMARY KEY,
    id_gasto           INTEGER NOT NULL REFERENCES gastos (id),
    id_cuenta_bancaria INTEGER NOT NULL REFERENCES cuentas_bancarias (id),
    codigo_operacion   VARCHAR(40) NOT NULL UNIQUE,
    monto              NUMERIC(14, 2) NOT NULL,
    estado             paymentstatus NOT NULL,
    creado_por         INTEGER NOT NULL REFERENCES usuarios (id),
    aprobado_por       INTEGER REFERENCES usuarios (id),
    fecha_pago         TIMESTAMPTZ NOT NULL,
    fecha_efectuado    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS index_pagos_estado ON pagos (estado);
CREATE INDEX IF NOT EXISTS index_pagos_id_gasto ON pagos (id_gasto);

CREATE TABLE IF NOT EXISTS pago_registros (
    id             SERIAL PRIMARY KEY,
    id_pago        INTEGER NOT NULL REFERENCES pagos (id),
    tipo_evento    paymentevent NOT NULL,
    realizado_por  INTEGER NOT NULL REFERENCES usuarios (id),
    detalle        TEXT,
    fecha_registro TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS index_pago_registros_id_pago ON pago_registros (id_pago);
