from rest_framework.serializers import ModelSerializer

from api.models.asset_snapshot import AssetSnapshot


class AssetSnapshotSerializer(ModelSerializer):
    class Meta:
        model = AssetSnapshot
        fields = ['asset', 'url']
