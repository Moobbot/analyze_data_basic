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
        "received against payment",
    ],
    "SELL": [
        "Sale",
        "Sell",
        "Your Sale",
        "Redemption",
        "SOLD for you as AGENT",
        "BOUGHT from you as PRINCIPAL",
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
