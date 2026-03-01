import numpy as np

def pack_embedding(vec: list[float]) -> tuple[bytes, int]:
    arr = np.array(vec, dtype=np.float32)
    return arr.tobytes(), int(arr.shape[0])

def unpack_embedding(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)