CREATE TABLE Role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_address TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    balance INTEGER,
    contribution INTEGER,
    FOREIGN KEY (role_id) REFERENCES Role (id)
);

CREATE TABLE Charger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    charger_address TEXT NOT NULL,
    price_per_kwh INTEGER NOT NULL,
    owner TEXT NOT NULL
);

CREATE TABLE ChargingSession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_address TEXT NOT NULL,
    charger_address TEXT NOT NULL,
    total_cost INTEGER NOT NULL,
    demand INTEGER NOT NULL,
    is_completed BOOLEAN NOT NULL,
    charger_owner TEXT NOT NULL
);
-- Insert predefined roles
INSERT INTO Role (name) VALUES ('None'), ('Admin'), ('Seller'), ('Client');

-- Insert initial admin user
INSERT INTO User (user_address, role_id, balance, contribution)
VALUES ('0x70997970C51812dc3A010C7d01b50e0d17dc79C8', 
        (SELECT id FROM Role WHERE name = 'Admin'), 
        0, 
        0);

-- Insert predefined users
INSERT INTO User (user_address, role_id, balance, contribution)
VALUES 
    ('0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC', (SELECT id FROM Role WHERE name = 'Admin'), 0, 0),
    ('0x90F79bf6EB2c4f870365E785982E1f101E93b906', (SELECT id FROM Role WHERE name = 'Seller'), 250, 0),
    ('0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65', (SELECT id FROM Role WHERE name = 'Seller'), 250, 0),
    ('0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc', (SELECT id FROM Role WHERE name = 'Seller'), 250, 0),
    ('0x976EA74026E726554dB657fA54763abd0C3a0aa9', (SELECT id FROM Role WHERE name = 'Seller'), 500, 0),
    ('0x14dC79964da2C08b23698B3D3cc7Ca32193d9955', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0x23618e81E3f5cdF7f54C3d65f7FBc0aBf5B21E8f', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xa0Ee7A142d267C1f36714E4a8F75612F20a79720', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xBcd4042DE499D14e55001CcbB24a551F3b954096', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0x71bE63f3384f5fb98995898A86B02Fb2426c5788', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xFABB0ac9d68B0B445fB7357272Ff202C5651694a', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xdF3e18d64BC6A983f673Ab319CCaE4f1a57C7097', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xcd3B766CCDd6AE721141F452C550Ca635964ce71', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0x2546BcD3c84621e976D8185a91A922aE77ECEc30', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xbDA5747bFD65F08deb54cb465eB87D40e51B197E', (SELECT id FROM Role WHERE name = 'Client'), 500, 0),
    ('0xdD2FD4581271e230360230F9337D5c0430Bf44C0', (SELECT id FROM Role WHERE name = 'Client'), 500, 0);

-- Insert predefined charger
INSERT INTO Charger (charger_address, price_per_kwh, owner)
VALUES ('0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199', 20, '0x90F79bf6EB2c4f870365E785982E1f101E93b906');
