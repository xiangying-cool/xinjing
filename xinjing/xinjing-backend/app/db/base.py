from app.db.session import Base

# Import all models so metadata can discover tables
from app.models.chat import ChatMessage, ChatSession  # noqa: F401
from app.models.evaluation import (  # noqa: F401
    EvaluationSession,
    FeatureSnapshot,
    MediaAsset,
    ModalityQualityMetric,
    ModelInferenceResult,
    SessionContextInfo,
)
from app.models.mood import EmotionCheckin, MoodCalendarRecord, TrendSnapshot  # noqa: F401
from app.models.questionnaire import (  # noqa: F401
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireResult,
    QuestionnaireTemplate,
)
from app.models.report import (  # noqa: F401
    EmergencyAlert,
    InterventionRecommendation,
    Report,
)
from app.models.user import User, UserProfile  # noqa: F401
