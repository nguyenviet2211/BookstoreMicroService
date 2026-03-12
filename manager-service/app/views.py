from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Manager
from .serializers import ManagerSerializer

import requests
import logging

logger = logging.getLogger(__name__)

STAFF_SERVICE_URL = 'http://staff-service:8001'


class ManagerListCreateView(APIView):
    def get(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerDetailView(APIView):
    def get(self, request, pk):
        try:
            manager = Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ManagerSerializer(manager)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            manager = Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ManagerSerializer(manager, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            manager = Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
        manager.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerStaffView(APIView):
    """Manager can view all staff members via staff-service."""
    def get(self, request, pk):
        try:
            Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            response = requests.get(f"{STAFF_SERVICE_URL}/api/staff/", timeout=5)
            return Response(response.json())
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch staff: {e}")
            return Response({"error": "Staff service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "manager-service"})
