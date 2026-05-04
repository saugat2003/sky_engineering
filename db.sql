CREATE TABLE IF NOT EXISTS auth_user (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    email               INTEGER NOT NULL UNIQUE,         
    username            TEXT,
    password            TEXT,
   
);
-- ============================================================
-- 1. USER AUTHENTICATION & PROFILES
-- (extends Django's built-in auth_user table)
-- ============================================================

CREATE TABLE IF NOT EXISTS user_profile (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL UNIQUE,          -- FK → Django auth_user.id
    bio                 TEXT,
    phone               VARCHAR(30),
    avatar              VARCHAR(255),                     -- file path / URL
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
);


-- ============================================================
-- 2. DEPARTMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS department (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                VARCHAR(100) NOT NULL UNIQUE,     -- e.g. xTV_Web, Mobile
    description         TEXT,
    specialisation      TEXT,                             -- area of technical focus
    head_user_id        INTEGER,                          -- FK → auth_user (Department Head)
    is_active           BOOLEAN NOT NULL DEFAULT 1,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (head_user_id) REFERENCES auth_user (id) ON DELETE SET NULL
);


-- ============================================================
-- 3. TEAM TYPES  (e.g. Platform, Product, Reliability…)
-- ============================================================

CREATE TABLE IF NOT EXISTS team_type (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT
);


-- ============================================================
-- 4. TEAMS
-- ============================================================

CREATE TABLE IF NOT EXISTS team (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                VARCHAR(150) NOT NULL UNIQUE,     -- e.g. "Code Warriors"
    department_id       INTEGER NOT NULL,
    team_type_id        INTEGER,
    manager_id          INTEGER,                          -- FK → auth_user (Team Leader)

    -- Identity & purpose
    mission             TEXT,                             -- team purpose / responsibilities
    description         TEXT,

    -- Agile / project management
    jira_project_name   VARCHAR(150),
    jira_board_link     VARCHAR(255),
    workstream          VARCHAR(150),
    agile_practices     TEXT,                             -- Scrum, Kanban, SAFe …
    concurrent_projects VARCHAR(20),                      -- e.g. "6+"

    -- Engineering metadata
    development_focus   TEXT,
    key_skills          TEXT,                             -- comma-separated or JSON
    versioning_approach TEXT,

    -- Contact & comms
    slack_channels      TEXT,                             -- comma-separated channel names
    daily_standup_link  VARCHAR(255),
    team_wiki_url       VARCHAR(255),
    wiki_search_terms   TEXT,

    -- Lifecycle
    status              VARCHAR(20) NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'restructured', 'disbanded')),
    disbanded_at        DATETIME,

    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE RESTRICT,
    FOREIGN KEY (team_type_id)  REFERENCES team_type (id) ON DELETE SET NULL,
    FOREIGN KEY (manager_id)    REFERENCES auth_user (id) ON DELETE SET NULL
);


-- ============================================================
-- 5. TEAM MEMBERS  (many-to-many: auth_user ↔ team)
-- ============================================================

