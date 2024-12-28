async function main() {
    try {
        const MyContract = await hre.ethers.getContractFactory("EVCharge");
        
        // Deploy the contract
        const MyContractDeployed = await MyContract.deploy();

        // Log the address from the receipt
        console.log("Deployed MyContract to: ", MyContractDeployed.address);
        console.log(MyContractDeployed);

    } catch (error) {
        console.error("Deployment failed:", error);
        process.exit(1);
    }    }

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("Error in main:", error);
        process.exit(1);
    });
