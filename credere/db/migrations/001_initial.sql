-- Schema inicial de Credere Analysis en Supabase.
-- Ejecutar desde Supabase SQL editor.

create extension if not exists "uuid-ossp";

-- Parametros globales (fila unica, id=1)
create table if not exists parametros_globales (
    id int primary key default 1,
    payload jsonb not null,
    updated_at timestamptz default now(),
    constraint parametros_unica check (id = 1)
);

-- Proyectos (una fila por operacion)
create table if not exists proyectos (
    id uuid primary key default uuid_generate_v4(),
    nombre text not null,
    localizacion text default '',
    ccaa text default 'Madrid',
    descripcion text default '',
    fecha_creacion date not null default current_date,
    fecha_financiacion date,
    payload jsonb not null,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index if not exists proyectos_nombre_idx on proyectos using btree (nombre);
create index if not exists proyectos_ccaa_idx on proyectos using btree (ccaa);

-- Resultados (snapshot inmutable por analisis)
create table if not exists resultados (
    id uuid primary key default uuid_generate_v4(),
    proyecto_id uuid not null references proyectos(id) on delete cascade,
    params_snapshot jsonb not null,
    prestamo jsonb not null,
    cashflow jsonb not null,
    ratios jsonb not null,
    analisis_mercado jsonb,
    scoring jsonb,
    created_at timestamptz default now()
);

create index if not exists resultados_proyecto_idx on resultados using btree (proyecto_id);
create index if not exists resultados_created_idx on resultados using btree (created_at desc);

-- Trigger updated_at en proyectos
create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists proyectos_updated_at on proyectos;
create trigger proyectos_updated_at
    before update on proyectos
    for each row execute function set_updated_at();
