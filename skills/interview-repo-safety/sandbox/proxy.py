#!/usr/bin/env python3
"""Default-deny HTTP/HTTPS (CONNECT) proxy for Phase 2.

Environment:
  ALLOW   comma-separated hostnames (exact match, case-insensitive)
  LISTEN  bind address, default 0.0.0.0:8888

Logs one line per decision:
  ALLOW CONNECT host:port
  ALLOW HTTP METHOD host:port path
  TRANSFER CONNECT host:port bytes=N
  BLOCKED egress: host:port
"""
from __future__ import annotations

import os
import select
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


def allowlist():
    raw = os.environ.get("ALLOW", "registry.npmjs.org")
    return {h.strip().lower().rstrip(".") for h in raw.split(",") if h.strip()}


ALLOWED = allowlist()
LISTEN = os.environ.get("LISTEN", "0.0.0.0:8888")


def host_of(authority: str) -> tuple[str, int]:
    authority = authority.strip()
    if authority.startswith("[") and "]" in authority:
        host, _, rest = authority[1:].partition("]")
        port = int(rest[1:]) if rest.startswith(":") and rest[1:] else 443
        return host.lower().rstrip("."), port
    if ":" in authority:
        host, _, port_s = authority.rpartition(":")
        try:
            return host.lower().rstrip("."), int(port_s)
        except ValueError:
            return authority.lower().rstrip("."), 0
    return authority.lower().rstrip("."), 0


def permitted(host: str) -> bool:
    return host.lower().rstrip(".") in ALLOWED


def log(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    timeout = 30

    def log_message(self, fmt: str, *args) -> None:
        return

    def _deny(self, host: str, port: int) -> None:
        target = f"{host}:{port}" if port else host
        log(f"BLOCKED egress: {target}")
        try:
            self.send_response(403, "Forbidden")
            self.send_header("Content-Type", "text/plain")
            body = f"BLOCKED egress: {target}\n"
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
        except OSError:
            pass

    def do_CONNECT(self) -> None:
        host, port = host_of(self.path)
        port = port or 443
        if not permitted(host):
            self._deny(host, port)
            return
        log(f"ALLOW CONNECT {host}:{port}")
        try:
            remote = socket.create_connection((host, port), timeout=30)
        except OSError as exc:
            log(f"ALLOW CONNECT {host}:{port} connect-failed {exc}")
            self.send_error(502, "Bad Gateway")
            return
        try:
            self.send_response(200, "Connection Established")
            self.send_header("Connection", "close")
            self.end_headers()
        except OSError:
            remote.close()
            return
        transferred = 0
        try:
            transferred = tunnel(self.connection, remote)
        finally:
            try:
                remote.close()
            except OSError:
                pass
            log(f"TRANSFER CONNECT {host}:{port} bytes={transferred}")

    def do_HTTP(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.scheme and parsed.netloc:
            host, port = host_of(parsed.netloc)
            path = parsed.path or "/"
            if parsed.query:
                path = f"{path}?{parsed.query}"
            if not port:
                port = 443 if parsed.scheme == "https" else 80
        else:
            raw = self.headers.get("Host", "")
            host, port = host_of(raw)
            path = self.path or "/"
            if not port:
                port = 80
        if not permitted(host):
            self._deny(host, port)
            return
        log(f"ALLOW HTTP {self.command} {host}:{port} {path}")
        try:
            remote = socket.create_connection((host, port), timeout=30)
        except OSError as exc:
            log(f"ALLOW HTTP {host}:{port} connect-failed {exc}")
            self.send_error(502, "Bad Gateway")
            return
        try:
            req = f"{self.command} {path} HTTP/1.1\r\n"
            req += f"Host: {host if not port or port in (80, 443) else f'{host}:{port}'}\r\n"
            req += "Connection: close\r\n"
            skip = {"host", "proxy-connection", "connection"}
            for key, value in self.headers.items():
                if key.lower() in skip:
                    continue
                req += f"{key}: {value}\r\n"
            req += "\r\n"
            remote.sendall(req.encode("utf-8", "surrogateescape"))
            length = int(self.headers.get("Content-Length", "0") or "0")
            remaining = length
            while remaining > 0:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                remote.sendall(chunk)
                remaining -= len(chunk)
            while True:
                data = remote.recv(65536)
                if not data:
                    break
                self.wfile.write(data)
            self.wfile.flush()
        except OSError:
            pass
        finally:
            try:
                remote.close()
            except OSError:
                pass

    def do_GET(self) -> None:
        self.do_HTTP()

    def do_POST(self) -> None:
        self.do_HTTP()

    def do_HEAD(self) -> None:
        self.do_HTTP()

    def do_PUT(self) -> None:
        self.do_HTTP()

    def do_DELETE(self) -> None:
        self.do_HTTP()

    def do_PATCH(self) -> None:
        self.do_HTTP()

    def do_OPTIONS(self) -> None:
        self.do_HTTP()


def tunnel(client: socket.socket, remote: socket.socket) -> int:
    transferred = 0
    client.setblocking(False)
    remote.setblocking(False)
    sockets = [client, remote]
    while sockets:
        readable, _, errored = select.select(sockets, [], sockets, 60)
        if errored:
            break
        if not readable:
            break
        for sock in readable:
            other = remote if sock is client else client
            try:
                data = sock.recv(65536)
            except OSError:
                return transferred
            if not data:
                return transferred
            try:
                other.sendall(data)
            except OSError:
                return transferred
            transferred += len(data)
    return transferred


def main() -> None:
    host, port_s = LISTEN.rsplit(":", 1)
    port = int(port_s)
    log(f"proxy listen={LISTEN} allow={','.join(sorted(ALLOWED))}")
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.allow_reuse_address = True
    httpd.daemon_threads = True
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
