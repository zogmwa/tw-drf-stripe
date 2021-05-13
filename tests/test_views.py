from api.models import Tag, Asset
from api.views import AssetViewSet


class TestAssetViewSet:
    def test__filter_desired_tags(self):
        email_marketing_tag_slug = 'email-marketing'
        aws_ses_tag_slug = 'ses'
        asset_makemymails = Asset.objects.create(name='MakeMyMails')
        asset_mailchimp = Asset.objects.create(name='MailChimp')

        email_marketing_tag = Tag(slug=email_marketing_tag_slug, name='Email Marketing')
        aws_ses_tag = Tag(slug=aws_ses_tag_slug, name='ses')
        Tag.objects.bulk_create([email_marketing_tag, aws_ses_tag])
        asset_makemymails.tags.set([email_marketing_tag, aws_ses_tag])
        asset_mailchimp.tags.set([email_marketing_tag])

        assets = AssetViewSet._filter_assets_matching_tags([email_marketing_tag_slug, aws_ses_tag_slug])
        assert assets.get().name == asset_makemymails.name
