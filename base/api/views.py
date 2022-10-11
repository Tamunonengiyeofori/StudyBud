from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import RoomSerializer
from base.models import Room

 
@api_view(["GET"])
def GetRoutes(request):
    routes = [
        "GET /api",
        "GET /api/rooms",
        "GET /api/rooms/:id"
    ]
    return Response(routes) 

@api_view(["GET"])
def GetRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def GetRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)