import time

import pinecone
import uuid
import numpy as np
import random
import sys
import pytest
from pinecone_nuts.utils import vs_adapter
import pinecone
from loguru import logger
from pinecone import QueryVector, Vector, Index, PineconeProtocolError, ApiKeyError, ApiException
from pinecone.core.client import Configuration
# from pinecone.core.client.model.upsert_response import UpsertResponse
# from pinecone import QueryVector
from pinecone.core.grpc.index_grpc import GRPCIndex, GRPCVector, GRPCQueryVector
from pinecone.core.grpc.protos import vector_column_service_pb2
from pinecone.core.utils import dump_numpy_public, dict_to_proto_struct
from pinecone.core.grpc.protos import vector_service_pb2
import cProfile, pstats
from pinecone.core.grpc.protos.vector_column_service_pb2 import NdArray
from google.protobuf.struct_pb2 import Struct

from google.protobuf import json_format
from munch import munchify
import pandas as pd
from pandas import DataFrame


# from tests.integration.utils import retry_assert


def test_cl_alpha():
    # pinecone.init(api_key='Jr50Ro7YGGIvRFP8WNEdnNiuLmYpvqdO', environment='internal-alpha')
    # pinecone.init(api_key='2c80b666-82a2-4e24-abd1-15fa467c770c', environment='us-west1-gcp')
    pinecone.init(api_key='7e9bf571-48f5-46c0-8a0f-7069a05ee926', environment='internal-alpha')
    # pinecone.init(api_key='su6f5TsLCvpiIs6PiCxBzbxQmVfvotCT', environment='hirad-dev-gcp')
    # cmp_filter = {"$and": [{"field": {"$eq": "match"}}, {"field": {"$nin": ['v1', 'v2', 'v3']}}]}
    # pinecone.init(api_key='QBSLhAlYRsQA48ydU6iT0VAQnjw4MVCX', environment='dev-yarden')
    for index in pinecone.list_indexes():
        pinecone.delete_index(index)


def test_pods_pod_type():
    # pinecone.init(api_key='QBSLhAlYRsQA48ydU6iT0VAQnjw4MVCX', environment='dev-yarden')
    name = 'ns-test'
    # pinecone.init(api_key='7e9bf571-48f5-46c0-8a0f-7069a05ee926', environment='internal-alpha')
    pinecone.init(api_key='a02452e1-75e1-4237-92ff-c595cd76c825', environment='us-west1-gcp')
    print(pinecone.list_indexes())
    # pinecone.delete_index(name)
    # pinecone.create_index(name=name, dimension=128, shards=1)
    index = GRPCIndex('ns-test')

    # print(index.describe_index_stats())
    #
    n = 1000
    vecs = [np.random.rand(128).tolist() for i in range(n)]
    ids = [str(i) + ' ' + str(i) for i in range(n)]
    ids = ['PP 3465'] * n
    meta = [{'yo lo': 1, 'yelo': 2, 'oloy': 3} for i in range(n)]
    data = tuple(zip(ids, vecs, meta))
    batch = 200

    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    res = []
    # for chunk in chunker(data, batch):
    #     res.append(index.upsert(vectors=chunk, async_req=False, namespace='ns2'))
    # for chunk in chunker(data, batch):
    #     res.append(index.upsert(vectors=chunk, async_req=False, namespace='ns2'))
    # for chunk in chunker(data, batch):
    #     res.append(index.upsert(vectors=chunk, async_req=False, namespace='ns3'))
    #
    # print(index.describe_index_stats())
    #
    # res = index.fetch(ids=ids, namespace='ns2')
    # print(res)

    # # index.delete(ids=['1'], namespace='ns2', delete_all=True)
    #
    print(index.describe_index_stats())


def test_gong_size():
    # df = pd.read_parquet('/Users/rajat/Downloads/gong.parquet', engine='pyarrow')
    # df = df[:10000]
    # df.to_parquet('gong_small.parquet',engine='pyarrow')
    pinecone.init(api_key='076a7136-9e84-45d0-b802-bd33861c5dc8', environment='gong-poc-us-east1-gcp')
    # pinecone.delete_index('upsert-billion-bert')
    # pinecone.create_index('upsert-billion-bert', 768, shards=250,
    #                       index_config={"hybrid": True, "deduplicate": True, "k_bits": 1024})
    for i in range(10):
        index = pinecone.GRPCIndex('test-{}'.format(i))
        ds = index.describe_index_stats().namespaces
        vc = 0
        # print(ds)
        for ns in ds:
            # print(ds[ns]['vector_count'])
            vc += ds[ns]['vector_count']
        print(vc)
        print(len(ds))


def test_delete_all():
    pinecone.init(api_key='2c80b666-82a2-4e24-abd1-15fa467c770c', environment='us-west1-gcp')
    index = pinecone.Index('test')
    index2 = pinecone.Index('rajat')
    print(index.describe_index_stats())
    # index.delete(delete_all=True, namespace='smt')
    print(index2.describe_index_stats())
    # print(index.fetch(ids=['1'],namespace='sm'))
    # print(index.fetch(ids=['1'], namespace='sm2'))
    # print(index.fetch(ids=['1'], namespace='smt'))


def test_ch():
    api_key = "2ba52061-3976-43b2-ab04-92b1bdb63ba8"
    pinecone.init(api_key=api_key, environment='us-west1-gcp')
    index_name = "v2index150s1"
    index = pinecone.Index(index_name=index_name)
    rvec = [0.1] * 768
    print(index.describe_index_stats())
    print(pinecone.describe_index(index_name))
    # index.query(queries=[rvec]*100,top_k=20)


