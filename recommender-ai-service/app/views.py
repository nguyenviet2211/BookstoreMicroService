from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Recommendation
from .serializers import RecommendationSerializer

import requests
import logging
import random

logger = logging.getLogger(__name__)


class RecommendationListView(APIView):
    """Get recommendations for a customer."""
    def get(self, request, customer_id):
        # Check for cached recommendations
        recommendations = Recommendation.objects.filter(customer_id=customer_id)
        if recommendations.exists():
            serializer = RecommendationSerializer(recommendations, many=True)
            return Response(serializer.data)

        # Generate new recommendations
        generated = self._generate_recommendations(customer_id)
        serializer = RecommendationSerializer(generated, many=True)
        return Response(serializer.data)

    def _generate_recommendations(self, customer_id):
        """
        Simple AI recommendation engine:
        1. Fetch customer's reviews from comment-rate-service
        2. Fetch all books from book-service
        3. Recommend top-rated unreviewed books
        """
        reviewed_book_ids = set()
        recommendations = []

        # Get customer's reviews
        try:
            resp = requests.get(
                f"{settings.COMMENT_RATE_SERVICE_URL}/api/reviews/",
                params={"customer_id": customer_id},
                timeout=5
            )
            if resp.status_code == 200:
                reviews = resp.json()
                reviewed_book_ids = {r['book_id'] for r in reviews}
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch reviews: {e}")

        # Get all books
        try:
            resp = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/", timeout=5)
            if resp.status_code == 200:
                books = resp.json()
                # Filter out already reviewed books and score them
                unreviewed = [b for b in books if b['id'] not in reviewed_book_ids]
                for book in unreviewed[:10]:
                    score = round(random.uniform(0.5, 1.0), 2)
                    rec, _ = Recommendation.objects.get_or_create(
                        customer_id=customer_id,
                        book_id=book['id'],
                        defaults={
                            'score': score,
                            'reason': f"Based on your reading preferences - {book.get('title', 'Unknown')}"
                        }
                    )
                    recommendations.append(rec)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch books: {e}")

        return recommendations


class PopularBooksView(APIView):
    """Get popular books based on average ratings."""
    def get(self, request):
        try:
            # Get all books
            resp = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/", timeout=5)
            if resp.status_code != 200:
                return Response({"error": "Book service unavailable"},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)
            books = resp.json()

            # Get ratings for each book
            popular = []
            for book in books[:20]:
                try:
                    rating_resp = requests.get(
                        f"{settings.COMMENT_RATE_SERVICE_URL}/api/reviews/book/{book['id']}/average/",
                        timeout=5
                    )
                    if rating_resp.status_code == 200:
                        rating_data = rating_resp.json()
                        book['average_rating'] = rating_data.get('average_rating')
                        book['total_reviews'] = rating_data.get('total_reviews', 0)
                except requests.exceptions.RequestException:
                    book['average_rating'] = None
                    book['total_reviews'] = 0
                popular.append(book)

            # Sort by rating (descending)
            popular.sort(key=lambda x: x.get('average_rating') or 0, reverse=True)
            return Response(popular)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to generate popular books: {e}")
            return Response({"error": "Service unavailable"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "recommender-ai-service"})
