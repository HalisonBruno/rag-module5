-- Run this once in your Supabase SQL Editor
-- Creates the persistent memory table for Module 5

create table if not exists agent_memory (
    id          bigserial primary key,
    session_id  text        not null,
    memory_type text        not null default 'fact',  -- 'fact' | 'summary' | 'preference'
    content     text        not null,
    importance  int         not null default 1,       -- 1-5, higher = more important
    created_at  timestamptz not null default now()
);

create index if not exists agent_memory_session_idx on agent_memory (session_id);
create index if not exists agent_memory_type_idx    on agent_memory (memory_type);
