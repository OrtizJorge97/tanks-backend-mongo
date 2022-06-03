db = db.getSiblingDB("tanks_db");

//db.animal_tb.drop();
db.createCollection("users");
db.users.insert(
    {
        name: "Test",
        last_name: "Ortiz",
        email: "jorge97@gmail.com",
        password: "test_password",
        user_verified: true
    }
)