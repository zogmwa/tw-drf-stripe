from api.models import Tag, Asset
from api.views.asset import AssetViewSet


class TestAssetViewSet:
    def test__filter_desired_tags(self):
        email_marketing_tag_slug = 'email-marketing'
        aws_ses_tag_slug = 'ses'
        asset_makemymails = Asset.objects.create(
            slug='make_my_mails', name='MakeMyMails'
        )
        asset_mailchimp = Asset.objects.create(slug='mailchimp', name='MailChimp')

        email_marketing_tag = Tag.objects.create(
            slug=email_marketing_tag_slug, name='Email Marketing'
        )
        aws_ses_tag = Tag.objects.create(slug=aws_ses_tag_slug, name='ses')
        email_marketing_tag.save()

        asset_makemymails.tags.set([email_marketing_tag, aws_ses_tag])
        asset_mailchimp.tags.set([email_marketing_tag])

        assets = AssetViewSet._filter_assets_matching_tags_exact(
            [email_marketing_tag_slug, aws_ses_tag_slug]
        )
        assert assets.get().name == asset_makemymails.name
