from django.db.models.signals import post_save, pre_save
from django.core.signals import request_finished

from api.models import Solution
from api.models.solution_booking import SolutionBooking
from api.views.solutions import SolutionViewSet

SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solutions/'


def patch_elasticsearch(mocker):
    mocker.patch.object(
        SolutionViewSet,
        '_get_solutions_db_qs_via_elasticsearch_query',
        return_value=Solution.objects.all(),
    )


class TestFetchingSolution:
    def test_anonymous_user_should_be_able_to_fetch_solution_with_search_query(
        self, unauthenticated_client, example_solution, mocker
    ):
        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )

        solution_list_url = '{}?q={}'.format(SOLUTIONS_BASE_ENDPOINT, 'Test')
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == example_solution.title

    def test_anonymous_user_should_be_able_to_fetch_filtered_solution_with_search_query(
        self, unauthenticated_client, example_solution, mocker
    ):
        added_example_solution = Solution.objects.create(
            slug='test-solution2',
            title='Test Solution2',
            type='I',
            has_free_consultation=True,
            description='bla bla bla',
            scope_of_work='bla bla bla',
        )

        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )

        solution_list_url = '{}?q={}&has_free_consultation={}'.format(
            SOLUTIONS_BASE_ENDPOINT, 'Test', 'true'
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == added_example_solution.title

    def test_anonymous_user_should_be_able_to_fetch_ordered_solution_with_search_query(
        self, unauthenticated_client, example_solution, mocker
    ):
        added_example_solution = Solution.objects.create(
            slug='test-solution2',
            title='Test Solution2',
            type='I',
            upvotes_count='2',
            description='bla bla bla',
            scope_of_work='bla bla bla',
        )

        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )

        solution_list_url = '{}?q={}&ordering={}'.format(
            SOLUTIONS_BASE_ENDPOINT, 'Test', 'upvotes_count'
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['count'] == 2
        assert response.data['results'][0]['title'] == example_solution.title
        assert response.data['results'][1]['title'] == added_example_solution.title

    def test_anonymous_user_should_be_able_to_get_solution_booked_count(
        self,
        authenticated_client,
        unauthenticated_client,
        example_solution,
        user_and_password,
    ):
        SolutionBooking.objects.create(
            solution=example_solution,
            stripe_session_id="zQds2Urgd",
            price_at_booking=10,
            booked_by=user_and_password[0],
            manager=user_and_password[0],
            status='Pending',
        )

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['booked_count'] == 1

    def test_returned_bookings_pending_fulfillment_count_with_solution(
        self,
        authenticated_client,
        unauthenticated_client,
        example_solution,
        user_and_password,
    ):
        # When user booking the solution.
        solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            stripe_session_id="zQds2Urgd",
            price_at_booking=10,
            booked_by=user_and_password[0],
            manager=user_and_password[0],
            status='Pending',
        )
        solution_booking.save()

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 1

        # When user solution booking status has changed to 'In Progress'.
        solution_booking.status = 'In Progress'
        solution_booking.save()

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 1

        # When user solution booking status has changed to 'In Review'.
        solution_booking.status = 'In Review'
        solution_booking.save()

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 1

        # When user solution booking status has changed to 'Complete'.
        solution_booking.status = 'Completed'
        solution_booking.save()

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 0

    def test_returned_point_of_contact_user_in_solution(
        self,
        authenticated_client,
        unauthenticated_client,
        example_solution,
        user_and_password,
    ):
        example_solution.point_of_contact = user_and_password[0]
        example_solution.save()

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['point_of_contact']['id'] == user_and_password[0].id
        assert (
            response.data['point_of_contact']['username']
            == user_and_password[0].username
        )

        response = authenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['point_of_contact']['id'] == user_and_password[0].id
        assert (
            response.data['point_of_contact']['username']
            == user_and_password[0].username
        )

    def test_user_should_not_be_able_to_fetch_solution_that_its_is_searchable_is_false(
        self, unauthenticated_client, example_solution, mocker
    ):
        Solution.objects.create(
            slug='test-solution2',
            title='Test Solution2',
            type='I',
            description='bla bla bla',
            scope_of_work='bla bla bla',
            is_searchable=False,
        )

        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.filter(is_searchable=True),
        )

        solution_list_url = '{}?q={}'.format(
            SOLUTIONS_BASE_ENDPOINT,
            'Test',
        )
        response = unauthenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == example_solution.title


class TestSolutionDetailSolutionBooking:
    def test_more_than_1_solution_booking_is_done_by_user_last_solution_booking_should_be_shown(
        self,
        example_solution,
        example_solution_booking,
        example_solution_booking2,
        admin_client,
    ):
        example_solution_booking2.provider_notes = '2nd solution_booking'
        example_solution_booking2.save()

        solution_detail_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = admin_client.get(solution_detail_url)
        assert len(response.data['last_solution_booking']) == 1
        assert (
            response.data['last_solution_booking'][0]['provider_notes']
            == example_solution_booking2.provider_notes
        )

        '''
        The reason to update this field is to change the update time of the 1st solution booking. This is to check that 
        the solution_booking instance which was updated last should be shown in the last_solution_booking on a solution detail page
        '''
        example_solution_booking = SolutionBooking.objects.get(
            id=example_solution_booking.id
        )
        example_solution_booking.provider_notes = '1st solution_booking'
        example_solution_booking.save()
        response = admin_client.get(solution_detail_url)
        assert (
            response.data['last_solution_booking'][0]['provider_notes']
            == example_solution_booking.provider_notes
        )

    def test_if_no_solution_booking_is_done_by_user_last_solution_booking_should_be_empty(
        self, example_solution, admin_client
    ):
        solution_detail_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = admin_client.get(solution_detail_url)
        assert len(response.data['last_solution_booking']) == 0
