const path = require("path");
const Database = require("better-sqlite3");

const dbPath = path.join(__dirname, "..", "data.sqlite");
const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT,
    file_id TEXT,
    caption TEXT,
    created_at INTEGER NOT NULL
  );
`);

function generateCode() {
  let code;
  do {
    code = Math.floor(100000 + Math.random() * 900000).toString();
  } while (getCode(code));
  return code;
}

function saveCode({ type, content = null, fileId = null, caption = null }) {
  const code = generateCode();
  db.prepare(
    `INSERT INTO codes (code, type, content, file_id, caption, created_at)
     VALUES (?, ?, ?, ?, ?, ?)`
  ).run(code, type, content, fileId, caption, Date.now());
  return code;
}

function getCode(code) {
  return db.prepare(`SELECT * FROM codes WHERE code = ?`).get(code);
}

module.exports = { saveCode, getCode };
