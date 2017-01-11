from rest_framework import serializers
from .models import LearningRecord, SocialRelationship, Classification, UserClassification

class LearningRecordSerializer(serializers.ModelSerializer):
    """
    Serializing all the Learning Records
    """
    # course_code = serializers.RelatedField(source='code', read_only=True)
    # user = serializers.RelatedField(source='user', read_only=True)
    # parent_user = serializers.RelatedField(source='parent_user', read_only=True)
    # print course_code
    # course_code = unit.code
    # username = user.username
    # parentusername = parent_user.username
    class Meta:
        model = LearningRecord
        fields = ('id', 'unit', 'platform', 'verb', 'user', 'platformid', 'platformparentid', 
                  'parent_user', 'message', 'datetimestamp', 'senttolrs')

class SocialRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializing all the Relationships for Social Network Analysis
    """
    
    # unit = serializers.RelatedField(source='unit', read_only=True)
    # to_user = serializers.RelatedField(source='to_user', read_only=True)
    # from_user = serializers.RelatedField(source='from_user', read_only=True)
    # course_code = unit.code
    # tousername = to_user.username
    # fromusername = from_user.username

    class Meta:
        model = SocialRelationship
        fields = ('id', 'unit', 'platform', 'verb', 'from_user', 'to_user', 'platformid', 'message', 'datetimestamp')


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
