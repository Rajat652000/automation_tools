import csv
import json
import threading
import uuid

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from .models import Lead
from .services import discover_leads
from portal.decorators import tool_access



# =========================================================
# BACKGROUND JOB STORAGE
# =========================================================

JOBS = {}


# =========================================================
# HOME
# =========================================================

@tool_access("scraper")
def scraper_home(request):
    leads = Lead.objects.filter(owner=request.user).order_by("-created_at")

    return render(
        request,
        "web_scraper/home.html",
        {
            "leads": leads,
            "total_leads": leads.count(),
        },
    )




# =========================================================
# PROGRESS CALLBACK
# =========================================================

def update_job_progress(job_id, progress):

    """
    Receives progress updates from services.py.

    Expected progress format:

    {
        "stage": "...",
        "current": 10,
        "total": 100,
        "found": 10,
        "saved": 0,
        "skipped": 0,
        "message": "..."
    }
    """

    if job_id not in JOBS:
        return

    current_job = JOBS[job_id]

    current_job.update({

        "status": "running",

        "stage": progress.get(
            "stage",
            current_job.get(
                "stage",
                "Working..."
            )
        ),

        "current": progress.get(
            "current",
            current_job.get(
                "current",
                0
            )
        ),

        "total": progress.get(
            "total",
            current_job.get(
                "total",
                0
            )
        ),

        "found": progress.get(
            "found",
            current_job.get(
                "found",
                0
            )
        ),

        "saved": progress.get(
            "saved",
            current_job.get(
                "saved",
                0
            )
        ),

        "skipped": progress.get(
            "skipped",
            current_job.get(
                "skipped",
                0
            )
        ),

        "message": progress.get(
            "message",
            current_job.get(
                "message",
                ""
            )
        ),
    })


# =========================================================
# BACKGROUND SCRAPING JOB
# =========================================================

