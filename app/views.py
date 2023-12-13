from django.http import HttpRequest, HttpResponse
# Create your views here.
from asyncio import sleep
from app.models import Counter

async def ok(req: HttpRequest) -> HttpResponse:
    # simulate a view that does a DB request, then some slow async processing, then another DB request
    ctr, _ = await Counter.objects.aget_or_create(pk=1)

    await sleep(3)

    # this change is just so we can force a DB write and confirm something happens
    # (its not an accurate counter if there are parallel requests as there's no transaction/lock)
    ctr.count += 1

    await ctr.asave()

    return HttpResponse(f"counter is at: {ctr.count}")
