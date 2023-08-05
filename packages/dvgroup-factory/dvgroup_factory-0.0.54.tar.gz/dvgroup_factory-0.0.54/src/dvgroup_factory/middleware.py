from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi import Request, Response, status as fastapi_status
import traceback
from datetime import datetime
import json
import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

class RequestUser(BaseModel):
    name: str = ""
    email: str = ""
    scopes: Optional[List] = []
    tenants: Optional[List] = []
    properties: Optional[Dict] = {}

class AuthenticationBackend(BaseHTTPMiddleware):
    def __init__(self, app, logger, public_key=None, access_algorithm=None, factory=None):
        super(AuthenticationBackend, self).__init__(app)
        self.logger = logger
        self.access_algorithm = "RS256"
        if factory is not None:
            consul = factory.consul(new=True)
            self.public_key = json.loads(consul.kv.get("services/auth-api/public_key"))["key"]
        if public_key is not None:
            self.public_key = public_key
        if access_algorithm is not None:
            self.access_algorithm = access_algorithm


    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.scope["auth"] = False
        try:
            token = request.headers.get('Authorization', None)
            if token is None:
                self.logger.info('Authorization header is None')
                request.scope["user"] = RequestUser(name="NotAuthenticated", email="", scopes=[])
                response = await call_next(request)
                return response
            try:
                payload = jwt.decode(token, self.public_key, algorithms=[self.access_algorithm])
            except Exception as e:
                self.logger.error(f'Error jwt.decode={traceback.format_exc()}')
                response = Response()
                response.status_code = fastapi_status.HTTP_403_FORBIDDEN
                response.body = json.dumps({"detail": str(e)}).encode()
                return response
            username: str = payload.get("name", "NoName")
            exp: datetime = datetime.fromtimestamp(payload.get("exp", 0))
            scopes = payload.get("scopes", [])
            email = payload.get("email")
            tenants = payload.get("tenants", [])
            properties = payload.get("properties", {})
            user = RequestUser(name=username, email=email, scopes=scopes, tenants=tenants, properties=properties)
            request.scope["user"] = user
            request.scope["auth"] = True
            response = await call_next(request)
        except Exception as e:
            request.scope["auth"] = False
            self.logger.error(f'Error = {traceback.format_exc()}')
            response = Response()
            response.body = json.dumps({"detail": traceback.format_exc()}).encode()
            response.status_code = fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR
        return response


