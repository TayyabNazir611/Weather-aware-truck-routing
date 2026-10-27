import logging

from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import exception_handler as drf_exception_handler

from . import providers
from .serializers import TripSerializer
from .service import analyze_trip

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {"message": "Please check your inputs or try again later.", "details": response.data}
        }
    return response


class AnalysisThrottle(AnonRateThrottle):
    scope = "analysis"


@api_view(["GET"])
@throttle_classes([])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def locations(request):
    query = request.query_params.get("q", "").strip()
    if not 3 <= len(query) <= 200:
        return Response({"error": {"message": "Enter 3–200 characters to search."}}, status=400)
    try:
        return Response({"results": providers.locations(query)})
    except providers.ProviderError as e:
        return Response({"error": {"message": e.message}}, status=e.status)


@api_view(["POST"])
@throttle_classes([AnalysisThrottle])
def analyze(request):
    serializer = TripSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        return Response(analyze_trip(serializer.validated_data))
    except providers.ProviderError as e:
        return Response({"error": {"message": e.message}}, status=e.status)
    except (ValueError, KeyError, IndexError, TypeError):
        # Do not log provider payloads, URLs, or credentials.
        logger.error("Provider response failed route schema validation")
        return Response(
            {"error": {"message": "A provider returned incomplete route data. Please try again."}}, status=502
        )
