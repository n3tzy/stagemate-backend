import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── 필수 환경변수 (미설정 시 서버 시작 불가) ─────────────
    SECRET_KEY: str
    DATABASE_URL: str

    # ── 선택 환경변수 (기본값 있음) ──────────────────────────
    # CORS 허용 origin (콤마로 구분, 예: https://app.example.com,https://www.example.com)
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Access token 만료: 30일 (43200분)
    # 앱 시작 시 서버 재검증(/auth/me)이 있으므로 탈취 시에도 빠른 무효화 가능.
    # 진정한 "무기한 로그인"이 필요하다면 refresh token 구조 도입 필요.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # 로그인 실패 허용 횟수 (초과 시 계정 잠금)
    MAX_LOGIN_ATTEMPTS: int = 5

    # 계정 잠금 지속 시간 (분)
    LOGIN_LOCKOUT_MINUTES: int = 15

    # Railway/Production 환경 여부
    IS_PRODUCTION: bool = False

    # ── 이메일 (Gmail SMTP) — 비밀번호 재설정용 ──────────────
    # Gmail 앱 비밀번호: https://myaccount.google.com/apppasswords
    MAIL_USERNAME: str = ""        # 발신 Gmail 주소
    MAIL_PASSWORD: str = ""        # Gmail 앱 비밀번호 (16자리)
    MAIL_FROM: str = ""            # 발신자 이메일 (보통 MAIL_USERNAME과 동일)
    MAIL_FROM_NAME: str = "StageMate"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # ── Apple 인앱결제 (App Store Connect → 앱 → 앱 내 구입 → 공유 암호)
    # https://appstoreconnect.apple.com → 앱 → 앱 내 구입 탭 → 앱별 공유 암호
    APPLE_IAP_SHARED_SECRET: str = ""

    # ── 카카오 로그인 ──────────────────────────────────────
    KAKAO_REST_API_KEY: str = ""

    # ── Cloudflare R2 (S3 호환 스토리지) ─────────────────────
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_ACCESS_KEY_SECRET: str = ""
    R2_BUCKET_NAME: str = "stagemate-media"
    R2_PUBLIC_URL: str = ""   # 예: https://pub-xxxx.r2.dev

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
