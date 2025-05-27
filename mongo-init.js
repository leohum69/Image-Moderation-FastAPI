db = db.getSiblingDB("image_moderation"); // set your DB name here

db.tokens.insertOne({
  token: "my-secret-admin-token",
  is_admin: true,
  created_at: new Date("2025-05-26T19:29:20.007Z")
});