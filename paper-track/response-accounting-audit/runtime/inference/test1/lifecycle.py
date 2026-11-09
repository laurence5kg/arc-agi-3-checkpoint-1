"""Notebook-global time budget and owned process cleanup, shared by all profiles."""
import os
import math
import contextlib
import signal
import socket
import subprocess
import threading
import time

_cleanup_lock = threading.Lock()
_bound_server = None
_server_responded = False


class ServingProcessExited(RuntimeError):
    pass


def bind_owned_server(process):
    global _bound_server,_server_responded
    _bound_server = process
    _server_responded = False


def mark_server_ready():
    global _server_responded
    if _bound_server is not None:
        _server_responded=True


def server_ready():
    return _bound_server is not None and _server_responded


class DeadlineExceeded(TimeoutError):
    pass


def remaining():
    value = os.environ.get('TEST1_PLAY_DEADLINE_EPOCH')
    if not value:
        return float('inf')
    deadline = float(value)
    if not math.isfinite(deadline):
        raise ValueError('gameplay deadline must be finite')
    return max(0.0, deadline-time.time())


def timeout(requested=900.0, minimum=5.0):
    if _bound_server is not None and _bound_server.poll() is not None:
        raise ServingProcessExited('Owned inference server exited; startup retries cannot recover it')
    boot_deadline=os.environ.get('TEST1_SERVER_BOOT_DEADLINE_EPOCH')
    if _bound_server is not None and not _server_responded and boot_deadline and time.time()>=float(boot_deadline):
        raise ServingProcessExited('Owned inference server exceeded its startup deadline without accepting a model request')
    requested = float(requested or 900.0)
    if not math.isfinite(requested):
        raise ValueError('request timeout must be finite')
    budget = remaining() - 2.0
    if budget < minimum:
        raise DeadlineExceeded('notebook gameplay deadline reached')
    selected = min(900.0, requested, budget)
    if selected < minimum:
        raise DeadlineExceeded('insufficient request time remains')
    return selected


def bounded_sleep(seconds):
    delay = max(0.0, float(seconds))
    if remaining() <= delay + 5.0:
        raise DeadlineExceeded('retry would exceed notebook gameplay deadline')
    time.sleep(delay)


@contextlib.contextmanager
def response_budget(response, request_deadline):
    """An absolute body deadline shared by JSON, errors, and SSE responses."""
    expired = threading.Event()
    def abort():
        expired.set()
        # requests/urllib3's public close alone may wait on a blocked reader.
        # Shutdown the *owned* socket first when the installed transport exposes it.
        try:
            sock = response.raw._fp.fp.raw._sock
            sock.shutdown(socket.SHUT_RDWR)
        except (AttributeError, OSError):
            pass
        try:
            response.close()
        except (OSError, ValueError):
            pass

    timer = threading.Timer(max(0.001, request_deadline - time.time()), abort)
    timer.daemon = True
    timer.start()
    try:
        yield expired
    except Exception as exc:
        if expired.is_set() or time.time() >= request_deadline:
            raise DeadlineExceeded('absolute response deadline reached') from exc
        raise
    finally:
        timer.cancel()
        response.close()


def cache_response_body(response, request_deadline, max_bytes=64*1024*1024):
    """Read a non-SSE response under a wall deadline and retain requests semantics."""
    chunks = []
    size = 0
    with response_budget(response, request_deadline) as expired:
        for chunk in response.iter_content(chunk_size=65536):
            if expired.is_set() or time.time() >= request_deadline or remaining() <= 2.0:
                raise DeadlineExceeded('absolute response deadline reached')
            size += len(chunk)
            if size > max_bytes:
                raise ValueError('inference response exceeds byte cap')
            chunks.append(chunk)
        if expired.is_set() or time.time() >= request_deadline:
            raise DeadlineExceeded('absolute response deadline reached')
        response._content = b''.join(chunks)
        response._content_consumed = True


def bounded_lines(response, request_deadline):
    """Close this response at its absolute deadline, including slow SSE streams."""
    with response_budget(response, request_deadline) as expired:
        for line in response.iter_lines(decode_unicode=False):
            if expired.is_set() or time.time() >= request_deadline or remaining() <= 2.0:
                raise DeadlineExceeded('absolute streaming request deadline reached')
            yield line
        if expired.is_set() or time.time() >= request_deadline:
            raise DeadlineExceeded('absolute streaming request deadline reached')


def stop_owned_process(process, grace=8.0):
    """Only the Popen handle created by this notebook is eligible for cleanup."""
    if process is None:
        return
    with _cleanup_lock:
        if getattr(process, '_test1_cleanup_done', False):
            return
        process._test1_cleanup_done = True
    if process.poll() is not None:
        # The session leader can exit before its GPU workers. The retained
        # handle owns the original process group; never rediscover a PID by name.
        if os.name == 'posix':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
        return
    try:
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        process.wait(timeout=grace)
    except (ProcessLookupError, OSError):
        return
    except subprocess.TimeoutExpired:
        try:
            if os.name == 'posix':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait(timeout=2.0)
        except (ProcessLookupError, OSError, subprocess.TimeoutExpired):
            pass
    finally:
        # Waiting for the leader alone does not prove GPU workers exited.
        # Kill any surviving members of this notebook's original session group.
        if os.name == 'posix':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
