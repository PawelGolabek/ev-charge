# Setup Guide

## Python and Libraries
py -m pip install --upgrade pip  
py -3.10 -m pip install regex==2024.9.11 pycryptodome==3.20.  
pip install web3 flask flask-cors django djangorestframework markdown django-filter django-cors-headers djangorestframework-simplejwt  

## Node.js and Angular
npm install -g @angular/cli  
npm i solidity-coverage ethers @typechain/ethers-v6 @metamask/sdk @synthetixio/synpress@latest  

## Create an Angular Project
ng new evcharge  
cd evcharge  
Copy frontend files to the new project.  

## Run the Application  

### Backend – Hardhat  
cd blockchain  
npx hardhat node  
npx hardhat run deploy.js --network localhost  

### Frontend – Angular  
cd frontend/evcharge  
ng serve  

### Backend – Django  
cd djbackend  
env\Scripts\activate  
cd EVCharge  
py manage.py runserver  

## Testing Smart Contract with Chai  
cd blockchain/EVCharge  
npx hardhat test  

### Recommended:  
- Microsoft Visual C++ 14.0+  