def run_scraping_job(
    job_id,
    context,
    max_results,
    owner
):

    try:

        # =================================================
        # IMPORTANT
        #
        # max_results = NEW leads requested in THIS search.
        #
        # Existing database records are NOT counted toward
        # this number.
        #
        # Example:
        #
        # DB = 16
        # User asks = 100
        #
        # Search for 100 NEW businesses.
        # Final DB can become 116.
        # =================================================

        existing_count = Lead.objects.filter(owner=owner).count()

        JOBS[job_id].update({

            "status": "running",

            "stage": (
                "🔎 Searching for new businesses..."
            ),

            "current": 0,

            "total": max_results,

            "saved": 0,

            "skipped": 0,

            "found": 0,

            "message": (
                f"{existing_count} existing leads in database. "
                f"Looking for {max_results} NEW leads."
            ),
        })


        # =================================================
        # SERVICE PROGRESS CALLBACK
        # =================================================

        def progress_callback(progress):

            # ---------------------------------------------
            # Keep service progress separate from DB count.
            #
            # current = number processed/found in THIS job
            # total   = requested NEW leads
            # ---------------------------------------------

            update_job_progress(
                job_id,
                progress
            )


        # =================================================
        # DISCOVER LEADS
        # =================================================

        results = discover_leads(

            context=context,

            max_results=max_results,

            progress_callback=progress_callback,
        )


        print(
            "===================================="
        )

        print(
            "DISCOVER LEADS RESULT COUNT:",
            len(results)
        )

        print(
            "===================================="
        )


        # =================================================
        # SAVE RESULTS
        # =================================================

        JOBS[job_id].update({

            "status": "running",

            "stage": "💾 Saving new leads...",

            "current": 0,

            "total": max_results,

            "found": len(results),

            "saved": 0,

            "skipped": 0,

            "message": (
                f"Found {len(results)} new businesses. "
                f"Saving them to database..."
            ),
        })


        saved = 0

        skipped = 0


        # =================================================
        # SAVE EACH LEAD
        # =================================================

        for index, lead in enumerate(
            results,
            start=1
        ):

            # -------------------------------------------------
            # PLACE ID
            # -------------------------------------------------

            place_id = lead.get(
                "place_id",
                ""
            )

            if place_id:

                place_id = place_id.strip()


            # -------------------------------------------------
            # CHECK DUPLICATE
            # -------------------------------------------------

            if place_id:

                already_exists = Lead.objects.filter(owner=owner, place_id=place_id).exists()

                if already_exists:

                    skipped += 1

                    JOBS[job_id].update({

                        "status": "running",

                        "stage": (
                            f"💾 Saving leads... "
                            f"{index}/{len(results)}"
                        ),

                        "current": index,

                        "total": max_results,

                        "saved": saved,

                        "skipped": skipped,

                        "found": len(results),

                        "message": (
                            f"{saved} saved, "
                            f"{skipped} duplicates skipped."
                        ),
                    })

                    continue


            # -------------------------------------------------
            # SAVE LEAD
            # -------------------------------------------------

            try:

                Lead.objects.create(

                    owner=owner,

                    business_name=lead.get(
                        "business_name",
                        ""
                    ),

                    place_id=(
                        place_id
                        or None
                    ),

                    category=lead.get(
                        "category",
                        ""
                    ),

                    location=lead.get(
                        "location",
                        ""
                    ),

                    search_context=context,

                    website=lead.get(
                        "website",
                        ""
                    ),

                    email=lead.get(
                        "email",
                        ""
                    ),

                    phone=lead.get(
                        "phone",
                        ""
                    ),

                    instagram=lead.get(
                        "instagram",
                        ""
                    ),

                    facebook=lead.get(
                        "facebook",
                        ""
                    ),

                    linkedin=lead.get(
                        "linkedin",
                        ""
                    ),

                    source_url=lead.get(
                        "source_url",
                        ""
                    ),

                    has_website=lead.get(
                        "has_website",
                        False
                    ),
                )

                saved += 1


            except Exception as save_error:

                # -----------------------------------------
                # Handle race-condition / unique place_id
                # -----------------------------------------

                if place_id and Lead.objects.filter(owner=owner, place_id=place_id).exists():

                    skipped += 1

                else:

                    raise save_error


            # -------------------------------------------------
            # UPDATE UI
            # -------------------------------------------------

            current_db_count = Lead.objects.filter(owner=owner).count()

            JOBS[job_id].update({

                "status": "running",

                "stage": (
                    f"💾 Saving leads... "
                    f"{index}/{len(results)}"
                ),

                "current": index,

                "total": max_results,

                "saved": saved,

                "skipped": skipped,

                "found": len(results),

                "message": (
                    f"{saved} new leads saved. "
                    f"{skipped} duplicates skipped."
                ),
            })


        # =================================================
        # FINAL STATUS
        # =================================================

        final_count = Lead.objects.filter(owner=owner).count()


        if len(results) >= max_results:

            final_message = (
                f"Search completed. "
                f"{saved} new leads saved."
            )

        else:

            final_message = (
                f"Search completed. "
                f"Only {len(results)} genuine new "
                f"businesses were found."
            )


        if skipped > 0:

            final_message += (
                f" {skipped} duplicates skipped."
            )


        JOBS[job_id].update({

            "status": "completed",

            "stage": "✅ Search completed",

            "current": len(results),

            "total": max_results,

            "saved": saved,

            "skipped": skipped,

            "found": len(results),

            "message": final_message,

            "database_total": final_count,
        })


    # =====================================================
    # ERROR
    # =====================================================

    except Exception as error:

        print(
            "===================================="
        )

        print(
            "SCRAPING ERROR:",
            repr(error)
        )

        print(
            "===================================="
        )


        JOBS[job_id].update({

            "status": "error",

            "stage": "❌ Search failed",

            "message": str(error),

        })


# =========================================================
# START SCRAPING
# =========================================================

