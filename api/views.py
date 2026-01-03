import re
from rest_framework.decorators import api_view, parser_classes, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import UserEntry, EntryData
from .serializers import UserEntrySerializer, EntryDataSerializer

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
@parser_classes([MultiPartParser, FormParser])
def data_entry_list_create(request):
    if request.method == 'GET':
        queryset = UserEntry.objects.all()
        # For list, we might just show users, or maybe we want to show all data?
        # Let's show users for now as that's the primary resource.
        serializer = UserEntrySerializer(queryset, many=True)
        return Response(serializer.data)
    

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def data_entry_message(request, custom_id, key, algoId):
    return handle_data_entry(request, custom_id, key, field_type='message', algoId=algoId)

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
@parser_classes([MultiPartParser, FormParser])
def data_entry_photo(request, custom_id, key):
    return handle_data_entry(request, custom_id, key, field_type='image')
def isGmail(email):
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@(gmail|email|yahoo)\.com$", email))

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register_gmail(request, custom_id, gmail):
    if len(custom_id) != 10:
        return Response({'error': 'ID must be 10 characters'}, status=status.HTTP_400_BAD_REQUEST)
    if not isGmail(gmail):
        return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
    user_entry, created = UserEntry.objects.get_or_create(
        custom_id=custom_id,
        defaults={'gmail': gmail}
    )
    
    if not created and user_entry.gmail != gmail:
        user_entry.gmail = gmail
        user_entry.save()

    if not EntryData.objects.filter(user_entry=user_entry).exists():
        EntryData.objects.create(user_entry=user_entry)
        data_status = 'created_empty'
    else:
        data_status = 'exists'

    return Response({
        'status': 'user registered' if created else 'user updated', 
        'custom_id': custom_id,
        'data_status': data_status
    }, status=status.HTTP_201_CREATED)

def handle_data_entry(request, custom_id, key, field_type , algoId = ''):
    if request.method == 'POST':
        retMes = 'updated'
        try:
            user_entry = UserEntry.objects.get(custom_id=custom_id)
            try:
                entry_data = EntryData.objects.get(user_entry=user_entry, key=key)
            except EntryData.DoesNotExist:
                entry_data = EntryData.objects.create(user_entry=user_entry, key=key)
                retMes = 'created'
                
        except UserEntry.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if field_type == 'message' and 'message' in request.data:
            entry_data.message = request.data['message']
            entry_data.algoId = algoId
            entry_data.save()
            return Response({'status': retMes+' message', 'custom_id': user_entry.custom_id, 'key': entry_data.key , 'algoId': entry_data.algoId})
        
        elif field_type == 'image' and 'image' in request.data:
            entry_data.image = request.data['image']
            entry_data.save()
            return Response({'status': retMes+' photo', 'custom_id': user_entry.custom_id, 'key': entry_data.key})
            
        return Response({'status': 'no changes made', 'detail': f'expected field {field_type}'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        try:
            user_entry = UserEntry.objects.get(custom_id=custom_id)
            entry_data = EntryData.objects.get(user_entry=user_entry, key=key)
        except (UserEntry.DoesNotExist, EntryData.DoesNotExist):
            return Response({'error': 'Data entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = {}
        if field_type == 'message':
            if entry_data.message:
                data['message'] = entry_data.message
                data['algoId'] = entry_data.algoId
            else:
                return Response({'error': 'No message found'}, status=status.HTTP_404_NOT_FOUND)
        
        elif field_type == 'image':
            if entry_data.image:
                try:
                    data['image'] = request.build_absolute_uri(entry_data.image.url)
                except ValueError:
                    pass
            else:
                 return Response({'error': 'No image found'}, status=status.HTTP_404_NOT_FOUND)
                 
        return Response(data)
