from datetime import datetime
import pytz

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def get_kst_now() -> datetime:
    """현재 한국 시간을 반환"""
    return datetime.now(KST)

def to_kst(dt: datetime) -> datetime:
    """주어진 datetime을 한국 시간으로 변환"""
    if dt.tzinfo is None:
        # naive datetime은 UTC로 가정하고 KST로 변환
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(KST)

def from_kst_to_utc(dt: datetime) -> datetime:
    """한국 시간을 UTC로 변환"""
    if dt.tzinfo is None:
        # naive datetime은 KST로 가정
        dt = KST.localize(dt)
    return dt.astimezone(pytz.UTC)

def localize_kst(dt: datetime) -> datetime:
    """naive datetime을 KST로 로컬라이즈"""
    if dt.tzinfo is None:
        return KST.localize(dt)
    return dt

def format_kst_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """한국 시간을 지정된 형식으로 포맷"""
    kst_dt = to_kst(dt) if dt.tzinfo else localize_kst(dt)
    return kst_dt.strftime(format_str)
