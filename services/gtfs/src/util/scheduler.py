from datetime import datetime
from ..config import RT_INTERVAL, STATIC_INTERVAL
from .logging import log
from apscheduler.schedulers.background import BackgroundScheduler
from ..business.fetcher import _fetch_static, _fetch_all_realtime


def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(_fetch_all_realtime, "interval", seconds=RT_INTERVAL,
                      id="realtime", next_run_time=datetime.now())
    scheduler.add_job(_fetch_static,       "interval", seconds=STATIC_INTERVAL,
                      id="static",   next_run_time=datetime.now())
    scheduler.start()
    log.info("Scheduler started (RT every %ds, static every %ds)",
             RT_INTERVAL, STATIC_INTERVAL)
    return scheduler
