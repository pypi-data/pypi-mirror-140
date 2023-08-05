from taodata.util import client
from taodata.util import auth
if __name__ == '__main__':
    token = auth.get_token()
    api = client.DataApi(token=token)

