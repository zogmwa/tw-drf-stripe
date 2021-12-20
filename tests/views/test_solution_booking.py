from api.models.solution_booking import SolutionBooking

SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solution_bookings/'


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

        response = authenticated_client.get(SOLUTIONS_BASE_ENDPOINT)

        assert response.status_code == 200
        assert response.data[0]['solution']['id'] == example_solution.id
        assert response.data[0]['booked_by'] == user_and_password[0].id
