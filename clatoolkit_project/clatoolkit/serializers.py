from rest_framework import serializers
from .models import LearningRecord, SocialRelationship

class LearningRecordSerializer(serializers.ModelSerializer):
    """
    Serializing all the Learning Records
    """
    class Meta:
        model = LearningRecord
        fields = ('id', 'course_code', 'platform', 'verb', 'username', 'platformid', 'platformparentid', 'parentusername', 'message', 'datetimestamp', 'senttolrs')

class SocialRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializing all the Relationships for Social Network Analysis
    """
    class Meta:
        model = SocialRelationship
        fields = ('id', 'course_code', 'platform', 'verb', 'fromusername', 'tousername', 'platformid', 'message', 'datetimestamp')
