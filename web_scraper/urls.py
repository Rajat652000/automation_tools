from django.urls import path

from .views import (
    scraper_home,
    start_scraping,
    scraping_status,
    clear_results,
    export_leads_csv,
    export_leads_json,
)


urlpatterns = [

    path(
        "",
        scraper_home,
        name="scraper_home"
    ),


    path(
        "start/",
        start_scraping,
        name="start_scraping"
    ),

    path(
        "status/<str:job_id>/",
        scraping_status,
        name="scraping_status"
    ),

    path(
        "clear/",
        clear_results,
        name="clear_results"
    ),

    path(
        "export/",
        export_leads_csv,
        name="export_leads"
    ),

    path(
        "export/json/",
        export_leads_json,
        name="export_leads_json"
    ),
]
