// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;
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
        address chargerOwner;
    }
    struct SummaryTransaction {
        address admin;
        address seller;
        uint256 amountPaid;
        bytes32 transactionHash;
    }
    SummaryTransaction[] public summaryTransactions;


    mapping(address => User) public users;
    mapping(address => Charger) public chargers;
    address public immutable initialAdmin;
    address[] public userAddresses;
    ChargingSession[] public chargingSessions;

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
            Role.Admin, Role.Client, Role.Seller, Role.Seller, Role.Seller,
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
    ////// view //////

    function getAllChargingSessions() public view returns (ChargingSession[] memory) {
        return chargingSessions;
    }

    // get all users
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

    // get client balance
    function checkMyBalance() public view returns (int) {
        require(users[msg.sender].userAddress != address(0), "User does not exist");
        require(users[msg.sender].role == Role.Client, "User is not a client");
        return users[msg.sender].balance;
    }    
    
    // check how much total seller contribution
    function checkMyContribution() public view returns (int) {
        require(users[msg.sender].role == Role.Seller, "User is not a seller");
        require(users[msg.sender].userAddress != address(0), "User does not exist");
        return int32(users[msg.sender].contribution);

    }
    
    /////// From now on need auth
    function updateChargerPrice(address chargerAddress, uint newPricePerKWh) public {
        require(users[msg.sender].role == Role.Seller, "Only seller can update charger price");
        require(chargers[chargerAddress].chargerAddress != address(0), "Charger does not exist");
        require(chargers[chargerAddress].owner == msg.sender, "Only charger owner can update price");

        chargers[chargerAddress].pricePerKWh = newPricePerKWh;
    }

    event ChargingAuthorized(address indexed clientAddress, address indexed chargerAddress, uint32 demand, bool isAuthorized);
    // create charging session
   function validateClient(address clientAddress,
            address chargerAddress,
            uint32 demand,
            bytes32 messageHash,
            bytes memory signature) 
        public returns (bool) {
        require(users[clientAddress].userAddress != address(0), "User does not exist");
        require(users[clientAddress].role == Role.Client, "User is not a client");
        require(users[clientAddress].balance > 100, "Client has insufficient balance");
        require(chargers[chargerAddress].chargerAddress != address(0), "Charger does not exist");
        require(getSigner(messageHash, signature) == clientAddress, "Bad signature");

        uint32 totalCost = uint32(chargers[chargerAddress].pricePerKWh * uint256(demand));
        require(totalCost >= chargers[chargerAddress].pricePerKWh, "Cost overflow");

        chargingSessions.push(ChargingSession({
            clientAddress: clientAddress,
            chargerAddress: chargerAddress,
            totalCost: totalCost,
            demand: demand,
            chargerOwner: chargers[chargerAddress].owner
        }));
        

        users[clientAddress].balance -= int256(uint256(totalCost));
        address chargerOwner = chargers[chargerAddress].owner;
        users[chargerOwner].contribution += totalCost;

        bool isAuthorized = users[clientAddress].balance >= int256(uint256(totalCost));
        emit ChargingAuthorized(clientAddress, chargerAddress, demand, isAuthorized);    // for charger
        return isAuthorized;
    }

    // admin withdraw eth
    function adminWithdraw(uint256 amount) public {
        require(msg.sender == initialAdmin, "Only admin can withdraw funds");
        require(address(this).balance >= amount, "Insufficient contract balance");

        // Transfer the specified amount of Ether to the admin
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Withdrawal failed");
    }

    // user increase balance
    function increaseBalance() public payable {
        require(users[msg.sender].userAddress != address(0), "User does not exist");
        require(users[msg.sender].role == Role.Client, "User is not a client");
        require(msg.value > 0, "Must send ETH to increase balance");

        uint256 balanceIncrease = msg.value;
        users[msg.sender].balance += int256(balanceIncrease);
    }
    // record summary payment
    function recordTransaction(address seller, uint256 amount, bytes32 txHash) public {
        require(msg.sender == initialAdmin, "Only admin can record transactions");
        require(users[seller].role == Role.Seller, "Recipient must be a seller");
        require(amount > 0, "Amount must be greater than zero");

        summaryTransactions.push(SummaryTransaction({
            admin: msg.sender,
            seller: seller,
            amountPaid: amount,
            transactionHash: txHash
        }));
    }

    ////// add //////
    function addCharger(address chargerAddress, uint pricePerKWh) public {
        require(users[msg.sender].role == Role.Seller, "Only seller can add chargers");
        chargers[chargerAddress] = Charger({
            chargerAddress: chargerAddress,
            pricePerKWh: pricePerKWh,
            owner: msg.sender
        });
    }

    function addUser(address userAddress, Role role, int initialBalance) public {
        require(msg.sender == initialAdmin, "Only admin can add users");
        require(users[userAddress].userAddress == address(0), "User already exists");

        users[userAddress] = User({
            userAddress: userAddress,
            role: role,
            balance: initialBalance,
            contribution: 0
        });

        userAddresses.push(userAddress);
    }

    ////// utility //////
    function getSigner(
        bytes32 messageHash,
        bytes memory signature
    ) public pure returns (address) {
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(signature);
        return ecrecover(messageHash, v, r, s);
    }

    function splitSignature(
        bytes memory sig
    )
        public
        pure
        returns (bytes32 r, bytes32 s, uint8 v)
    {
        require(sig.length == 65, "Invalid signature length");

        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
    }
    
}

