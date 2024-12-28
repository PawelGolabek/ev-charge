from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Charger, ChargingSession
from .serializers import UserSerializer, ChargerSerializer, ChargingSessionSerializer

from web3 import Web3
import json
from pathlib import Path


# Get the current script directory
script_dir = Path(__file__).parent.parent

# Path to ABI file, to change in full release
abi_file_path = script_dir.parent  / 'EVCharge' /'blockchain' / 'artifacts' / 'contracts' / 'EVCharge.sol' / 'EVCharge.json'

# Load ABI from the file
with open(abi_file_path, 'r') as abi_file:
    contract_json = json.load(abi_file)
    abi = contract_json['abi']

# Connect to local Ethereum test network
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))   # hardhat 

# Check if the connection is successful
if w3.is_connected():
    print("Connected to Ethereum network")

# Set the deployed contract address and ABI
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
contract = w3.eth.contract(address=contract_address, abi=abi)


class UserCreateView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChargerCreateView(APIView):
    def post(self, request):
        serializer = ChargerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChargingSessionCreateView(APIView):
    def post(self, request):
        serializer = ChargingSessionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            charger = Charger.objects.get(charger_address=data['charger_address'])
            data['total_cost'] = charger.price_per_kwh * data['demand'] 
            data['is_completed'] = False # Default to False as a new session is not completed yet 
            data['charger_owner'] = charger.owner
            # Blockchain transaction
            try:
                tx_hash = contract.functions.validateClient(
                    data['client_address'],
                    data['charger_address'],
                    data['demand']
                ).transact({'from': w3.eth.accounts[0]})
                w3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Save to database
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data, 'tx_hash': tx_hash.hex()}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class ChargerCreateView1(APIView):
    def post(self, request):
        serializer = ChargerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")



def simple_endpoint(request):
    data = {
        "message": "Hello, this is a response from Django!"
    }
    return JsonResponse(data)


def get_transactions(request):

    transactions = ChargingSession.objects.all()
    transactions_list = list(transactions.values())
    return JsonResponse(transactions_list, safe = False)
