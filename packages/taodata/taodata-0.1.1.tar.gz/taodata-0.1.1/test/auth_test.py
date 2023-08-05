from taodata.util import auth

if __name__ == '__main__':
    token = '123456'
    auth.set_token(token)
    local_token = auth.get_token()
    if token == local_token:
        print('it is passed!')
    else:
        print('it is failed!')
