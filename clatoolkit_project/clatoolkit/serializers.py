from rest_framework import serializers
from .models import LearningRecord, SocialRelationship, Classification, UserClassification

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

class ClassificationSerializer(serializers.ModelSerializer):
    """
    Serializing all the Machine Learning Classifications eg CoI
    """
    class Meta:
        model = Classification
        fields = ('id', 'xapistatement', 'classification', 'classifier')

class UserClassificationSerializer(serializers.ModelSerializer):
    """
    Serializing all the User Reclassifications for the Machine Learning Classifications
    """
    class Meta:
        model = UserClassification
        fields = ('id', 'classification', 'username', 'isclassificationcorrect', 'userreclassification', 'trained', 'feedback', 'feature')
