from api.models.solution_booking import Solution, SolutionBooking

from django.core import mail
from api.views.solutions import SolutionViewSet

SOLUTIONBOOKINGS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solution_bookings/'
SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solutions/'
FETCH_SOLUTION_BOOKING_URL = 'http://127.0.0.1:8000/users/bookings/'


class TestFetchingSolutionBooking:
    def test_authenticated_user_should_be_fetching_solution_bookings_list(
        self, authenticated_client, example_solution, user_and_password
    ):
        solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
            manager=user_and_password[0],
            status='Pending',
        )
        solution_booking.save()

        response = authenticated_client.get(SOLUTIONBOOKINGS_BASE_ENDPOINT)

        assert response.status_code == 200
        assert response.data['results'][0]['solution']['id'] == example_solution.id
        assert (
            response.data['results'][0]['booked_by']['username']
            == user_and_password[0].username
        )


class TestDeletingSolutionBooking:
    def test_decrease_pending_solution_booking_fulfillment_count_of_solution(
        self, mocker, authenticated_client, example_solution, user_and_password
    ):
        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
            status=SolutionBooking.Status.PENDING,
        )
        example_solution_booking.save()

        example_solution_booking.delete()
        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 0


class TestChangeStatus:
    def test_creating_started_at_field_when_status_from_pending_to_others(
        self,
        admin_user,
        user_and_password,
        example_solution,
    ):
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
        )
        example_solution_booking.status = SolutionBooking.Status.IN_PROGRESS
        example_solution_booking.save()

        contract_instance = SolutionBooking.objects.get(id=example_solution_booking.id)

        assert contract_instance.started_at is not None

    def test_increase_capacity_used_field_when_payment_checkout(
        self,
        mocker,
        authenticated_client,
        user_and_password,
        example_solution,
    ):
        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )

        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
        )

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['capacity_used'] == 0

        example_solution_booking.is_payment_completed = True
        example_solution_booking.save()

        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['capacity_used'] == 1


class TestFetchSolutionBookings:
    def test_anonymous_user_could_not_fetch_solution_bookings(
        self, example_solution, unauthenticated_client, user_and_password
    ):
        SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
        )
        response = unauthenticated_client.get(FETCH_SOLUTION_BOOKING_URL)

        assert response.status_code == 401

    def test_authenticated_user_should_fetch_solution_bookings(
        self, example_solution, authenticated_client, user_and_password
    ):
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
        )
        response = authenticated_client.get(FETCH_SOLUTION_BOOKING_URL)

        assert response.status_code == 200
        assert response.data['results'][0]['id'] == example_solution_booking.id
        assert response.data['results'][0]['solution']['id'] == example_solution.id

        fetch_solution_booking_url = '{}?id={}'.format(
            FETCH_SOLUTION_BOOKING_URL, example_solution_booking.id
        )
        response = authenticated_client.get(fetch_solution_booking_url)

        assert response.status_code == 200
        assert response.data['results'][0]['id'] == example_solution_booking.id
        assert response.data['results'][0]['solution']['id'] == example_solution.id

    def test_authenticated_user_could_update_rating(
        self, example_solution, authenticated_client, user_and_password
    ):
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
        )

        patch_solution_booking_url = '{}{}/'.format(
            SOLUTIONBOOKINGS_BASE_ENDPOINT, example_solution_booking.id
        )
        response = authenticated_client.patch(
            patch_solution_booking_url, {'rating': 1}, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.data['id'] == example_solution_booking.id
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['solution']['avg_rating'] == 1

        response = authenticated_client.patch(
            patch_solution_booking_url, {'rating': -1}, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.data['id'] == example_solution_booking.id
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['solution']['avg_rating'] == -1

        response = authenticated_client.patch(
            patch_solution_booking_url, {'rating': 0}, content_type='application/json'
        )

        assert response.status_code == 200
        assert response.data['id'] == example_solution_booking.id
        assert response.data['solution']['id'] == example_solution.id
        assert response.data['solution']['avg_rating'] == 0
