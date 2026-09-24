from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bcrypt = Bcrypt()
csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})
limiter = Limiter(key_func=get_remote_address,
                  default_limits=['500 per day', '100 per hour'])