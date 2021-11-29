from rest_framework import status

from api.models import Asset, Tag, Organization, Solution, SolutionQuestion
import pytest
from api.documents.tag import TagDocument
from api.documents.asset import AssetDocument

from api.views import solution_questions
from api.views import tag, organization


class TestTestAutocomplete:
    def test_asset_and_tag_autocomplete(
        self,
        authenticated_client,
        example_asset,
        mocker,
        example_asset_tag,
        example_asset_tag2,
    ):
        mocker.patch.object(
            tag,
            '_es_search_asset_and_tag',
            return_value=(Tag.objects.all(), Asset.objects.all()),
        )
        # ?q=mail does not matter in this test because we're mocking elastic search query to return all the objects
        # of assets and tags
        response = authenticated_client.get(
            'http://localhost:8000/autocomplete-tags-and-assets/?q=mail'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['tags'][0] == example_asset_tag.slug
        assert response.json()['tags'][1] == example_asset_tag2.slug
        assert response.json()['assets'][0] == example_asset.name
        assert response.json()['asset_slugs'][0] == example_asset.slug

    def test_autocomplete_organization(
        self, example_asset_customer_organization, mocker, authenticated_client
    ):
        mocker.patch.object(
            organization,
            '_es_search_organizations',
            return_value=Organization.objects.all(),
        )
        response = authenticated_client.get(
            'http://localhost:8000/autocomplete-organizations/?q=primer'
        )
        assert response.status_code == status.HTTP_200_OK
        response_organization = response.json()['results'][0]
        assert response_organization['name'] == example_asset_customer_organization.name
        assert (
            response_organization['website']
            == example_asset_customer_organization.website
        )

    def test_autocomplete_solution_questions(
        self, mocker, authenticated_client, example_solution_question
    ):
        mocker.patch.object(
            solution_questions,
            '_get_solution_questions_db_qs_via_elasticsearch_query',
            return_value=SolutionQuestion.objects.all(),
        )
        response = authenticated_client.get(
            'http://localhost:8000/autocomplete-solution-questions/?q=test&solution__slug=test-solution'
        )
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.json()['results'][0]['solution']
            == example_solution_question.solution.id
        )
        assert response.json()['results'][0]['title'] == 'test solution question'


#
