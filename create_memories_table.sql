CREATE TABLE memories (
    user_id    VARCHAR(255) NOT NULL,
    `key`      VARCHAR(255) NOT NULL,
    `value`    TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, `key`)
);
