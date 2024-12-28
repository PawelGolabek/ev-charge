import { expect } from 'chai';
import { ethers } from 'hardhat';

describe("TransactionVerifier", function() {
  it("Should return name", async function() {
    const TransactionVerifier = await ethers.getContractFactory("TransactionVerifier");
    const myContractDeployed = await TransactionVerifier.deploy("TransactionVerifierName");

    expect(await myContractDeployed.name()).to.equal("TransactionVerifierName");

    // Wait for the deployment to be confirmed
    
    await new Promise(resolve => setTimeout(resolve, 30000)); // Waits for 10 seconds

    var address = myContractDeployed.getAddress()
    console.log("Address:" , address)
  });
});
