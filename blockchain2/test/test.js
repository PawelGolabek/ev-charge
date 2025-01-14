const { expect } = require("chai");
const { ethers } = require("hardhat");
const { BigNumber } = require("ethers")

describe("EVCharge", function () {
  let EVCharge, evCharge;
  let owner, admin, seller, client;
  let accounts;
  let testAddressNew = "0x553D473C0A05044f6a0CA0cc78f29Ece1F0672Eb";    // publicly known hardhat test accounts
  let testAddressClient = "0xdD2FD4581271e230360230F9337D5c0430Bf44C0";
  let testAddressSeller = "0x90F79bf6EB2c4f870365E785982E1f101E93b906";
  let testAddressAdmin = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8";
  let testAddressCharger = "0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199";
  

  beforeEach(async function () {
    // Get the accounts from Hardhat
    accounts = await ethers.getSigners();
    [owner, admin, client, seller] = accounts;


    charger = await ethers.getSigner("0x8626f6940E2eb28930eFb4CeF49B2d1F2C9C1199");
    // Deploy the contract
    EVCharge = await ethers.getContractFactory("EVCharge");
    evCharge = await EVCharge.deploy();
    await evCharge.waitForDeployment();

  });

  it("should initialize with the correct admin", async function () {
    expect(await evCharge.initialAdmin()).to.equal(owner.address);
  });

  it("should allow admin to add a user", async function () {
    await evCharge.addUser(testAddressNew, 3, 1000);
    const user = await evCharge.users(testAddressNew);
    expect(user.role).to.equal(3); // Role.Client (3)
    expect(user.balance).to.equal(1000);
  });

  it("should allow a client to increase balance", async function () {
    initialBalance = 0; // assuming client has 0 at start. Will fail if value changes
    const increment = 1000; 
    await evCharge.connect(client).increaseBalance({ value: increment });
    const balance = await evCharge.connect(client).checkMyBalance();
  
    expect(balance).to.equal(initialBalance + increment);
  });

  it("should allow seller to update charger price", async function () {
    await evCharge.connect(seller).addCharger(testAddressCharger, 20);
    await evCharge.connect(seller).updateChargerPrice(testAddressCharger, 30);
    const charger = await evCharge.chargers(testAddressCharger);
    expect(charger.pricePerKWh).to.equal(30);
  });


  it("Should return all charging sessions", async function () {
    // Validate no charging sessions initially
    const chargingSessions = await evCharge.getAllChargingSessions();
    expect(chargingSessions).to.be.an("array").that.is.empty;

    message = "10 200"
    const messageHash = ethers.hashMessage(message);
    const signature = await client.signMessage(message);

    // increase balance so client can pay
    const increment = 1000; 
    await evCharge.connect(client).increaseBalance({ value: increment });


    // Simulate adding a charging session
    const demand = 10;
    const totalCost = 200;
    await evCharge.connect(client).validateClient(
      client.address,
      testAddressCharger,
      demand,
      messageHash,
      signature
    );

    const updatedChargingSessions = await evCharge.getAllChargingSessions();
    expect(updatedChargingSessions).to.be.an("array").that.has.length(1);
    expect(updatedChargingSessions[0].clientAddress).to.equal(client.address);
  });

  it("Should return all users", async function () {
    const [userAddrs, userRoles, userBalances] = await evCharge.getAllUsers();
    expect(userAddrs).to.be.an("array").that.is.not.empty;
    expect(userRoles).to.be.an("array").that.is.not.empty;
    expect(userBalances).to.be.an("array").that.is.not.empty;

    const adminIndex = userAddrs.indexOf(admin.address);
    expect(userRoles[adminIndex]).to.equal(1); // 1 predefined account for tests. Will fail if changed starting conditions
    expect(userBalances[adminIndex]).to.equal(0);

    const sellerIndex = userAddrs.indexOf(seller.address);
    expect(userRoles[sellerIndex]).to.equal(2); // 1 predefined account for tests. Will fail if changed starting conditions
    expect(userBalances[sellerIndex]).to.equal(250);
  });

  
  it("Should return seller's contribution", async function () {
    // Validate initial contribution for the seller
    const initialContribution = await evCharge.connect(seller).checkMyContribution();
    expect(initialContribution).to.equal(0);
    // increase balance so client can pay
    const increment = 1000; 
    await evCharge.connect(client).increaseBalance({ value: increment });
    // simple transaction so contribution changes
    message = "10 200"
    const demand = 10;
    const totalCost = 200;
    const messageHash = ethers.hashMessage(message);
    const signature = await client.signMessage(message);
    await evCharge.connect(client).validateClient(
      client.address,
      testAddressCharger,
      demand,
      messageHash,
      signature
    );
    // add contribution
    const updatedContribution = await evCharge.connect(seller).checkMyContribution();
    expect(updatedContribution).to.equal(200);
  });

  // to make more complicated once signatures work
  it("Should allow admin to withdraw Ether", async function () {

    // Client transaction so contract has money
    const increment = 1000; 
    await evCharge.connect(client).increaseBalance({ value: increment });

    const updatedChargingSessions = await evCharge.getAllChargingSessions();

    depositAmount = BigInt(0);
    let contractBalance = await ethers.provider.getBalance(evCharge.target);

    // Admin withdraws part of the Ether
    const withdrawAmount = BigInt(1);
    const adminInitialBalance = BigInt(await ethers.provider.getBalance(owner.address)); 
    const tx = await evCharge.connect(owner).adminWithdraw(withdrawAmount);
    const receipt = await tx.wait();

    const gasUsed = receipt.gasUsed * receipt.gasPrice;
    const adminFinalBalance = await ethers.provider.getBalance(owner.address);
    contractBalance = await ethers.provider.getBalance(evCharge.target);

    expect(adminFinalBalance).to.equal(adminInitialBalance + withdrawAmount - gasUsed);
    expect(contractBalance).to.equal(depositAmount - withdrawAmount + BigInt(increment));
  });


  it("Should allow admin to record a transaction for a seller", async function () {
    const txHash = ethers.keccak256(ethers.toUtf8Bytes("test transaction"));
    const amount = 500;
    await evCharge.connect(owner).recordTransaction(testAddressSeller, amount, txHash);
    
    // Retrieve the recorded transaction
    const recordedTransaction = await evCharge.summaryTransactions(0);
    
    expect(recordedTransaction.admin).to.equal(owner.address);
    expect(recordedTransaction.seller).to.equal(testAddressSeller);
    expect(recordedTransaction.amountPaid).to.equal(amount);
    expect(recordedTransaction.transactionHash).to.equal(txHash);
  })
  
});
