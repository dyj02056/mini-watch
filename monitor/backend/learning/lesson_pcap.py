"""Create a small educational PCAP and compare the first 5 seconds with 1 second.

Only Python's standard library is used. The generated packets are synthetic UDP
frames and are not captures from the bulletin board or from a live interface.
"""
import argparse
import json
import os
import struct
import tempfile


OFFSETS = (0.1, 0.5, 1.2, 2.5, 4.8, 5.2)
PAYLOADS = (b"a", b"bb", b"ccc", b"dddd", b"eeeee", b"ffffff")
BASE_TS = 1_700_000_000


def synthetic_frame(index, payload):
    destination = bytes.fromhex("020000000002")
    source = bytes.fromhex("020000000001")
    ethernet = destination + source + struct.pack("!H", 0x0800)
    udp_length = 8 + len(payload)
    total_length = 20 + udp_length
    ip_without_checksum = struct.pack(
        "!BBHHHBBH4s4s", 0x45, 0, total_length, index + 1, 0, 64, 17, 0,
        bytes((192, 0, 2, index + 1)), bytes((198, 51, 100, 1)),
    )
    words = struct.unpack("!10H", ip_without_checksum)
    checksum_sum = sum(words)
    checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)
    checksum = (~checksum_sum) & 0xFFFF
    ip_header = ip_without_checksum[:10] + struct.pack("!H", checksum) + ip_without_checksum[12:]
    udp_header = struct.pack("!HHHH", 10000 + index, 9000, udp_length, 0)
    return ethernet + ip_header + udp_header + payload


def write_demo_pcap(path):
    with open(path, "wb") as stream:
        stream.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for index, (offset, payload) in enumerate(zip(OFFSETS, PAYLOADS)):
            frame = synthetic_frame(index, payload)
            seconds = int(BASE_TS + offset)
            microseconds = int((offset % 1) * 1_000_000)
            stream.write(struct.pack("<IIII", seconds, microseconds, len(frame), len(frame)))
            stream.write(frame)


def read_window(path, window_seconds):
    selected_count = 0
    byte_sum = 0
    with open(path, "rb") as stream:
        header = stream.read(24)
        if len(header) != 24:
            raise ValueError("PCAP global header is incomplete")
        magic = header[:4]
        if magic == bytes.fromhex("d4c3b2a1"):
            endian = "<"
        elif magic == bytes.fromhex("a1b2c3d4"):
            endian = ">"
        else:
            raise ValueError("Unsupported PCAP magic number")
        first_timestamp = None
        while True:
            record = stream.read(16)
            if not record:
                break
            if len(record) != 16:
                raise ValueError("PCAP packet header is incomplete")
            seconds, micros, captured_length, _original_length = struct.unpack(endian + "IIII", record)
            packet = stream.read(captured_length)
            if len(packet) != captured_length:
                raise ValueError("PCAP packet data is incomplete")
            timestamp = seconds + micros / 1_000_000
            if first_timestamp is None:
                first_timestamp = timestamp
            if timestamp - first_timestamp < window_seconds:
                selected_count += 1
                byte_sum += captured_length
    return {"window_seconds": window_seconds, "packet_count": selected_count, "captured_bytes": byte_sum}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", choices=("1", "5", "compare"), default="compare")
    args = parser.parse_args()
    with tempfile.NamedTemporaryFile(prefix="education-", suffix=".pcap", delete=False) as temp:
        pcap_path = temp.name
    try:
        write_demo_pcap(pcap_path)
        if args.window == "compare":
            results = [read_window(pcap_path, seconds) for seconds in (5, 1)]
        else:
            results = [read_window(pcap_path, int(args.window))]
        print(json.dumps({"pcap": "synthetic educational UDP frames", "live_capture": False, "results": results}, indent=2))
    finally:
        os.unlink(pcap_path)


if __name__ == "__main__":
    main()