def test_customer():
    # pinecone.init(api_key='e5a254ec-fe3d-49c0-9479-85774003d170', environment='us-west1-gcp')
    # ydc
    pinecone.init(api_key='d3767b7f-13d5-4560-b539-0a5418bbbab6', environment='us-west1-gcp')
    # two
    # pinecone.init(api_key='7c64c130-f379-4104-a29f-c3f372db69a2', environment='us-west1-gcp')
    # hello retail
    # pinecone.init(api_key='9757ae30-835c-461a-9e97-1afa19d26c32')
    # print(pinecone.list_indexes())
    index = GRPCIndex('ydc-pinecone')
    # n = 2
    # vecs = [np.random.rand(768).tolist() for i in range(n)]
    # ids = [str(i)*512 for i in range(n)]
    # print(ids)
    # qvec = [0.1] * 768
    # print(vecs)
    # data = tuple(zip(ids, vecs))
    # # index.upsert(vectors=data)
    # # pinecone.
    # index.delete(ids=ids)
    # qr = index.query(queries=[[0.1] * 768], top_k=10, include_metadata=True,namespace='example')
    # print(qr)
    # for i in range(4000):
    #     # if i % 500 == 0:
    #     #     time.sleep(1)
    # index = pinecone.GRPCIndex('test-{}'.format(i))
    ds = index.describe_index_stats().namespaces
    vc = 0
    # print(ds)
    for ns in ds:
        # print(ds[ns]['vector_count'])
        vc += ds[ns]['vector_count']
    print(vc)
    print(len(ds))
    # print(pinecone.describe_index('ion-vectors'))


def test_size():
    pinecone.init(api_key='a02452e1-75e1-4237-92ff-c595cd76c825', environment='us-west1-gcp')
    index = pinecone.GRPCIndex('stuff')
    print(index.describe_index_stats())


def test_grpc():
    pinecone.init(api_key='a02452e1-75e1-4237-92ff-c595cd76c825', environment='us-west1-gcp')
    # pinecone.init(api_key='c26c4ff3-1423-4fc8-b3c9-5cc089baed71', environment='hirad-dev')
    # pinecone.init(api_key='ffca3f13-b041-4112-a6de-49b79b4e288c', environment='internal-beta-aws')

    # pinecone.init(api_key='7e9bf571-48f5-46c0-8a0f-7069a05ee926', environment='internal-alpha')
    # pinecone.init(api_key='a02452e1-75e1-4237-92ff-c595cd76c825', environment='us-west1-gcp')
    # pinecone.delete_index('test-sst')
    # pinecone.describe_index(lol='what')
    # pinecone.create_index('test', 512)
    # print(pinecone.list_indexes())
    # pinecone.scale_index('test-sst',300)
    index = Index('kafka-test')
    # pinecone.create_index(dil='heart')
    # pinecone.init(api_key='', environment='us-west1-gcp')
    # pinecone.init(api_key='', environment='us-west1-gcp')
    # pinecone.list_indexes()
    # index = Index('test')
    n = 1500
    vecs = [np.random.rand(768).tolist() for i in range(n)]
    ids = ['i'*512 for i in range(n)]
    meta = [{'yo lo': 1, 'yelo': 2, 'oloy': 3} for i in range(n)]
    data = tuple(zip(ids, vecs, meta))
    batch = 400

    # index = GRPCIndex('test')
    # print(index.describe_index_stats())
    # print(index.describe_index_stats())
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    #
    s = time.perf_counter()
    res = []
    for chunk in chunker(data, batch):
        index.upsert(vectors=chunk)
    # for chunk in chunker(data, batch):
    #     res.append(index.upsert(vectors=chunk, async_req=True, namespace='ns6'))

    # qvec = [0.1] * 512
    # filter = {'yelo':{'$eq':3}}
    # fr = index.fetch(ids=ids)
    # print(len(fr['vectors']))
    # res = index.query(queries=[qvec], namespace='ns', top_k=1000, include_values=True, include_metadata=True)
    # print(res)
    # rs = [r.result() for r in res]
    # e = time.perf_counter()
    # print(e - s)
    # print(async_results)
    # index.delete(ids=ids,namespace='ns')
    # index.fetch(ids=ids,namespace='ns')
    # print([async_result.result() for async_result in async_results])
    # for chunk in chunker(data, batch):
    #     # res = index.async_upsert(5,chunk)
    #     index.upsert(vectors=chunk)
    # from concurrent.futures import ThreadPoolExecutor
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     for chunk in chunker(data, batch):
    #         future_results = executor.submit(index.upsert, chunk)
    #     rset= future_results.result()
    # print(res)
    qr = index.query(queries=[[0.1] * 768], top_k=10, include_metadata=True)
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('tottime')
    # stats.print_stats()
    # index.describe_index_stats(lol=2)
    # index.fetch(ids=['0'], namespace='smtv')


def test_s():
    pinecone.init(api_key='9a1ca6b7-84e3-4669-b1d2-ce63a7cb8046', environment='us-west1-gcp')
    index = GRPCIndex('index-s1-1')
    # print(pinecone.list_indexes())
    # print(pinecone.describe_index('index-s1-1'))
    # print(index.describe_index_stats())
    qvec = [0.1] * 768
    res = index.query(queries=[qvec], top_k=10)
    print(res)
    n = 10
    vecs = [np.random.rand(768).tolist() for i in range(n)]
    ids = [str(uuid.uuid4()) for i in range(n)]
    data = tuple(zip(ids, vecs))
    index.upsert(vectors=data)


def test_delete():
    pinecone.init(api_key='2c80b666-82a2-4e24-abd1-15fa467c770c', environment='us-west1-gcp')
    # for index in pinecone.list_indexes():
    #     pinecone.delete_index(index)
    print(pinecone.whoami())
