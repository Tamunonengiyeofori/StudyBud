from rest_framework.serializers import ModelSerializer
from base.models import Room 

# create a room serializer to serialize all the data from the room object.
class RoomSerializer(ModelSerializer):
    class Meta:
        # point to the particular model object to be serialzed
        model = Room
        # specify all the fields to be serialized in the model
        fields = "__all__"
        
        