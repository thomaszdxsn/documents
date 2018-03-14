import botocore.session
import botocore.config

cfg = botocore.config.Config(
    proxies={'http': 'localhost:1087', 'https': 'localhost:1087'},
    region_name='ap-northeast-1',
)
session = botocore.session.get_session()
client = session.create_client('s3', config=cfg)

def test_list_buckets():
    result = client.list_buckets()
    return result


def test_head_bucket():
    result = client.head_bucket(Bucket='dquant1')
    return result


def test_head_object():
    result = client.head_object(
        Bucket='dquant1',
        Key='123'
    )
    return result


def test_put_object():
    result = client.put_object(
        Body=b'tests',
        Bucket='dquant1',
        Key='123'
    )
    return result

def test_list_objects():
    result = client.list_objects_v2(
        Bucket='dquant1'
    )
    return result

def test_delete_objects():
    list_result = test_list_objects()
    result = client.delete_objects(
        Bucket='dquant1',
        Delete={
            'Objects': [
                {'Key': item['Key']}
                for item in list_result['Contents']
            ]
        }
    )
    return result


def test_get_object():
    response = client.get_object(
        Bucket='dquant1',
        Key='binance_depth/btcusdt/2018-02-26/part1.csv.gz'
    )
    with open('test.csv.gz', 'wb') as f:
        f.write(response['Body'].read())


if __name__ == '__main__':
    # print('test_list_buckets: ', test_list_buckets(), end='\n\n')
    # print('test_head_bucket: ', test_head_bucket(), end='\n\n')
    # print('test_put_object: ', test_put_object(), end='\n\n')
    # print('test_list_objects: ', test_list_objects(), end='\n\n')
    # print('test_head_object: ', test_head_object(), end='\n\n')
    # print('test_delete_objects: ', test_delete_objects(), end='\n\n')
    # test_get_object()