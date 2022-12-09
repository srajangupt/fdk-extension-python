import hashlib
import json
import uuid

from ..constants import ONLINE_ACCESS_MODE
from ..utilities.utility import isoformat_to_datetime
from ..utilities.utility import json_serial


class Session:
    def __init__(self, session_id, is_new=True):
        self.session_id = session_id
        self.company_id = None
        self.state = None
        self.scope = None
        self.expires = None
        self.expires_in = None
        self.access_token_validity = None
        self.access_mode = ONLINE_ACCESS_MODE
        self.access_token = None
        self.current_user = None
        self.refresh_token = None
        self.is_new = is_new
        self.extension_id = None

    @staticmethod
    def clone_session(session):
        session_object = Session(session["session_id"], session["is_new"])
        for key in session:
            if key in ["expires"]:
                if session[key]:
                    session[key] = isoformat_to_datetime(session[key])
            setattr(session_object, key, session[key])
        return session_object

    def update_token(self, raw_token: dict):
        self.access_mode = raw_token.get("access_mode")
        self.access_token = raw_token.get("access_token")
        self.current_user = raw_token.get("current_user")
        self.refresh_token = raw_token.get("refresh_token")
        self.expires_in = raw_token.get("expires_in")
        self.access_token_validity = raw_token.get("access_token_validity")

    def to_json(self):
        return json.dumps(self.__dict__, default=json_serial,
                          sort_keys=True, indent=4)

    @staticmethod
    def generate_session_id(is_online, **config_options):
        if is_online:
            return str(uuid.uuid4())
        else:
            return hashlib.sha256(
                "{}:{}".format(config_options["cluster"], config_options["company_id"]).encode()).hexdigest()
