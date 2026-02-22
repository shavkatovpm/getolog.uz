from bot.middlewares.rate_limit import RateLimitMiddleware

# Reuse the same rate limiter for user bots
__all__ = ["RateLimitMiddleware"]
