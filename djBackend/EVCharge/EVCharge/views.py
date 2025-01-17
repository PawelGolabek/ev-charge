from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Role, User, Charger, ChargingSession, TransactionSummary
from .serializers import UserSerializer, ChargerSerializer, ChargingSessionSerializer
from django.contrib.auth import authenticate
from .tokens import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from web3 import Web3
import json
from pathlib import Path
from django.db.models import Sum, F
from django.db.models import Q
from eth_utils import to_bytes, is_address

from eth_account.messages import encode_defunct
from eth_utils import keccak
from django.db.models import Max, Min
from datetime import datetime, timedelta


############################ Web3 stuff #####################################
# Get the current script directory
script_dir = Path(__file__).parent.parent.parent

# Path to ABI file, to change in full release
abi_file_path = script_dir.parent /'blockchain2' / 'artifacts' / 'contracts' / 'EVCharge.sol' / 'EVCharge.json'

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

server_public_key = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
server_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
#########################################################################



class LoginView(APIView):
    def post(self, request):
        user_address = request.data.get('user_address')
        password = request.data.get('password')
        user = authenticate(user_address=user_address, password=password)
        if user:
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)
        return Response({"error": "Niepoprawny adres lub hasło"}, status=status.HTTP_401_UNAUTHORIZED)


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
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_address = decoded_token.get('user_address')
        user_role = decoded_token.get('role')

        charger_address = request.data.get('charger_address')
        demand = request.data.get('demand')
        date = request.data.get('date', None)
        clientSignature = request.data.get('signature')
        print(clientSignature)
        clientHash = request.data.get('hash', None)
        clientSignature =  Web3.to_bytes(hexstr=clientSignature)
        
        if not charger_address or demand is None:
            return Response({
                'status': 'error',
                'message': 'Błąd: nie wypełniono wszystkich wymaganych pól.'
            }, status=status.HTTP_400_BAD_REQUEST)

        client = get_object_or_404(User, user_address=user_address)
        charger = get_object_or_404(Charger, charger_address=charger_address)
        total_cost = charger.price_per_kwh * demand
        is_completed = False
        data=request.data
        charger = Charger.objects.get(charger_address=data['charger_address'])
        data['client_address'] = client.pk
        data['total_cost'] = charger.price_per_kwh * data['demand'] 
        data['is_completed'] = False 
        data['charger_owner'] = charger.owner.pk
        data['charger_address'] = charger.pk
        serializer = ChargingSessionSerializer(data=data)
        if serializer.is_valid():
            data = serializer.validated_data
            # Blockchain transaction
            demand = int(demand)
            try:
                tx_hash = contract.functions.validateClient(
                    client.user_address,
                    charger_address,
                    demand,
                    clientHash,
                    clientSignature
                ).transact({'from': w3.eth.accounts[0]})
                w3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Save to database
            data['client_address'] = client
            data['charger_address'] = get_object_or_404(Charger, charger_address=charger_address)
            serializer.save()
            client.nonce += 1
            return Response({'status': 'success', 'data': serializer.data, 'tx_hash': tx_hash.hex()}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        admin_role = decoded_token.get('role')

        if admin_role != "Admin":
            return Response({
                'status': 'error',
                'message': 'Only admin can add users.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get user data from the request
        valid_roles = ["None", "Admin", "Seller", "Client"]
        user_address = request.data.get('user_address')
        try:
            roleUser = request.data.get('role')
            if roleUser not in valid_roles:
                return Response({
                    'status': 'error',
                    'message': f'Invalid role. Valid roles are: {", ".join(valid_roles)}.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the corresponding Role instance from the database
            role = Role.objects.get(name=roleUser)
        except Role.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Role not found in the database.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already exists
        if User.objects.filter(user_address=user_address).exists():
            return Response({
                'status': 'error',
                'message': 'User already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Blockchain interaction to add the user
        try:
            tx_hash = contract.functions.addUser(
                Web3.to_checksum_address(user_address),
                role.id-1,  # Mismatched id on db and bc
            ).transact({'from': Web3.to_checksum_address(server_public_key)})
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # Check if the transaction was successful
            if receipt['status'] != 1:
                return Response({
                    'status': 'error',
                    'message': 'Blockchain transaction failed.'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the user to the database only if the blockchain transaction succeeds
        user = User(
            user_address=user_address,
            role=role,  # Assign the Role instance
            balance=0,
            contribution=0
        )
        user.save()

        return Response({
            'status': 'success',
            'message': 'User added successfully.',
            'tx_hash': tx_hash.hex()
        }, status=status.HTTP_201_CREATED)

class CheckContributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract the JWT token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                'status': 'error',
                'message': 'Authorization header missing.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        role = decoded_token.get('role')
        user_address = decoded_token.get('user_address')  # Assuming user_address is included in the token

        # Ensure the user is a seller
        if role != "Seller":
            return Response({
                'status': 'error',
                'message': 'Only sellers can check their contributions.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Verify user existence in the database
        try:
            user = User.objects.get(user_address=user_address)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found in the database.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Retrieve contribution from the database
        db_contribution = user.contribution

        # Retrieve contribution from the blockchain
        try:
            blockchain_contribution = contract.functions.checkMyContribution().call({
                'from': Web3.to_checksum_address(user_address)
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to fetch contribution from the blockchain: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': 'success',
            'data': {
                'database_contribution': db_contribution,
                'blockchain_contribution': blockchain_contribution
            }
        }, status=status.HTTP_200_OK)



def simple_endpoint(request):
    data = {
        "message": "Hello, this is a response from Django!"
    }
    return JsonResponse(data)




class GetTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        # Decode the token to get user information
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_address = decoded_token.get('user_address')
        user_role = decoded_token.get('role')

        # Filter transactions based on the user address
        transactions = ChargingSession.objects.filter(client_address__user_address=user_address).select_related('client_address', 'charger_address', 'charger_owner').all()

        transactions_list = [
            {
                "transaction_id": transaction.id,
                "client_address": transaction.client_address.user_address,
                "charger_address": transaction.charger_address.charger_address,
                "total_cost": transaction.total_cost,
                "demand": transaction.demand,
                "is_completed": transaction.is_completed,
                "charger_owner": transaction.charger_owner.user_address,
                "date": transaction.date.isoformat(),
            }
            for transaction in transactions
        ]

        return JsonResponse(transactions_list, safe=False)

class CheckMyBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_address = decoded_token.get('user_address')

        try:
            balance = contract.functions.checkMyBalance().call({'from': user_address})
            return JsonResponse({'balance': balance})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class IncreaseBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_address = decoded_token.get('user_address')

        amount = request.data.get('amount')

        try:
            tx_hash = contract.functions.increaseBalance().transact({'from': user_address, 'value': amount})
            w3.eth.wait_for_transaction_receipt(tx_hash)
            return JsonResponse({'status': 'success', 'tx_hash': tx_hash.hex()})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class GenerateTransactionSummaryView(APIView):
    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"status": "error", "message": "Niepoprawny zakres dat. Użyj: YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if an existing summary overlaps with the date range
        overlapping_summaries = TransactionSummary.objects.filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        )
        if overlapping_summaries.exists():
            return Response({"status": "error", "message": "Istnieje już podsumowanie dla tego zakresu dat"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all charging sessions within the date range
        sessions = ChargingSession.objects.filter(date__range=[start_date, end_date])

        # Group by charger owner (seller) and calculate the total demand and total cost for each charger owner
        charger_summaries = sessions.values('charger_owner').annotate(
            total_demand=Sum('demand'),
            total_amount_owed=Sum(F('demand') * F('charger_address__price_per_kwh'))  # Correct calculation for total amount
        )
        
        # Create transaction summaries for each charger owner (seller)
        for summary in charger_summaries:
            seller = User.objects.get(id=summary['charger_owner'])
            chargers = Charger.objects.filter(owner=seller)
            for charger in chargers:
                TransactionSummary.objects.create(
                    seller=seller,
                    charger=charger,
                    total_demand=summary['total_demand'],
                    total_amount_owed=summary['total_amount_owed'],
                    start_date=start_date,
                    end_date=end_date
                )

        return Response({"status": "success", "message": "Pomyślnie wygenerowano podsumowanie."}, status=status.HTTP_201_CREATED)


class GetDateRangeView(APIView):
    def get(self, request):
        # Get the newest date with a summary
        latest_date_with_summary = TransactionSummary.objects.aggregate(latest_date=Max('end_date'))['latest_date']
        
        # If no summaries exist, assume the oldest date from ChargingSession
        if latest_date_with_summary:
            newest_date_without_summary = latest_date_with_summary + timedelta(days=1)
        else:
            # Pick the date of the first-ever charging session
            oldest_date = ChargingSession.objects.aggregate(oldest_date=Min('date'))['oldest_date']
            if oldest_date:
                newest_date_without_summary = oldest_date.date()
            else:
                return Response(
                    {"error": "Brak sesji ładowania do stworzenia podsumowania."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get yesterday's date
        yesterday_date = (datetime.now() - timedelta(days=1)).date()
        print(newest_date_without_summary)
        print(yesterday_date)
        # Ensure the date range makes sense
        if newest_date_without_summary > yesterday_date:
            newest_date_without_summary = yesterday_date


        return Response(
            {
                "newest_date_without_summary": newest_date_without_summary,
                "yesterday_date": yesterday_date
            },
            status=status.HTTP_200_OK
        )


class RetrieveTransactionSummaryView(APIView):
    def get(self, request):
        summaries = TransactionSummary.objects.all()
        
        # Serialize summaries into a structured JSON format
        data = []
        for summary in summaries:
            data.append({
                "id": summary.id,
                "seller": {
                    "user_address": summary.seller.user_address,
                    "role": summary.seller.role.name,
                    "balance": summary.seller.balance,
                    "contribution": summary.seller.contribution,
                },
                "charger": {
                    "charger_address": summary.charger.charger_address,
                    "price_per_kwh": summary.charger.price_per_kwh,
                },
                "total_demand": float(summary.total_demand),
                "total_amount_owed": float(summary.total_amount_owed),
                "start_date": summary.start_date.strftime('%Y-%m-%d'),
                "end_date": summary.end_date.strftime('%Y-%m-%d'),
                "created_at": summary.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "paid": summary.paid
            })

        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

class paySellerView(APIView):
    def post(self, request):
        #auth check if admmin
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_role = decoded_token.get('role')
        if(user_role != 'Admin'):
            return Response({"status": "unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        summary = TransactionSummary.objects.get(id=request.data)
        sender_address = server_public_key
        recipient_address = summary.seller

        # Check recipient's balance before the transaction
        recipient_balance_before = w3.eth.get_balance(recipient_address.user_address)
        total_amount_owed = int(summary.total_amount_owed)

        # Transaction details
        tx = {
            "nonce": w3.eth.get_transaction_count(sender_address),
            "to": to_bytes(hexstr=recipient_address.user_address),
            "value": total_amount_owed,
            "gas": 21000,
            "gasPrice": w3.to_wei(50, "gwei"),
        }

        # Sign the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, server_private_key)

        # Send the transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Check recipient's balance after the transaction
        recipient_balance_after = w3.eth.get_balance(recipient_address.user_address)

        print(f"Transaction successful with hash: {tx_hash.hex()}")
        print(f"Recipient's balance before transaction: {recipient_balance_before}")
        print(f"Recipient's balance after transaction: {recipient_balance_after}")

        # Get transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        receipt_hash = receipt['transactionHash'].hex()

        summary.paid = True
        summary.save()
        print(f"Transaction successful with hash: {tx_hash.hex()}")
        return Response({"status": "success", "data":  receipt_hash}, status=status.HTTP_200_OK)
    


class AddChargerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract the JWT token and decode it
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                'status': 'error',
                'message': 'Authorization header missing.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        role = decoded_token.get('role')
        user_address = decoded_token.get('user_address')  # Assuming `user_address` is in the token

        # Ensure the user is a seller
        if role != "Seller":
            return Response({
                'status': 'error',
                'message': 'Only sellers can add chargers.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get data from the request
        charger_address = request.data.get('charger_address')
        price_per_kwh = request.data.get('price_per_kwh')

        if not charger_address or not price_per_kwh:
            return Response({
                'status': 'error',
                'message': 'Both charger_address and price_per_kwh are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if charger already exists
        if Charger.objects.filter(charger_address=charger_address).exists():
            return Response({
                'status': 'error',
                'message': 'Charger already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Interact with the blockchain
        try:
            tx_hash = contract.functions.addCharger(
                Web3.to_checksum_address(charger_address),
                int(price_per_kwh)
            ).transact({'from': Web3.to_checksum_address(user_address)})
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt['status'] != 1:
                return Response({
                    'status': 'error',
                    'message': 'Blockchain transaction failed.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to add charger on blockchain: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save to the database
        owner = User.objects.get(user_address=user_address)
        charger = Charger(
            charger_address=charger_address,
            price_per_kwh=price_per_kwh,
            owner=owner
        )
        charger.save()

        return Response({
            'status': 'success',
            'message': 'Charger added successfully.',
            'tx_hash': tx_hash.hex()
        }, status=status.HTTP_201_CREATED)




class UpdateChargerPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract the JWT token and decode it
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({
                'status': 'error',
                'message': 'Authorization header missing.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        role = decoded_token.get('role')
        user_address = decoded_token.get('user_address')  # Assuming `user_address` is in the token

        # Ensure the user is a seller
        if role != "Seller":
            return Response({
                'status': 'error',
                'message': 'Only sellers can update charger prices.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get data from the request
        charger_address = request.data.get('charger_address')
        new_price_per_kwh = request.data.get('price_per_kwh')

        if not charger_address or new_price_per_kwh is None:
            return Response({
                'status': 'error',
                'message': 'Both charger_address and new_price_per_kwh are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify the charger exists and is owned by the user
        try:
            charger = Charger.objects.get(charger_address=charger_address, owner__user_address=user_address)
        except Charger.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Charger not found or you do not own this charger.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Interact with the blockchain
        try:
            tx_hash = contract.functions.updateChargerPrice(
                Web3.to_checksum_address(charger_address),
                int(new_price_per_kwh)
            ).transact({'from': Web3.to_checksum_address(user_address)})
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt['status'] != 1:
                return Response({
                    'status': 'error',
                    'message': 'Blockchain transaction failed.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to update price on blockchain: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update in the database
        charger.price_per_kwh = new_price_per_kwh
        charger.save()

        return Response({
            'status': 'success',
            'message': 'Charger price updated successfully.',
            'tx_hash': tx_hash.hex()
        }, status=status.HTTP_200_OK)


class ListMyChargersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extract and decode the token to get the seller's role and address
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_address = decoded_token.get('user_address')
        user_role = decoded_token.get('role')

        # Verify that the user is a seller
        if user_role != "Seller":
            return Response({
                "status": "error",
                "message": "Only sellers can view their chargers."
            }, status=403)

        # Query the chargers owned by this seller
        chargers = Charger.objects.filter(owner__user_address=user_address)
        charger_list = []

        for charger in chargers:
            charger_list.append({
                "charger_address": charger.charger_address,
                "price_per_kwh": charger.price_per_kwh
            })

        return Response({
            "status": "success",
            "data": charger_list
        }, status=200)