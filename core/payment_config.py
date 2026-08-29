import os


class PaymentConfig:

    def __init__(self):
        self.mode = os.getenv("PAYMENT_MODE", "SIMULATION")

        self.provider = os.getenv(
            "PAYMENT_PROVIDER",
            "NONE"
        )

        self.api_key = os.getenv(
            "PAYMENT_API_KEY",
            ""
        )

        self.webhook_secret = os.getenv(
            "PAYMENT_WEBHOOK_SECRET",
            ""
        )

    def status(self):
        return {
            "mode": self.mode,
            "provider": self.provider,
            "api_key_configured": bool(self.api_key),
            "webhook_configured": bool(self.webhook_secret),
            "real_payments_enabled": (
                self.mode == "LIVE"
                and bool(self.api_key)
                and bool(self.webhook_secret)
            )
        }


if __name__ == "__main__":
    config = PaymentConfig()

    print("PAYMENT CONFIG")
    print("================")
    print("Mode:", config.mode)
    print("Provider:", config.provider)
    print("API Key Configured:", config.status()["api_key_configured"])
    print("Webhook Configured:", config.status()["webhook_configured"])
    print("REAL PAYMENTS:", config.status()["real_payments_enabled"])
