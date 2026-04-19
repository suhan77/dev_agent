from __future__ import annotations

import logging


def configure_logging(verbose: bool = False) -> None:
    """CLI에서 사용할 기본 로그 설정을 적용합니다."""
    level = logging.INFO if verbose else logging.WARNING

    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
    )
