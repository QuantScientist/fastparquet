
import gzip
from .thrift_structures import parquet_thrift
# TODO: use stream/direct-to-buffer conversions instead of memcopy

# TODO: enable ability to pass kwargs to compressor

compressions = {
    'UNCOMPRESSED': lambda x: x
}
decompressions = {
    'UNCOMPRESSED': lambda x: x
}
try:
    compressions['GZIP'] = gzip.compress
    decompressions['GZIP'] = gzip.decompress
except AttributeError:
    # Python2.7
    def gzip_compress(data, compresslevel=9):
        from io import BytesIO
        bio = BytesIO()
        f = gzip.GzipFile(mode='wb',
                          compresslevel=compresslevel,
                          fileobj=bio)
        f.write(data)
        f.close()
        return bio.getvalue()
    def gzip_decompress(data):
        import zlib
        return zlib.decompress(data,
                               16+15)
    compressions['GZIP'] = gzip_compress
    decompressions['GZIP'] = gzip_decompress
try:
    import snappy
    compressions['SNAPPY'] = snappy.compress
    decompressions['SNAPPY'] = snappy.decompress
except ImportError:
    pass
try:
    import lzo
    compressions['LZO'] = lzo.compress
    decompressions['LZO'] = lzo.decompress
except ImportError:
    pass
try:
    import brotli
    compressions['BROTLI'] = brotli.compress
    decompressions['BROTLI'] = brotli.decompress
except ImportError:
    pass

compressions = {k.upper(): v for k, v in compressions.items()}
decompressions = {k.upper(): v for k, v in decompressions.items()}

rev_map = {getattr(parquet_thrift.CompressionCodec, key): key for key in
           dir(parquet_thrift.CompressionCodec) if key in compressions}


def compress_data(data, algorithm='gzip'):
    if isinstance(algorithm, int):
        algorithm = rev_map[algorithm]
    if algorithm.upper() not in compressions:
        raise RuntimeError("Compression '%s' not available.  Options: %s" %
                (algorithm, sorted(compressions)))
    return compressions[algorithm.upper()](data)


def decompress_data(data, algorithm='gzip'):
    if isinstance(algorithm, int):
        algorithm = rev_map[algorithm]
    if algorithm.upper() not in decompressions:
        raise RuntimeError("Decompression '%s' not available.  Options: %s" %
                (algorithm.upper(), sorted(decompressions)))
    return decompressions[algorithm.upper()](data)
