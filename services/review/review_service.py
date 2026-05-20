from datetime import datetime

from repositories import review_repository


def weekly_review(user_id: str):
    return review_repository.weekly_review_summary(user_id)


def monthly_trigger_check(user_id: str):
    pref = review_repository.get_user_preferences(user_id)
    if not pref:
        return None
    last_review = pref.get("last_monthly_review_at")
    now = datetime.utcnow()
    should_run = last_review is None or (now - last_review).days >= 28
    return {
        "should_run_review": should_run,
        "last_monthly_review_at": last_review.isoformat() if last_review else None,
        "checked_at": now.isoformat(),
    }


def monthly_mark_done(user_id: str):
    ok = review_repository.mark_monthly_review_done(user_id)
    if not ok:
        return None
    return review_repository.get_user_preferences(user_id)
