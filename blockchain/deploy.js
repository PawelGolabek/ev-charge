
/** @type import('hardhat/config').HardhatUserConfig */
async function main() {
    try {
        
        // Compile contracts
        await hre.run('compile');

        // Get the contract factory using artifacts
        const EVChargeArtifact = await hre.artifacts.readArtifact("EVCharge");

        // Use Hardhat's low-level deployment utilities
        const EVChargeContract = await hre.network.provider.send("eth_sendTransaction", [{
            data: EVChargeArtifact.bytecode
        }]);

        console.log("Deployed EVCharge contract to: ", EVChargeContract);

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
