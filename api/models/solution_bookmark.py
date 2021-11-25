from django.db import models
from django.db.models import UniqueConstraint

from api.models.solution import Solution
from api.models.user import User


class SolutionBookmark(models.Model):
    """
    Solution Bookmark is for authenticated user bookmark the solution.
    """

    solution = models.ForeignKey(
        Solution, on_delete=models.CASCADE, related_name='bookmarks'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')

    def __str__(self):
        return "{}: {}".format(self.solution, self.user)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['solution', 'user'], name='user_solution_bookmark')
        ]
        verbose_name = 'Solution Bookmark'
        verbose_name_plural = 'Solution Bookmarks'
