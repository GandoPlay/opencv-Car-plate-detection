import pickle
import struct
import time
import cv2
import numpy

HEADERSIZE = 10
CLIENT_BUFFER = 16
BUFFER_SIZE = 4096
payload_size = struct.calcsize(">L")


def send_cv2_image_as_png(img, socket):
    """
    Send the Client in a png Image.
    :param socket: socket
    :param img: The image
    :return:
    """
    t = time.time()
    encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 90]
    frame = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    result, frame = cv2.imencode('.png', frame, encode_param)
    data = pickle.dumps(frame, 0)
    size = len(data)
    socket.sendall(struct.pack(">L", size) + data)
    print('time to send', time.time() - t)


def receive_large_data(data, size, socket):
    while len(data) < size:
        data += socket.recv(BUFFER_SIZE)
    return data


def extract_image(data, socket):
    """
    Convert the giving data to an image.
    :param data:
    :param socket: socket
    :return:
    """
    t = time.time()
    data = receive_large_data(data, payload_size, socket)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    data = receive_large_data(data, msg_size, socket)
    print('time to recv', time.time() - t)

    frame_data = data[:msg_size]
    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")

    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    return frame


def create_msg_with_header(simple_msg):
    simple_msg = f'{len(simple_msg) :<{HEADERSIZE}}' + simple_msg
    return simple_msg


def decode_data(m):
    return m.decode("utf-8")[HEADERSIZE:]


def recive_msg_header(sock):
    full_msg = ""
    new_msg = True
    while True:
        msg = sock.recv(CLIENT_BUFFER)
        if len(msg) == 0:
            return None
        if new_msg:
            msglen = int(msg[:HEADERSIZE])
            new_msg = False
        full_msg += msg.decode("utf-8")

        if len(full_msg) - HEADERSIZE == msglen:
            return full_msg[HEADERSIZE:]
