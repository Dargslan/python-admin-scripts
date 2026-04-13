"""
dargslan-dns-check — DNS Record Checker & Analyzer

Query and analyze DNS records for any domain.
Zero external dependencies — uses only Python standard library.

Homepage: https://dargslan.com
Books: https://dargslan.com/books
Blog: https://dargslan.com/blog
"""

__version__ = "1.0.0"
__author__ = "Dargslan"
__url__ = "https://dargslan.com"

import socket
import struct
import json
import random
import time


class DNSChecker:
    """Query and analyze DNS records for domains."""

    RECORD_TYPES = {
        'A': 1, 'NS': 2, 'CNAME': 5, 'SOA': 6, 'MX': 15,
        'TXT': 16, 'AAAA': 28,
    }

    def __init__(self, nameserver="8.8.8.8", timeout=5):
        self.nameserver = nameserver
        self.timeout = timeout

    def _build_query(self, domain, qtype):
        tid = random.randint(0, 65535)
        header = struct.pack('>HHHHHH', tid, 0x0100, 1, 0, 0, 0)
        question = b''
        for part in domain.encode().split(b'.'):
            question += bytes([len(part)]) + part
        question += b'\x00'
        question += struct.pack('>HH', qtype, 1)
        return header + question, tid

    def _parse_name(self, data, offset):
        labels = []
        jumped = False
        original_offset = offset
        while True:
            if offset >= len(data):
                break
            length = data[offset]
            if length == 0:
                offset += 1
                break
            if (length & 0xC0) == 0xC0:
                if not jumped:
                    original_offset = offset + 2
                pointer = struct.unpack('>H', data[offset:offset+2])[0] & 0x3FFF
                offset = pointer
                jumped = True
                continue
            offset += 1
            labels.append(data[offset:offset+length].decode(errors='replace'))
            offset += length
        return '.'.join(labels), original_offset if jumped else offset

    def _query_raw(self, domain, record_type):
        qtype = self.RECORD_TYPES.get(record_type.upper(), 1)
        packet, tid = self._build_query(domain, qtype)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            sock.sendto(packet, (self.nameserver, 53))
            response, _ = sock.recvfrom(4096)
        except socket.timeout:
            return []
        except Exception:
            return []
        finally:
            sock.close()

        if len(response) < 12:
            return []

        _, flags, qdcount, ancount, _, _ = struct.unpack('>HHHHHH', response[:12])
        offset = 12

        for _ in range(qdcount):
            _, offset = self._parse_name(response, offset)
            offset += 4

        records = []
        for _ in range(ancount):
            name, offset = self._parse_name(response, offset)
            if offset + 10 > len(response):
                break
            rtype, rclass, ttl, rdlength = struct.unpack('>HHIH', response[offset:offset+10])
            offset += 10
            rdata = response[offset:offset+rdlength]
            offset += rdlength

            record = {'name': name, 'type': record_type.upper(), 'ttl': ttl}

            if rtype == 1 and len(rdata) == 4:
                record['value'] = socket.inet_ntoa(rdata)
            elif rtype == 28 and len(rdata) == 16:
                record['value'] = socket.inet_ntop(socket.AF_INET6, rdata)
            elif rtype == 15 and len(rdata) >= 3:
                priority = struct.unpack('>H', rdata[:2])[0]
                mx_name, _ = self._parse_name(response, offset - rdlength + 2)
                record['value'] = mx_name
                record['priority'] = priority
            elif rtype == 2 or rtype == 5:
                ns_name, _ = self._parse_name(response, offset - rdlength)
                record['value'] = ns_name
            elif rtype == 16:
                txt = b''
                pos = 0
                while pos < len(rdata):
                    tlen = rdata[pos]
                    txt += rdata[pos+1:pos+1+tlen]
                    pos += 1 + tlen
                record['value'] = txt.decode(errors='replace')
            elif rtype == 6:
                mname, pos = self._parse_name(response, offset - rdlength)
                rname, pos = self._parse_name(response, pos)
                if pos + 20 <= len(response):
                    serial, refresh, retry, expire, minimum = struct.unpack('>IIIII', response[pos:pos+20])
                    record['value'] = f"{mname} {rname} {serial}"
                    record['serial'] = serial
                    record['primary_ns'] = mname
                    record['admin'] = rname
            else:
                record['value'] = rdata.hex()

            records.append(record)

        return records

    def query(self, domain, record_type='A'):
        """Query DNS records for a domain."""
        return self._query_raw(domain, record_type)

    def query_all(self, domain):
        """Query all common DNS record types for a domain."""
        result = {}
        for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']:
            records = self._query_raw(domain, rtype)
            if records:
                result[rtype] = records
        return result

    def reverse_lookup(self, ip):
        """Perform reverse DNS lookup."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return {'ip': ip, 'hostname': hostname}
        except socket.herror:
            return {'ip': ip, 'hostname': None, 'error': 'No PTR record'}
        except Exception as e:
            return {'ip': ip, 'hostname': None, 'error': str(e)}

    def check_propagation(self, domain, record_type='A', nameservers=None):
        """Check DNS propagation across multiple nameservers."""
        if nameservers is None:
            nameservers = ['8.8.8.8', '1.1.1.1', '208.67.222.222', '9.9.9.9']

        results = []
        for ns in nameservers:
            checker = DNSChecker(nameserver=ns, timeout=self.timeout)
            records = checker.query(domain, record_type)
            values = [r.get('value', '') for r in records]
            results.append({'nameserver': ns, 'records': records, 'values': values})
        return results

    def print_report(self, domain):
        """Print a formatted DNS report."""
        all_records = self.query_all(domain)

        print(f"\n{'='*60}")
        print(f"  DNS Report: {domain}")
        print(f"{'='*60}")

        for rtype, records in all_records.items():
            print(f"\n  {rtype} Records:")
            for r in records:
                extra = f" (priority: {r['priority']})" if 'priority' in r else ""
                extra += f" (TTL: {r['ttl']}s)" if r.get('ttl') else ""
                print(f"    {r.get('value', 'N/A')}{extra}")

        print(f"\n{'='*60}")
        print(f"  More tools: https://dargslan.com")
        print(f"  eBooks: https://dargslan.com/books")
        print(f"{'='*60}\n")

    def to_json(self, domain):
        """Return all DNS records as JSON."""
        return json.dumps(self.query_all(domain), indent=2, default=str)


__all__ = ["DNSChecker"]
