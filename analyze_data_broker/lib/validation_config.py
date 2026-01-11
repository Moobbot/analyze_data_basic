# validation_config.py

# ==============================================================================
# 1. CONSTANTS & CONFIGURATION
# ==============================================================================

# Define keywords for verifying "Transaction Type"
# Maps standard types "BUY" and "SELL" to list of possible valid values
TRANSACTION_KEYWORDS = {
    "BUY": [
        "Buy",
        "Purchase",
        "Your Purchase",
        "New issue purchase",
        "SOLD to you as PRINCIPAL",
        "BOUGHT for you as AGENT",
        "HAVE BOUGHT FOR",
        "Receive against payment",
    ],
    "BUY CANCELLATION": [
        "New issue purchase Cancellation",
    ],
    "SELL": [
        "Sale",
        "Sell",
        "Your Sale",
        "Redemption",
        "SOLD for you as AGENT",
        "BOUGHT from you as PRINCIPAL",
    ],
    "SELL CANCELLATION": [
        "Your sale Cancellation",
    ],
    "ADJUSTMENT MAX. NOTIONAL": [
        "Adjustment Max. Notional",
    ],
    "KNOCKOUT ADVICE": [
        "Knockout Advice",
    ],
    "MATURITY": [
        "Maturity",
    ],
    "PREPAYMENT FOR FUND SUBSCRIPTION": [
        "Prepayment for fund subscription",
    ],
    "PREPAYMENT FOR FUND SUBSCRIPTION CORRECTION": [
        "Prepayment for fund subscription Correction",
    ],
    "PREPAYMENT FOR FUND SUBSCRIPTION CANCELLATION": [
        "Prepayment for fund subscription Cancellation",
    ],
}

# Define keywords for verifying Context of Date Fields
# Used to check if the date found in JSON also appears near these words in text
DATE_KEYWORDS = {
    "Trade Date": ["trade date", "traded on", "booking date"],
    "Settlement Date": [
        "Value date",
        "Settlement due on",
        "Settlement date",
        "Payment date",
        "Receipt date",
    ],
}
