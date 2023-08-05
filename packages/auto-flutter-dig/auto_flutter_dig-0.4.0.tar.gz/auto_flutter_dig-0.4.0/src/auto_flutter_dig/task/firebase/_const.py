from ...core.config import Config
from ...core.utils import _Lazy, _Static

FIREBASE_CONFIG_KEY_PATH = "firebase"
FIREBASE_CONFIG_KEY_STANDALONE = "firebase-standalone"
FIREBASE_PROJECT_APP_ID_KEY = _Static("google-app-id")
FIREBASE_DISABLE_INTERACTIVE_MODE = _Static("--non-interactive")
FIREBASE_ENV = _Lazy(
    lambda: {"FIREPIT_VERSION": "1"}
    if Config.get_bool(FIREBASE_CONFIG_KEY_STANDALONE)
    else {}
)
