const { loadTestData } = require('./readCSV'); // Import the loadTestData function
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("EVCharge Test with CSV Data", function () {
	const provider = ethers.provider; // Get the Hardhat provider
	let EVCharge, evCharge;
	let accounts;
	let csvData;
	let users = {};
	let chargers = {};
	let sellers = {};

	before(async function () {
		// Load test data from the CSV file
		csvData = await loadTestData();
		//console.log("CSV Data Loaded:", csvData);
	});

	beforeEach(async function () {
		accounts = await ethers.getSigners();

		// Deploy the EVCharge contract
		EVCharge = await ethers.getContractFactory("EVCharge");
		evCharge = await EVCharge.deploy();
		await evCharge.waitForDeployment();
	});

	it("should process transactions and setup accounts based on CSV", async function () {
		for (const row of csvData) {
			const { UserID, ChargerID, ChargerCompany, Location, Demand } = row;

			// Handle client
			if (!users[UserID]) {
				const client = await ethers.Wallet.createRandom().connect(provider);
				await fundWallet(client, 0.1);
				users[UserID] = client; // Store the wallet for future reference

				// Add the user to the contract as a client
				await evCharge.addUser(client.address, 3);
				const increment = ethers.parseEther("0.00001");
				await evCharge.connect(client).increaseBalance({ value: increment });
				//    console.log(`Added client ${UserID}: ${client.address}`);
			}

			// Handle seller
			if (!sellers[Location]) {
				const seller = ethers.Wallet.createRandom().connect(provider);
				sellers[Location] = seller;

				await fundWallet(seller, 0.1);

				// Add the user to the contract as a seller
				await evCharge.addUser(seller.address, 2);
				//     console.log(`Added seller for location ${Location}: ${seller.address}`);
			}

			// Handle charger
			if (!chargers[ChargerID]) {
				const chargerOwner = sellers[Location]; // The seller for this location
				const chargerAddress = ethers.Wallet.createRandom().address;
				chargers[ChargerID] = chargerAddress;

				// Add the charger to the contract
				await evCharge.connect(chargerOwner).addCharger(chargerAddress, 10);
				//   console.log(`Added charger ${ChargerID} owned by ${chargerOwner.address}`);
			}

			// Simulate a transaction
			const client = users[UserID];
			const chargerAddress = chargers[ChargerID];

			// Validate client transaction
			const message = `200`;
			const messageHash = ethers.hashMessage(message);
			const signature = await client.signMessage(message);
			const demand = BigInt(Math.ceil(Demand));

			const initialBalance = await evCharge.connect(client).checkMyBalance();
			const tx = await evCharge.connect(client).validateClient(
				client.address,
				chargerAddress,
				demand,
				messageHash,
				signature
			);

			const receipt = await tx.wait();

			// Calculate the gas cost if needed later
			const gasUsed = receipt.gasUsed * receipt.gasPrice;
			const chargerPrice = (await evCharge.chargers(chargerAddress)).pricePerKWh;

			// Assert the balance is reduced correctly
			const clientBalance = await evCharge.connect(client).checkMyBalance();
			expect(clientBalance).to.equal(initialBalance - demand * chargerPrice);

		//	console.log(`Processed transaction for User ${UserID} with Charger ${ChargerID} at ${Location}`	);
		}
	});
});

const fundWallet = async (wallet, amount) => {
	const [funder] = await ethers.getSigners(); // Use the first account from Hardhat
	await funder.sendTransaction({
		to: wallet.address,
		value: ethers.parseEther(amount.toString()),
	});
};
