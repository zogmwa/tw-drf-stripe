from api.models import Asset


class TestAsset:
    def test_create_asset_updates_promo_video_to_embedable_url(self):
        non_embedable_promo_video_link = 'http://www.youtube.com/watch?v=Q0hi9d1W3Ag'
        expected_embedable_link = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        asset = Asset.objects.create(
            slug='mailchimp',
            name='Mailchimp',
            website='https://mailchimp.com/',
            short_description='bla bla',
            description='bla bla bla',
            promo_video=non_embedable_promo_video_link,
        )
        assert asset.promo_video == expected_embedable_link

    def test_addition_of_promo_video_on_existing_asset(self):
        non_embedable_promo_video_link = 'http://www.youtube.com/watch?v=Q0hi9d1W3Ag'
        expected_embedable_link = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        asset = Asset.objects.create(
            slug='mailchimp',
            name='Mailchimp',
            website='https://mailchimp.com/',
            short_description='bla bla',
            description='bla bla bla',
        )
        asset.promo_video = non_embedable_promo_video_link
        asset.save()
        assert asset.promo_video == expected_embedable_link

    def test_addition_of_embedable_promo_video(self):
        embedable_link = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        asset = Asset.objects.create(
            slug='mailchimp',
            name='Mailchimp',
            website='https://mailchimp.com/',
            short_description='bla bla',
            description='bla bla bla',
            promo_video=embedable_link,
        )
        assert asset.promo_video == embedable_link

    def test_addition_of_embedable_promo_video_without_https_prefix(self):
        form_url = 'www.youtube.com/embed/Q0hi9d1W3Ag'
        asset = Asset.objects.create(
            slug='mailchimp',
            name='Mailchimp',
            website='https://mailchimp.com/',
            short_description='bla bla',
            description='bla bla bla',
            promo_video=form_url,
        )

        expected_embed_url = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        assert asset.promo_video == expected_embed_url

    def test_https_prefix_is_added_for_non_https_urls(self):
        form_url = 'http://www.youtube.com/embed/Q0hi9d1W3Ag'
        asset = Asset.objects.create(
            slug='mailchimp',
            name='Mailchimp',
            website='https://mailchimp.com/',
            short_description='bla bla',
            description='bla bla bla',
            promo_video=form_url,
        )

        expected_embed_url = 'https://www.youtube.com/embed/Q0hi9d1W3Ag'
        assert asset.promo_video == expected_embed_url
