import taodata as td

if __name__ == '__main__':
    api = td.get_api('123456', 30)
    pd = api.query(api_name='api_name', fields='f1,f2,f3', arg1='a', arg2='b')
    print(pd)

