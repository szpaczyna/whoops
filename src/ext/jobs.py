import dataclasses
import datetime
import logging

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from src.ext.database import upsert_all
from src.models import WhoopCycle, WhoopRecovery, WhoopSleep, WhoopWorkout
from src.models.schedule import load_schedule
from src.utils import ImportStatus, ImportTask

logger = logging.getLogger(__name__)

logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)

IMPORT_JOB_ID = "import_job"


def refresh_token_job(app):
    logger.info("Running refresh token job")

    whoop_client = app.config["WhoopClient"]
    if not whoop_client.tokens:
        logger.error("Manual authorization required. Visit /authorize.")
        return

    try:
        if whoop_client.ensure_fresh_token():
            logger.info("Token refreshed successfully.")
    except requests.HTTPError:
        logger.error("Manual authorization required. Visit /authorize.")


def fill_backlog(app, start=None):
    whoop_client = app.config["WhoopClient"]
    import_queue = app.config["ImportQueue"]

    for task in (
        ImportTask(WhoopWorkout, whoop_client.get_workouts, start),
        ImportTask(WhoopCycle, whoop_client.get_cycles, start),
        ImportTask(WhoopSleep, whoop_client.get_sleeps, start),
        ImportTask(WhoopRecovery, whoop_client.get_recoveries, start),
    ):
        if task not in import_queue:
            import_queue.append(task)

    # request immediate import
    job = app.config["Scheduler"].get_job("import_worker")
    job.modify(next_run_time=datetime.datetime.now(datetime.timezone.utc))


def incremental_backlog(app):
    days = int(app.config.get("INCREMENTAL_IMPORT_DAYS", 7))
    start = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    logger.info(f"Starting incremental import from {start.isoformat()}")
    fill_backlog(app, start=start)


def register_import_job(app, hour: int, minute: int):
    app.config["Scheduler"].add_job(
        func=incremental_backlog,
        trigger="cron",
        hour=hour,
        minute=minute,
        args=[app],
        id=IMPORT_JOB_ID,
        replace_existing=True,
    )


def _refresh_after_401(app) -> bool:
    try:
        app.config["WhoopClient"].refresh_token()
        return True
    except requests.HTTPError:
        return False


def _import_worker(app):
    import_queue = app.config["ImportQueue"]

    if not import_queue:
        return

    logger.info(f"Import queue size: {len(import_queue)}")

    task = import_queue.popleft()
    status = ImportStatus.STARTED

    try:
        result, fetch_skipped = task.callable(start=task.start)
        with app.app_context():
            db_skipped = upsert_all(result)

        if fetch_skipped + db_skipped > 0:
            fetched = len(result) + fetch_skipped
            written = len(result) - db_skipped
            skipped = fetch_skipped + db_skipped
            status = ImportStatus.SKIPPED
            logger.warning(
                "%s import completed with skipped records (fetched=%d, written=%d, skipped=%d)",
                task.model.__name__,
                fetched,
                written,
                skipped,
            )
        else:
            logger.info(f"{task.model.__name__} imported successfully ({len(result)})")
            status = ImportStatus.SUCCESS

    except requests.HTTPError as e:
        status_code = getattr(e.response, "status_code", None)

        if status_code == 401:
            if not task.retried_after_401 and _refresh_after_401(app):
                logger.warning(f"Unauthorized during {task.model.__name__} import, token refreshed, re-queueing task")
                import_queue.appendleft(dataclasses.replace(task, retried_after_401=True))
            else:
                logger.exception("Unauthorized error")
                status = ImportStatus.UNAUTHORIZED
                import_queue.clear()
        elif status_code == 429:
            logger.exception("Rate limit hit, re-queueing task")
            status = ImportStatus.RATE_LIMIT
            if task not in import_queue:
                import_queue.append(task)
        elif status_code is not None and 500 <= status_code < 600:
            logger.exception("Server error, re-queueing task")
            status = ImportStatus.SERVER_ERROR
            if task not in import_queue:
                import_queue.append(task)
        else:
            logger.exception("Unexpected HTTP error")
            status = ImportStatus.UNEXPECTED_ERROR

    except requests.ConnectionError:
        logger.exception("Connection error, re-queueing task")
        status = ImportStatus.CONNECTION_ERROR
        if task not in import_queue:
            import_queue.append(task)

    except requests.Timeout:
        logger.exception("Request timed out, re-queueing task")
        status = ImportStatus.TIMEOUT
        if task not in import_queue:
            import_queue.append(task)

    except Exception:
        logger.exception("Unexpected error")
        status = ImportStatus.UNEXPECTED_ERROR

    finally:
        logger.info(f"Import queue size: {len(import_queue)}")
        app.config["LastImportStatus"] = status


def init_app(app):
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        refresh_token_job,
        "interval",
        minutes=5,
        args=[app],
        id="refresh_token_job",
    )

    scheduler.add_job(
        _import_worker,
        "interval",
        minutes=1,
        args=[app],
        id="import_worker",
    )

    app.config["Scheduler"] = scheduler

    scheduler.start()

    with app.app_context():
        try:
            saved = load_schedule()
        except Exception:  # noqa: BLE001 - startup must not fail on a missing table
            logger.exception("Could not load import schedule")
            saved = None

    if saved:
        register_import_job(app, *saved)
        logger.info(f"Import job restored at {saved[0]:02d}:{saved[1]:02d} UTC")