CREATE TABLE IF NOT EXISTS team_member (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id             INTEGER NOT NULL,
    user_id             INTEGER NOT NULL,
    role                VARCHAR(100),                     -- e.g. "Senior Engineer"
    joined_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    left_at             DATETIME,
    is_active           BOOLEAN NOT NULL DEFAULT 1,
    UNIQUE (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES team (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
);


-- ============================================================
-- 6. CODE REPOSITORIES
-- ============================================================

CREATE TABLE IF NOT EXISTS repository (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id             INTEGER NOT NULL,
    name                VARCHAR(150) NOT NULL,
    url                 VARCHAR(255) NOT NULL,
    platform            VARCHAR(50) DEFAULT 'GitHub',     -- GitHub, GitLab, Bitbucket …
    description         TEXT,
    is_primary          BOOLEAN NOT NULL DEFAULT 0,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES team (id) ON DELETE CASCADE
);


-- ============================================================
-- 7. TEAM DEPENDENCIES  (upstream / downstream)
-- ============================================================

CREATE TABLE IF NOT EXISTS team_dependency (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    from_team_id        INTEGER NOT NULL,    -- the team that has the dependency
    to_team_id          INTEGER NOT NULL,    -- the team being depended on
    dependency_type     VARCHAR(100),        -- e.g. "Infrastructure Support", "Bug Resolution"
    description         TEXT,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (from_team_id, to_team_id),
    CHECK (from_team_id != to_team_id),      -- prevent a team depending on itself
    FOREIGN KEY (from_team_id) REFERENCES team (id) ON DELETE CASCADE,
    FOREIGN KEY (to_team_id)   REFERENCES team (id) ON DELETE CASCADE
);


-- ============================================================
-- 8. SOFTWARE OWNED BY TEAM
-- ============================================================

CREATE TABLE IF NOT EXISTS software_product (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id             INTEGER NOT NULL,
    name                VARCHAR(200) NOT NULL,
    description         TEXT,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES team (id) ON DELETE CASCADE
);


-- ============================================================
-- 9. CONTACT CHANNELS  (email, Slack, Teams …)
-- ============================================================

CREATE TABLE IF NOT EXISTS contact_channel (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id             INTEGER NOT NULL,
    channel_type        VARCHAR(50) NOT NULL
                            CHECK (channel_type IN ('email', 'slack', 'teams', 'other')),
    value               VARCHAR(255) NOT NULL,            -- e.g. team@broadcast.com or #channel-name
    is_primary          BOOLEAN NOT NULL DEFAULT 0,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES team (id) ON DELETE CASCADE
);


-- ============================================================
-- 10. MESSAGES  (internal messaging between users)
-- ============================================================

CREATE TABLE IF NOT EXISTS message (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id           INTEGER NOT NULL,
    recipient_id        INTEGER NOT NULL,
    subject             VARCHAR(255),
    body                TEXT NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'inbox'
                            CHECK (status IN ('inbox', 'sent', 'draft', 'deleted')),
    is_read             BOOLEAN NOT NULL DEFAULT 0,
    parent_message_id   INTEGER,                          -- for threading / replies
    sent_at             DATETIME,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id)        REFERENCES auth_user (id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id)     REFERENCES auth_user (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_message_id) REFERENCES message (id) ON DELETE SET NULL
);


-- ============================================================
-- 11. SCHEDULED MEETINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS meeting (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    organiser_id        INTEGER NOT NULL,
    team_id             INTEGER,                          -- optional: linked to a team
    title               VARCHAR(255) NOT NULL,
    description         TEXT,
    platform            VARCHAR(50),                      -- Zoom, Teams, Google Meet …
    meeting_link        VARCHAR(255),
    scheduled_at        DATETIME NOT NULL,
    duration_minutes    INTEGER DEFAULT 60,
    recurrence          VARCHAR(20) DEFAULT 'none'
                            CHECK (recurrence IN ('none', 'daily', 'weekly', 'monthly')),
    status              VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                            CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organiser_id) REFERENCES auth_user (id) ON DELETE CASCADE,
    FOREIGN KEY (team_id)      REFERENCES team (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS meeting_attendee (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id          INTEGER NOT NULL,
    user_id             INTEGER NOT NULL,
    rsvp_status         VARCHAR(20) DEFAULT 'pending'
                            CHECK (rsvp_status IN ('pending', 'accepted', 'declined')),
    UNIQUE (meeting_id, user_id),
    FOREIGN KEY (meeting_id) REFERENCES meeting (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES auth_user (id) ON DELETE CASCADE
);


-- ============================================================
-- 12. AUDIT LOG  (tracks all edits / updates for traceability)
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER,                          -- NULL if system action
    table_name          VARCHAR(100) NOT NULL,
    record_id           INTEGER NOT NULL,
    action              VARCHAR(20) NOT NULL
                            CHECK (action IN ('CREATE', 'UPDATE', 'DELETE')),
    changed_fields      TEXT,                             -- JSON snapshot of changed values
    ip_address          VARCHAR(45),
    timestamp           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL
);


-- ============================================================
-- 13. NOTIFICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS notification (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    message             TEXT NOT NULL,
    link                VARCHAR(255),                     -- relative URL to navigate to
    is_read             BOOLEAN NOT NULL DEFAULT 0,
    created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE CASCADE
);


-- ============================================================
-- INDEXES  (performance on common lookups)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_team_department     ON team (department_id);
CREATE INDEX IF NOT EXISTS idx_team_manager        ON team (manager_id);
CREATE INDEX IF NOT EXISTS idx_team_status         ON team (status);
CREATE INDEX IF NOT EXISTS idx_team_member_team    ON team_member (team_id);
CREATE INDEX IF NOT EXISTS idx_team_member_user    ON team_member (user_id);
CREATE INDEX IF NOT EXISTS idx_dependency_from     ON team_dependency (from_team_id);
CREATE INDEX IF NOT EXISTS idx_dependency_to       ON team_dependency (to_team_id);
CREATE INDEX IF NOT EXISTS idx_repo_team           ON repository (team_id);
CREATE INDEX IF NOT EXISTS idx_message_sender      ON message (sender_id);
CREATE INDEX IF NOT EXISTS idx_message_recipient   ON message (recipient_id);
CREATE INDEX IF NOT EXISTS idx_meeting_organiser   ON meeting (organiser_id);
CREATE INDEX IF NOT EXISTS idx_meeting_scheduled   ON meeting (scheduled_at);
CREATE INDEX IF NOT EXISTS idx_audit_table_record  ON audit_log (table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_notification_user   ON notification (user_id);


-- ============================================================
-- SAMPLE SEED DATA  (aligned with the Excel registry)
-- ============================================================

-- Departments (6 from the registry)
INSERT OR IGNORE INTO department (name, description, specialisation) VALUES
    ('xTV_Web',          'Cross-platform TV web engineering',      'Web / streaming platforms'),
    ('Mobile',           'Mobile application development',         'iOS & Android'),
    ('Native TVs',       'Native TV application engineering',      'Smart TV apps'),
    ('Programme',        'Programme delivery and management',      'Agile delivery'),
    ('Reliability_Tool', 'Site reliability and internal tooling',  'SRE / DevOps'),
    ('Arch',             'Architecture and platform design',       'System architecture');

-- Team Types
INSERT OR IGNORE INTO team_type (name, description) VALUES
    ('Platform',    'Infrastructure and platform teams'),
    ('Product',     'Customer-facing product teams'),
    ('Reliability', 'SRE and reliability teams'),
    ('Security',    'Security and compliance teams'),
    ('Agile',       'Agile coaching and process teams');


-- ============================================================
-- END OF SCHEMA
-- ============================================================



-- Core data (from the Excel registry)

-- department — the 6 departments (xTV_Web, Mobile, Native TVs, etc.) with head and specialisation
-- team — all team fields: name, mission, Jira, Slack, wiki, agile practices, lifecycle status (active/restructured/disbanded)
-- team_member — many-to-many between users and teams, with role and join/leave dates
-- team_type — classifies teams (Platform, Product, SRE, etc.)
-- team_dependency — upstream/downstream relationships between teams with direction and type
-- repository — code repos (GitHub links) per team
-- software_product — software owned and evolved by each team
-- contact_channel — email, Slack, Teams channels per team

-- Feature-driven tables (from functional requirements)

-- message — inbox/sent/draft/deleted internal messaging with threading support
-- meeting + meeting_attendee — scheduled meetings with platform, recurrence, and RSVP
-- audit_log — full edit trail (table, record, action, changed fields, timestamp) for every change
-- notification — user-level notifications with read/unread state
-- user_profile — extends Django's auth_user with bio, phone, and avatar