from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "payments" (
    "uuid" UUID NOT NULL PRIMARY KEY,
    "date" TIMESTAMPTZ,
    "document" VARCHAR(200) UNIQUE,
    "beneficiary" VARCHAR(200) NOT NULL,
    "amount" DECIMAL(15,2) NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "uuid" UUID NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(255) UNIQUE,
    "hashed_password" VARCHAR(128) NOT NULL,
    "disabled" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "apikeys" (
    "uuid" UUID NOT NULL PRIMARY KEY,
    "hashed_key" VARCHAR(128) NOT NULL,
    "key_prefix" VARCHAR(10) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL DEFAULT True,
    "user_id" UUID NOT NULL REFERENCES "users" ("uuid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