@tool_access("scraper")
def start_scraping(request):

    # =====================================================
    # ONLY POST
    # =====================================================

    if request.method != "POST":

        return JsonResponse(

            {
                "error": (
                    "POST request required"
                )
            },

            status=405
        )


    # =====================================================
    # SEARCH CONTEXT
    # =====================================================

    context = request.POST.get(
        "context",
        ""
    ).strip()


    if not context:

        return JsonResponse(

            {
                "error": (
                    "Search context is required"
                )
            },

            status=400
        )


    # =====================================================
    # MAX RESULTS
    # =====================================================

    try:

        max_results = int(
            request.POST.get(
                "max_results",
                20
            )
        )

    except (
        ValueError,
        TypeError
    ):

        max_results = 20


    # =====================================================
    # VALIDATE RESULT LIMIT
    # =====================================================

    if max_results <= 0:

        return JsonResponse(

            {
                "error": (
                    "max_results must be greater than 0"
                )
            },

            status=400
        )


    # Prevent accidental crazy requests.

    if max_results > 1000:

        return JsonResponse(

            {
                "error": (
                    "Maximum 1000 leads per search."
                )
            },

            status=400
        )


    # =====================================================
    # CREATE JOB
    # =====================================================

    job_id = str(
        uuid.uuid4()
    )


    existing_count = Lead.objects.filter(owner=request.user).count()


    JOBS[job_id] = {

        "status": "starting",

        "stage": (
            "Preparing search..."
        ),

        "current": 0,

        "total": max_results,

        "saved": 0,

        "skipped": 0,

        "found": 0,

        "database_total": existing_count,

        "message": (
            f"Looking for "
            f"{max_results} new leads..."
        ),
    }


    # =====================================================
    # START BACKGROUND THREAD
    # =====================================================

    thread = threading.Thread(

        target=run_scraping_job,

        args=(

            job_id,

            context,

            max_results,

            request.user,
        ),

        daemon=True,
    )


    thread.start()


    # =====================================================
    # RESPONSE
    # =====================================================

    return JsonResponse({

        "status": "started",

        "job_id": job_id,

        "message": (
            "Scraping started."
        ),
    })


# =========================================================
# SEARCH STATUS
# =========================================================

@tool_access("scraper")
def scraping_status(
    request,
    job_id
):

    job = JOBS.get(
        job_id
    )


    if not job:

        return JsonResponse(

            {
                "status": "error",

                "message": (
                    "Job not found."
                )
            },

            status=404
        )


    return JsonResponse(
        job
    )


# =========================================================
# CLEAR RESULTS
# =========================================================

@tool_access("scraper")
@require_POST
def clear_results(request):

    # =====================================================
    # DELETE ALL LEADS
    # =====================================================

    deleted_count, _ = (
        Lead.objects.filter(owner=request.user).delete()
    )


    # =====================================================
    # RESPONSE
    # =====================================================

    return JsonResponse({

        "status": "success",

        "deleted": deleted_count,

        "message": (
            f"{deleted_count} leads deleted."
        ),
    })


# =========================================================
# EXPORT CSV
# =========================================================

@tool_access("scraper")
def export_leads_csv(request):

    response = HttpResponse(

        content_type=(
            "text/csv; charset=utf-8"
        )
    )


    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="lead_data_review.csv"'
    )


    # =====================================================
    # CSV WRITER
    # =====================================================

    writer = csv.writer(
        response
    )


    writer.writerow([

        "#",

        "Current Business",

        "Website",

        "Email",

        "Phone",

        "Instagram",

        "Facebook",

        "LinkedIn",

        "Source",

        "Correct Business Name",

        "Website Correct?",

        "Data Correct?",

        "What Should Change?"
    ])


    # =====================================================
    # LEADS
    # =====================================================

    leads = Lead.objects.filter(owner=request.user).order_by(
        "-created_at"
    )


    # =====================================================
    # WRITE ROWS
    # =====================================================

    for index, lead in enumerate(
        leads,
        start=1
    ):

        writer.writerow([

            index,

            lead.business_name,

            lead.website,

            lead.email,

            lead.phone,

            lead.instagram,

            lead.facebook,

            lead.linkedin,

            lead.source_url,

            "",

            "",

            "",

            "",
        ])


    return response


# =========================================================
# EXPORT JSON
# =========================================================

@tool_access("scraper")
def export_leads_json(request):
    """Download all saved leads as a structured JSON document."""
    leads = Lead.objects.filter(owner=request.user).order_by("-created_at")
    data = [
        {
            "id": lead.id,
            "business_name": lead.business_name,
            "category": lead.category,
            "location": lead.location,
            "search_context": lead.search_context,
            "website": lead.website,
            "email": lead.email,
            "phone": lead.phone,
            "instagram": lead.instagram,
            "facebook": lead.facebook,
            "linkedin": lead.linkedin,
            "source_url": lead.source_url,
            "has_website": lead.has_website,
            "place_id": lead.place_id,
            "created_at": lead.created_at.isoformat(),
        }
        for lead in leads
    ]
    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="lead_data.json"'
    return response
