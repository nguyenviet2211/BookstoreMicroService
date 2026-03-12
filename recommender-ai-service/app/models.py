from django.db import models


class Recommendation(models.Model):
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    score = models.FloatField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer_id', 'book_id')
        ordering = ['-score']

    def __str__(self):
        return f"Recommend Book {self.book_id} to Customer {self.customer_id} (score: {self.score})"
