import copy
import hashlib
import json
import uuid


class Session:
    def __init__(self, session_id, is_new=True):
        self.session_id = session_id
        self.company_id = None
        self.state = None
        self.scope = None
        self.expires = None
        self.expires_in = None
        self.access_token_validity = None
        self.access_mode = "online"
        self.access_token = None
        self.current_user = None
        self.refresh_token = None
        self.isNew = is_new
        self.extension_id = None

    @staticmethod
    def clone_session(session):
        return copy.deepcopy(session)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    @staticmethod
    def generate_session_id(is_online, **config_options):
        if is_online:
            return uuid.uuid4()
        else:
            return hashlib.sha256(
                "{}:{}".format(config_options["cluster"], config_options["company_id"]).encode()).hexdigest()
