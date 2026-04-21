from app.services import rate_limit_service


def test_rate_limiter_blocks_after_threshold():
    user_id = "user-test-rate-limit"
    rate_limit_service._user_message_timestamps.pop(user_id, None)

    for _ in range(rate_limit_service.MAX_MESSAGES_PER_WINDOW):
        assert rate_limit_service.is_rate_limited(user_id) is False

    assert rate_limit_service.is_rate_limited(user_id) is True

    rate_limit_service._user_message_timestamps.pop(user_id, None)