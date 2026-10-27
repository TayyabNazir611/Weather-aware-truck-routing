from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .geometry import distance


class LocationSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=300)
    coordinates = serializers.ListField(child=serializers.FloatField(), min_length=2, max_length=2)

    def validate_coordinates(self, value):
        if not (-180 <= value[0] <= 180 and -85 <= value[1] <= 85):
            raise serializers.ValidationError("Invalid longitude/latitude.")
        return value


class TripSerializer(serializers.Serializer):
    origin = LocationSerializer()
    destination = LocationSerializer()
    departure = serializers.DateTimeField()
    load_lb = serializers.FloatField(min_value=0, max_value=200000)
    interval_miles = serializers.ChoiceField(choices=[10, 25, 50], default=25)

    def validate_departure(self, value):
        raw = str(self.initial_data.get("departure", ""))
        if not (raw.endswith("Z") or "+" in raw[10:] or "-" in raw[10:]):
            raise serializers.ValidationError("Departure must include a timezone offset.")
        now = timezone.now()
        if value < now - timedelta(minutes=5) or value > now + timedelta(days=5):
            raise serializers.ValidationError("Choose a departure between now and five days ahead.")
        return value

    def validate(self, value):
        if distance(value["origin"]["coordinates"], value["destination"]["coordinates"]) < 100:
            raise serializers.ValidationError("Origin and destination must be at least 100 meters apart.")
        if not __import__("math").isfinite(value["load_lb"]):
            raise serializers.ValidationError("Load must be a finite number.")
        return value
