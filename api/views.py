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
    
    elif request.method == 'POST':
        # Expecting mixed data: custom_id, gmail, key, message, image
        data = request.data.copy()
        
        # 1. Handle UserEntry (Get or Create)
        custom_id = data.get('custom_id')
        gmail = data.get('gmail')
        
        if not custom_id or len(custom_id) != 10:
             return Response({'error': 'custom_id is required and must be 10 chars'}, status=status.HTTP_400_BAD_REQUEST)

        user_entry, created = UserEntry.objects.get_or_create(
            custom_id=custom_id,
            defaults={'gmail': gmail}
        )
        
        if not created and gmail and user_entry.gmail != gmail:
            # Update gmail if provided and different? Or just ignore?
            # Let's update it for now to keep it fresh
            user_entry.gmail = gmail
            user_entry.save()

        # 2. Handle EntryData
        key = data.get('key')
        if not key or len(key) > 15:
             return Response({'error': 'key is required and must be max 15 chars'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if key already exists for this user
        if EntryData.objects.filter(user_entry=user_entry, key=key).exists():
             return Response({'error': f'Key {key} already exists for this ID'}, status=status.HTTP_400_BAD_REQUEST)

        entry_data = EntryData.objects.create(
            user_entry=user_entry,
            key=key,
            message=data.get('message'),
            image=data.get('image')
        )
        
        # Serialize response to look somewhat like before (combined)
        return Response({
            'custom_id': user_entry.custom_id,
            'gmail': user_entry.gmail,
            'key': entry_data.key,
            'message': entry_data.message,
            'image': entry_data.image.url if entry_data.image else None
        }, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def data_entry_message(request, custom_id, key):
    return handle_data_entry(request, custom_id, key, field_type='message')

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
@parser_classes([MultiPartParser, FormParser])
def data_entry_photo(request, custom_id, key):
    return handle_data_entry(request, custom_id, key, field_type='image')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register_gmail(request, custom_id, gmail):
    if len(custom_id) != 10:
        return Response({'error': 'ID must be 10 characters'}, status=status.HTTP_400_BAD_REQUEST)
    
    user_entry, created = UserEntry.objects.get_or_create(
        custom_id=custom_id,
        defaults={'gmail': gmail}
    )
    
    if not created:
        if user_entry.gmail != gmail:
            user_entry.gmail = gmail
            user_entry.save()
            return Response({'status': 'updated user email', 'custom_id': custom_id})
        return Response({'status': 'user already exists', 'custom_id': custom_id})
        
    return Response({'status': 'user registered', 'custom_id': custom_id}, status=status.HTTP_201_CREATED)

def handle_data_entry(request, custom_id, key, field_type):
    try:
        user_entry = UserEntry.objects.get(custom_id=custom_id)
        entry_data = EntryData.objects.get(user_entry=user_entry, key=key)
    except (UserEntry.DoesNotExist, EntryData.DoesNotExist):
        return Response({'error': 'Data entry not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Key validation is implicit now because we looked up BY KEY.
    # If the key was wrong for this user, EntryData.get(...) would fail or find nothing.
    # Wait, the prompt implies "one id can have different keys".
    # So looking up by (user_entry, key) IS the validation.
    
    if request.method == 'POST':
        if field_type == 'message' and 'message' in request.data:
            entry_data.message = request.data['message']
            entry_data.save()
            return Response({'status': 'updated message', 'custom_id': user_entry.custom_id, 'key': entry_data.key})
        
        elif field_type == 'image' and 'image' in request.data:
            entry_data.image = request.data['image']
            entry_data.save()
            return Response({'status': 'updated photo', 'custom_id': user_entry.custom_id, 'key': entry_data.key})
            
        return Response({'status': 'no changes made', 'detail': f'expected field {field_type}'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        data = {}
        if field_type == 'message':
            if entry_data.message:
                data['message'] = entry_data.message
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
