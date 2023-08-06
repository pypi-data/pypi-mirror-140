import sys

__all__ = [
    "PCMResponseSchemasPredicate",
    "PCMRequestSchemasPredicate",
    "PCMTagsPredicate",
    "PCMSummaryPredicate",
    "PCMDescriptionPredicate",
    "PCMSecurityPredicate",
    "PCMShowInPredicate",
]


class _BasePCMSchemasPredicate:
    PRED_ID = "pcm"

    def __init__(self, val, _):
        self.val = val

    def text(self):
        return "{} = {}".format(self.PRED_ID, self.val)

    phash = text

    def __call__(self, context, request):
        return True


class PCMResponseSchemasPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_responses"


class PCMRequestSchemasPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_request"


class PCMTagsPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_tags"


class PCMSummaryPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_summary"


class PCMDescriptionPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_description"


class PCMSecurityPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_security"


class PCMShowInPredicate(_BasePCMSchemasPredicate):
    PRED_ID = "pcm_show"


def register(config):
    this = sys.modules[__name__]

    for c in __all__:
        cls_ = getattr(this, c)
        config.add_view_predicate(cls_.PRED_ID, cls_)
