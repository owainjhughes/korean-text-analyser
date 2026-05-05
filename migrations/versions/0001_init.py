"""init: users + shared multi-language tables, schema-compatible with ObuCon.

This migration is idempotent — every CREATE uses IF NOT EXISTS, and the
updated_at trigger is dropped before recreation. That means it is safe to run
against a fresh local Postgres OR against the shared ObuCon Postgres where
ObuCon's own migration already created `users`, `known_words`, `analyses`,
and `analysis_tokens`. The Saebae app does not own those shared tables —
it only ensures they exist with the agreed schema.

Phase 1 only uses `users`. The other tables are created here so the schema is
fully aligned with ObuCon's `001_init.up.sql` and ready for phase 2 (known
words, analysis history) without a follow-up migration.

Revision ID: 0001
Revises:
Create Date: 2026-05-05
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS known_words (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    lemma TEXT NOT NULL,
    grade_level INTEGER,
    status VARCHAR(20) DEFAULT 'unknown',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, language, lemma)
);

CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    text_hash CHAR(64),
    coverage_pct DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_tokens (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    surface TEXT NOT NULL,
    lemma TEXT NOT NULL,
    grade_level INTEGER,
    is_known BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE INDEX IF NOT EXISTS idx_known_words_user_language ON known_words(user_id, language);
CREATE INDEX IF NOT EXISTS idx_known_words_user_id ON known_words(user_id);
CREATE INDEX IF NOT EXISTS idx_known_words_lemma ON known_words(lemma);
CREATE INDEX IF NOT EXISTS idx_known_words_grade_level ON known_words(grade_level);
CREATE INDEX IF NOT EXISTS idx_known_words_metadata_gin ON known_words USING gin (metadata);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_text_hash ON analyses(text_hash);

CREATE INDEX IF NOT EXISTS idx_tokens_analysis_id ON analysis_tokens(analysis_id);
CREATE INDEX IF NOT EXISTS idx_tokens_is_known ON analysis_tokens(is_known);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


DOWNGRADE_SQL = """
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP TABLE IF EXISTS analysis_tokens;
DROP TABLE IF EXISTS analyses;
DROP TABLE IF EXISTS known_words;
DROP TABLE IF EXISTS users;
"""


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(DOWNGRADE_SQL)
