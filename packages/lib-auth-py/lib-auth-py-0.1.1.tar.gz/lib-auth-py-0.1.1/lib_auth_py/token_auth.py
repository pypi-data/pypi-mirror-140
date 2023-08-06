# from fastapi import Request, HTTPException
import math
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, Response, status, Depends
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jose.jwt as jwt
import secMgr
import os
import traceback as tb
import json
import datetime
import time
import os
from dotenv import load_dotenv

if os.path.exists('./lib-auth-py/.env'):
    load_dotenv()

def getSecret():
    # Get the JWT token secret
    try:
        env = os.environ.get('ECS_CLUSTER_NAME')
        secrets = secMgr.get_secret(env)#os.environ.get('ECS_CLUSTER_NAME'))
        secrets = json.loads(secrets)
        jwt_secret_token = secrets['JWT_TOKEN_SECRET']
        os.environ['JWT_TOKEN_SECRET'] = jwt_secret_token
        return jwt_secret_token
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        secrets = []
        return None
        raise


def decodeJWT(token):
    #TODO add expiration time as part of a json
    exp_time = 24*60*60

    jwt_secret_token = os.environ.get('JWT_TOKEN_SECRET') if os.environ.get('JWT_TOKEN_SECRET') is not None else getSecret()
    try:
        payload = jwt.decode(
            token,
            key=jwt_secret_token
        )
        return payload
        
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        return None
        raise
        # return None

def signJWT(userid, tenantId, userTypeId):
    #TODO add expiration time as part of a json
    exp_time = 24*60*60

    jwt_secret_token = os.environ.get('JWT_TOKEN_SECRET') if os.environ.get('JWT_TOKEN_SECRET') is not None else getSecret()

    iat = datetime.datetime.utcnow().timestamp() #datetime.datetime.now()
    exp = iat + +24*60*60
        # return jwt.sign({ name: userid, userid, tenantId, userTypeId, iat, exp }, JWT_TOKEN_SECRET)
    try:
        token = jwt.encode(
            {'id': userid, 'tenantId': tenantId, 'userTypeId': userTypeId, 'iat': iat, 'exp':exp },
            key=jwt_secret_token
        )
        return token
        
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
        exp_time = 24*60*60

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
            expiration = payload['exp'] if 'exp' in payload.keys() else 0
            if expiration == 0:
                if payload['iat']+exp_time>time.mktime(datetime.date.today().timetuple()):
                    isTokenValid = True
                else:
                    isTokenValid = False
                
            else:
                if datetime.datetime.fromtimestamp(expiration)>datetime.datetime.now():
                    isTokenValid = True
                else:
                    isTokenValid = False
            # isTokenValid = True
        else:
            isTokenValid = False
        return isTokenValid

if __name__ == '__main__':
    signJWT(1,'TEN0',None)        


# from fastapi import Request, HTTPException, Response, status, Depends
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# import jose.jwt as jwt
# import secMgr
# import os
# import traceback as tb
# import json
# import datetime
# import time

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def verify_token(token: str = Depends(oauth2_scheme)):#req: Request):#, response: Response):
#     # if 'authorization' in req.headers.keys():
#     #     token = req.headers["authorization"].split(' ')[1]
#     # else:
#     #     return False
#     #TODO add expiration time as part of a json
#     exp_time = 24*60*60

#     # Get the JWT token secret
#     try:
#         env = os.environ.get('ECS_CLUSTER_NAME')
#         secrets = secMgr.get_secret(env)#os.environ.get('ECS_CLUSTER_NAME'))
#         secrets = json.loads(secrets)
#         jwt_secret_token = secrets['JWT_TOKEN_SECRET']
#     except Exception as e:
#         print(str(e))
#         print(tb.format_exc())
#         secrets = []
#         return False

#     try:
#         payload = jwt.decode(
#             token,
#             key=jwt_secret_token
#         )
#         expiration = payload['exp'] if 'exp' in payload.keys() else 0
#         if expiration == 0:
#             if payload['iat']+exp_time>time.mktime(datetime.date.today().timetuple()):
#                 return True
#             else:
#                 return False
            
#         else:
#             if datetime(expiration)>datetime.now():
#                 return True
#             else:
#                 return False
#         return True
#     except Exception as e:
#         print(str(e))
#         print(tb.format_exc())
#         return False
    
