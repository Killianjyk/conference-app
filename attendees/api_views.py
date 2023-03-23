from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Attendee
from events.models import Conference
from django.views.decorators.http import require_http_methods
import json


class AttendeesListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    if request.method == "GET":
        attendees = Attendee.objects.all()
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeesListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
    ]

    def get_extra_data(self, o):
        return {"conference": o.conference.name}


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_attendee(request, id):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)

        try:
            if "conference" in content:
                conference = Conference.objects.get(id=id)
                content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference"},
                status=400,
            )

        Attendee.objects.filter(id=id).update(**content)

        attendee = Attendee.objects.get(id=id)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
