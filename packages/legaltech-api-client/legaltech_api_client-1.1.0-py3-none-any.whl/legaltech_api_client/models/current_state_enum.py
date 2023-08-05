from enum import Enum


class CurrentStateEnum(str, Enum):
    CLAIM_CREATED = "claim_created"
    CLAIM_MISMATCH_DOC = "claim_mismatch_doc"
    CLAIM_NOT_SCOPE = "claim_not_scope"
    CLAIM_REJECTED = "claim_rejected"
    CLAIM_RESTORED = "claim_restored"
    CONTENT_BRAND_ABUSE = "content_brand_abuse"
    CONTENT_COUNTERFEIT = "content_counterfeit"
    CONTENT_DISCARDED = "content_discarded"
    CONTENT_DOWN = "content_down"
    CONTENT_GRAY_MARKET = "content_gray_market"
    CONTENT_LEGAL = "content_legal"
    CONTENT_NOT_ENFORCEABLE = "content_not_enforceable"
    CONTENT_PARALLEL_IMPORT = "content_parallel_import"
    CONTENT_TO_WHITELIST = "content_to_whitelist"
    CONTENT_USE_OF_IMAGES = "content_use_of_images"
    LETTER_SENT = "letter_sent"
    NOTIFICATION_SENT = "notification_sent"
    OPEN_DISPUTE = "open_dispute"
    PENDING_LEGAL_SETUP = "pending_legal_setup"
    TEST_PURCHASE = "test_purchase"
    TEST_PURCHASE_RESULTS = "test_purchase_results"

    def __str__(self) -> str:
        return str(self.value)
