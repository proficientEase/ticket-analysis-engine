-- Hardware Asset Tracking Table
CREATE TABLE IF NOT EXISTS network_devices (
    device_id  TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    model TEXT NOT NULL,
    firmware_version TEXT NOT NULL,
    ip_address TEXT UNIQUE
);

-- Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    severity TEXT CHECK(severity IN ('P1','P2','P3','P4')),
    external_ref_id TEXT UNIQUE,
    customer TEXT NOT NULL,
    device_id TEXT,                 --Links to network_devices(device_id)
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT CHECK(status IN ('Open','In_Progress','Pending','Resolved')),
    timestamp DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT,
    FOREIGN KEY (device_id) REFERENCES network_devices(device_id)
);


--(6/11/2026)
--Future Functionality


CREATE TABLE IF NOT EXISTS ticket_routing_history (
    routing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER,
    assigned_tier INTEGER CHECK(assigned_tier IN (1, 2, 3)),
    handoff_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);
