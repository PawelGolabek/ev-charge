// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract EVCharge {
    enum Role { None, Admin, Seller, Client }

    struct User {
        address userAddress;
        Role role;
        int balance;
        uint32 contribution;
    }
    struct Charger {
        address chargerAddress;
        uint pricePerKWh;
        address owner;
    }

    struct ChargingSession {
        address clientAddress;
        address chargerAddress;
        uint32 totalCost;
        uint32 demand;
        bool isCompleted;
        address chargerOwner;
    }

    mapping(address => User) public users;
    mapping(address => Charger) public chargers;
    address public immutable initialAdmin;
    address[] public userAddresses;
    ChargingSession[] public chargingSessions;
    uint public conversionRate = 1000; // Example: 1 ETH = 1000 balance units

constructor() {
    initialAdmin = msg.sender;
    userAddresses.push(msg.sender);

    users[msg.sender] = User({
        userAddress: msg.sender,
        role: Role.Admin,
        balance: 0,
        contribution: 0
    });

    address[18] memory predefinedUsers = [
        0x70997970C51812dc3A010C7d01b50e0d17dc79C8,
        0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC,
        0x90F79bf6EB2c4f870365E785982E1f101E93b906,
        0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65,
        0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc,
        0x976EA74026E726554dB657fA54763abd0C3a0aa9,
        0x14dC79964da2C08b23698B3D3cc7Ca32193d9955,
        0x23618e81E3f5cdF7f54C3d65f7FBc0aBf5B21E8f,
        0xa0Ee7A142d267C1f36714E4a8F75612F20a79720,
        0xBcd4042DE499D14e55001CcbB24a551F3b954096,
        0x71bE63f3384f5fb98995898A86B02Fb2426c5788,
        0xFABB0ac9d68B0B445fB7357272Ff202C5651694a,
        0x1CBd3b2770909D4e10f157cABC84C7264073C9Ec,
        0xdF3e18d64BC6A983f673Ab319CCaE4f1a57C7097,
        0xcd3B766CCDd6AE721141F452C550Ca635964ce71,
        0x2546BcD3c84621e976D8185a91A922aE77ECEc30,
        0xbDA5747bFD65F08deb54cb465eB87D40e51B197E,
        0xdD2FD4581271e230360230F9337D5c0430Bf44C0
    ];

    Role[18] memory roles = [
        Role.Admin, Role.Admin, Role.Seller, Role.Seller, Role.Seller,
        Role.Seller, Role.Client, Role.Client, Role.Client, Role.Client,
        Role.Client, Role.Client, Role.Client, Role.Client, Role.Client,
        Role.Client, Role.Client, Role.Client
    ];

    int256[18] memory balances = [
        int256(0), int256(0), int256(250), int256(250), int256(250),
        int256(500), int256(500), int256(500), int256(500), int256(500),
        int256(500), int256(500), int256(500), int256(500), int256(500),
        int256(500), int256(500), int256(500)
    ];

    for (uint256 i = 0; i < predefinedUsers.length; i++) {
        address addr = predefinedUsers[i];
        userAddresses.push(addr);
        users[addr] = User({
            userAddress: addr,
            role: roles[i],
            balance: balances[i],
            contribution: 0
        });
    }

    address chargerAddress = 0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199;
    chargers[chargerAddress] = Charger({
        chargerAddress: chargerAddress,
        pricePerKWh: 20,
        owner: 0x90F79bf6EB2c4f870365E785982E1f101E93b906
    });


}

    // nie wiem czy dalej dziala po ostatnich zmianach
    function addCharger(address _chargerAddress, uint _pricePerKWh) public {
        require(users[msg.sender].role == Role.Seller, "Only seller can add chargers");
        chargers[_chargerAddress] = Charger({
            chargerAddress: _chargerAddress,
            pricePerKWh: _pricePerKWh,
            owner: msg.sender
        });
    }

    event ChargingCompleted(address indexed clientAddress, uint32 totalCost, address indexed chargerOwner, address chargerAddress, uint32 demand);

    function completeCharging(address _clientAddress, address _chargerAddress) public {
        require(chargers[_chargerAddress].chargerAddress != address(0), "Invalid charger address");
        require(msg.sender == chargers[_chargerAddress].owner, "Only charger owner can complete the charging");
        require(users[_clientAddress].userAddress != address(0), "Client does not exist");

        bool sessionFound = false;
        for (uint i = 0; i < chargingSessions.length; i++) {
            if (chargingSessions[i].clientAddress == _clientAddress && 
                chargingSessions[i].chargerAddress == _chargerAddress && 
                !chargingSessions[i].isCompleted) {
                sessionFound = true;

                uint32 totalCost = chargingSessions[i].totalCost;
                uint32 demand = chargingSessions[i].demand;

                users[_clientAddress].balance -= int256(uint256(totalCost));
                address chargerOwner = chargers[_chargerAddress].owner;
                users[chargerOwner].contribution += totalCost;

                chargingSessions[i].isCompleted = true;

                emit ChargingCompleted(_clientAddress, totalCost, chargerOwner, _chargerAddress, demand);
                break;
            }
        }
        require(sessionFound, "No active charging session found to complete");
    }

    function getAllChargingSessions() public view returns (ChargingSession[] memory) {
        return chargingSessions;
    }
    function getAllUsers() public view returns (address[] memory, uint8[] memory, int256[] memory) {
        uint256 userCount = userAddresses.length;
        address[] memory userAddrs = new address[](userCount); 
        uint8[] memory userRoles = new uint8[](userCount);
        int256[] memory userBalances = new int256[](userCount);

        // Iterate through all user addresses
        for (uint256 i = 0; i < userCount; i++) {
            address userAddr = userAddresses[i];
            userAddrs[i] = userAddr;
            userRoles[i] = uint8(users[userAddr].role); 
            userBalances[i] = users[userAddr].balance; 
        }

        return (userAddrs, userRoles, userBalances);
    }


    event ChargingAuthorized(address indexed clientAddress, address indexed chargerAddress, uint32 demand, bool isAuthorized);

    function validateClient(address _clientAddress, address _chargerAddress, uint32 _demand) public returns (bool) {
        require(users[_clientAddress].userAddress != address(0), "User does not exist");
        require(users[_clientAddress].role == Role.Client, "User is not a client");
        require(users[_clientAddress].balance > 100, "Client has insufficient balance");
        require(chargers[_chargerAddress].chargerAddress != address(0), "Charger does not exist");

        uint32 totalCost = uint32(chargers[_chargerAddress].pricePerKWh * uint256(_demand));
        require(totalCost >= chargers[_chargerAddress].pricePerKWh, "Cost overflow");

        chargingSessions.push(ChargingSession({
            clientAddress: _clientAddress,
            chargerAddress: _chargerAddress,
            totalCost: totalCost,
            demand: _demand,
            isCompleted: false,
            chargerOwner: chargers[_chargerAddress].owner
        }));

        bool isAuthorized = users[_clientAddress].balance >= int256(uint256(totalCost));
        emit ChargingAuthorized(_clientAddress, _chargerAddress, _demand, isAuthorized);

        return isAuthorized;
    }

    function isChargingSessionActive(address _clientAddress, address _chargerAddress) public view returns (bool) {
        for (uint i = 0; i < chargingSessions.length; i++) {
            if (chargingSessions[i].clientAddress == _clientAddress && 
                chargingSessions[i].chargerAddress == _chargerAddress && 
                !chargingSessions[i].isCompleted) {
                return true;
            }
        }
        return false;
    }

    function checkMyBalance() public view returns (int) {
        require(users[msg.sender].userAddress != address(0), "User does not exist");
        require(users[msg.sender].role == Role.Client, "User is not a client");
        return users[msg.sender].balance;
    }
    
    
    function increaseBalance() public payable {
        require(users[msg.sender].userAddress != address(0), "User does not exist");
        require(users[msg.sender].role == Role.Client, "User is not a client");
        require(msg.value > 0, "Must send ETH to increase balance");

        uint256 balanceIncrease = msg.value * conversionRate;
        users[msg.sender].balance += int256(balanceIncrease);
    }

    function setConversionRate(uint _newRate) public {
        require(users[msg.sender].role == Role.Admin, "Only admin can set conversion rate");
        require(_newRate > 0, "Conversion rate must be greater than zero");
        conversionRate = _newRate;
    }

    function checkMyContribution() public view returns (int) {
        require(users[msg.sender].role == Role.Seller, "User is not a seller");
        require(users[msg.sender].userAddress != address(0), "User does not exist");
        return int32(users[msg.sender].contribution);

    }
}