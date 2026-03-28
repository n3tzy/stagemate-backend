"""
cron.py — StageMate 정기 정리 작업 (Railway Cron Service)
실행 주기: 1시간마다 (railway.toml 참고)

작업 목록:
  1. expire_boosts        — 만료된 홍보 부스트 게시글 리셋
  2. expire_plans         — 만료된 동아리 플랜 → free 강등 + 관련 구독 트랜잭션 expired 처리
  3. cleanup_presign      — 만료된 presign_requests 레코드 삭제
"""

import logging
from datetime import datetime

from database import SessionLocal
import db_models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CRON] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def expire_boosts(db) -> int:
    """boost_expires_at이 지난 게시글의 부스트 플래그를 해제한다."""
    now = datetime.utcnow()
    rows = (
        db.query(db_models.Post)
        .filter(
            db_models.Post.is_boosted == True,
            db_models.Post.boost_expires_at <= now,
        )
        .all()
    )
    for post in rows:
        post.is_boosted = False
        post.boost_expires_at = None
    db.commit()
    if rows:
        logger.info(f"expire_boosts: {len(rows)}개 게시글 부스트 해제")
    return len(rows)


def expire_plans(db) -> int:
    """plan_expires_at이 지난 동아리를 free 플랜으로 강등하고
    연관된 active 구독 트랜잭션을 expired 로 표시한다."""
    now = datetime.utcnow()

    # 1) 만료된 동아리 플랜 강등
    clubs = (
        db.query(db_models.Club)
        .filter(
            db_models.Club.plan != "free",
            db_models.Club.plan_expires_at <= now,
        )
        .all()
    )
    club_ids = [c.id for c in clubs]
    for club in clubs:
        logger.info(f"expire_plans: club_id={club.id} ({club.name}) {club.plan} → free")
        club.plan = "free"
        club.plan_expires_at = None

    # 2) 연관 구독 트랜잭션 expired 처리
    tx_count = 0
    if club_ids:
        txs = (
            db.query(db_models.SubscriptionTransaction)
            .filter(
                db_models.SubscriptionTransaction.club_id.in_(club_ids),
                db_models.SubscriptionTransaction.status == "active",
            )
            .all()
        )
        for tx in txs:
            tx.status = "expired"
        tx_count = len(txs)

    # 3) club_id 없는 개인 구독 트랜잭션도 만료 처리
    personal_txs = (
        db.query(db_models.SubscriptionTransaction)
        .filter(
            db_models.SubscriptionTransaction.club_id == None,
            db_models.SubscriptionTransaction.status == "active",
            db_models.SubscriptionTransaction.expires_at <= now,
        )
        .all()
    )
    for tx in personal_txs:
        tx.status = "expired"
    tx_count += len(personal_txs)

    db.commit()
    if clubs or tx_count:
        logger.info(
            f"expire_plans: {len(clubs)}개 동아리 강등, {tx_count}개 트랜잭션 expired"
        )
    return len(clubs)


def cleanup_presign(db) -> int:
    """만료된 presign_requests 레코드를 삭제한다."""
    now = datetime.utcnow()
    deleted = (
        db.query(db_models.PresignRequest)
        .filter(db_models.PresignRequest.expires_at <= now)
        .delete(synchronize_session=False)
    )
    db.commit()
    if deleted:
        logger.info(f"cleanup_presign: {deleted}개 레코드 삭제")
    return deleted


def run():
    logger.info("=== Cron 시작 ===")
    db = SessionLocal()
    try:
        expire_boosts(db)
        expire_plans(db)
        cleanup_presign(db)
    except Exception as e:
        logger.error(f"Cron 실패: {e}", exc_info=True)
        raise
    finally:
        db.close()
    logger.info("=== Cron 완료 ===")


if __name__ == "__main__":
    run()
