import logging

import requests
from apscheduler.jobstores.base import JobLookupError
from flask import (
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from src.ext.database import query_all
from src.ext.jobs import IMPORT_JOB_ID, fill_backlog, register_import_job
from src.models.cycle import WhoopCycle
from src.models.recovery import WhoopRecovery
from src.models.schedule import clear_schedule, load_schedule, save_schedule
from src.models.sleep import WhoopSleep
from src.models.workout import WhoopWorkout
from src.utils import ImportStatus

logger = logging.getLogger(__name__)


def index():
    """
    Retrieve data from database.
    """
    cycles = query_all(WhoopCycle)
    sleeps = query_all(WhoopSleep)
    recoveries = query_all(WhoopRecovery)
    workouts = query_all(WhoopWorkout)

    return render_template(
        "index.html",
        cycles=cycles,
        sleeps=sleeps,
        recoveries=recoveries,
        workouts=workouts,
    )


def authorize():
    """
    Initiates the OAuth2 authorization flow by redirecting to the authorization URL.
    """

    whoo_client = current_app.config["WhoopClient"]

    return redirect(whoo_client.authorization_url(), code=302)


def callback():
    """
    Handles the OAuth2 callback and exchanges the authorization code for tokens.
    """
    code = request.args.get("code")
    state = request.args.get("state")

    expected = current_app.config.pop("OAuthState", None)
    if expected is None or state != expected:
        flash("Invalid OAuth state", "danger")
        return redirect(url_for("webui.index"))

    try:
        client = current_app.config["WhoopClient"]
        client.set_tokens(code)
        from src.models.token import save_tokens

        save_tokens(client)
        flash("Authorized", "success")

    except requests.HTTPError as e:
        flash(f"Failed to set tokens: {e}", "danger")
        return redirect(url_for("webui.index"))

    return redirect(url_for("webui.index"))


def manual_import():
    """
    Manual retrieve and import Whoop data.
    """
    logger.info("Starting import via web UI")

    fill_backlog(current_app)
    return jsonify({"message": "Import tasks queued"}), 201


def schedule():
    """
    Schedule (POST) or disable (DELETE) the daily data import.
    """

    scheduler = current_app.config.get("Scheduler")

    if not scheduler:
        return {"error": "Scheduler not configured"}, 500

    if request.method == "DELETE":
        clear_schedule()
        try:
            scheduler.remove_job(IMPORT_JOB_ID)
        except JobLookupError:
            pass
        logger.info("Import job disabled")
        return {"message": "Import schedule disabled"}, 200

    data = request.get_json()

    if not data:
        abort(400, description="Missing input")

    hour = data.get("hour")
    minute = data.get("minute")

    if hour is None or minute is None:
        abort(400, description="Invalid input")

    try:
        hour = int(hour)
        minute = int(minute)

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        abort(400, description="Invalid input")

    save_schedule(hour, minute)
    register_import_job(current_app._get_current_object(), hour, minute)  # type: ignore

    logger.info("Import job scheduled")

    return {"message": "Import scheduled successfully"}, 201


def status():
    """
    Get the status of the import queue.
    """

    import_queue = current_app.config.get("ImportQueue", [])
    last_status = current_app.config.get("LastImportStatus", ImportStatus.UNKNOWN)
    saved = load_schedule()

    return {
        "backlog": len(import_queue),
        "last_status": last_status.value,
        "schedule": {"hour": saved[0], "minute": saved[1]} if saved else None,
    }, 200
