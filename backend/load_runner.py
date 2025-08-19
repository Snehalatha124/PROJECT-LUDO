import asyncio
import aiohttp
import time
from datetime import datetime
from statistics import median
from typing import Any, Dict, List, Optional, Callable


class HTTPLoadRunner:
    """
    Async HTTP load runner with precise TPS pacing and optional ramp-up.

    Config schema (subset):
      - url, method, headers, params, body, bodyType
      - auth: { type: 'basic'|'bearer', username, password, token }
      - users: max concurrent requests (semaphore)
      - target_tps: desired transactions per second (float)
      - duration_seconds: total run time
      - ramp_up_seconds: time to ramp from 0 to target TPS
      - loop_count: optional, number of iterations to send instead of duration-based

    Emits periodic updates via on_tick callback and returns final results.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        on_tick: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_sample: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.config = config
        self.on_tick = on_tick
        self.on_sample = on_sample

        self.start_time = time.time()
        self.stop_requested = False

        self.total = 0
        self.passed = 0
        self.failed = 0
        self.latencies: List[float] = []
        self.codes: Dict[str, int] = {}
        self.errors: List[Dict[str, Any]] = []
        self.samples: List[Dict[str, Any]] = []
        self.timeseries: List[Dict[str, Any]] = []
        self.per_second_count: Dict[int, int] = {}
        self.per_second_rt_sum: Dict[int, float] = {}

    async def _send_one(self, session: aiohttp.ClientSession, req_id: int) -> None:
        url = self.config.get('url')
        method = (self.config.get('method') or 'GET').upper()
        headers = self.config.get('headers') or {}
        params = self.config.get('params') or {}
        body = self.config.get('body')
        body_type = (self.config.get('bodyType') or 'raw').lower()

        data = None
        json_data = None
        if method in ('POST', 'PUT', 'PATCH') and body is not None:
            if body_type == 'json':
                json_data = body
                headers.setdefault('Content-Type', 'application/json')
            elif body_type == 'form' and isinstance(body, dict):
                data = body
            else:
                data = str(body)

        ts_ms = int(time.time() * 1000)
        t0 = time.perf_counter()
        status = 0
        ok = False
        resp_text_preview = None
        try:
            async with session.request(method, url, headers=headers, params=params, data=data, json=json_data) as resp:
                status = resp.status
                # lightweight preview: up to 4KB
                resp_text_preview = await resp.text(encoding='utf-8', errors='ignore')
                if len(resp_text_preview) > 4096:
                    resp_text_preview = resp_text_preview[:4096]
                ok = 200 <= status < 400
        except Exception as e:
            status = 0
            resp_text_preview = str(e)
            ok = False

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # aggregate
        self.total += 1
        self.latencies.append(elapsed_ms)
        self.codes[str(status)] = self.codes.get(str(status), 0) + 1
        if ok:
            self.passed += 1
        else:
            self.failed += 1
            if len(self.errors) < 200:
                self.errors.append({
                    'time': ts_ms,
                    'code': status,
                    'message': resp_text_preview or ''
                })

        # per-second aggregates
        sec_bucket = int(ts_ms // 1000)
        self.per_second_count[sec_bucket] = self.per_second_count.get(sec_bucket, 0) + 1
        self.per_second_rt_sum[sec_bucket] = self.per_second_rt_sum.get(sec_bucket, 0.0) + elapsed_ms

        # sample log (cap to 500)
        if len(self.samples) < 500:
            self.samples.append({
                'timestamp': ts_ms,
                'status': status,
                'ok': ok,
                'responseTime': elapsed_ms,
            })

        if self.on_sample:
            self.on_sample({
                'timestamp': ts_ms,
                'status': status,
                'responseTime': elapsed_ms,
                'ok': ok,
            })

    async def _runner(self) -> Dict[str, Any]:
        # auth
        auth_cfg = (self.config.get('auth') or {})
        auth = None
        headers = self.config.get('headers') or {}
        if auth_cfg.get('type') == 'basic':
            auth = aiohttp.BasicAuth(auth_cfg.get('username', ''), auth_cfg.get('password', ''))
        elif auth_cfg.get('type') == 'bearer':
            headers = dict(headers)
            headers.setdefault('Authorization', f"Bearer {auth_cfg.get('token', '')}")

        duration = int(self.config.get('duration_seconds') or self.config.get('duration') or 60)
        ramp_up = int(self.config.get('ramp_up_seconds') or self.config.get('ramp_up') or 0)
        target_tps = float(self.config.get('target_tps') or self.config.get('tps') or 0)
        loop_count = self.config.get('loop_count')
        max_concurrency = max(1, int(self.config.get('users') or 50))

        connector = aiohttp.TCPConnector(limit=max_concurrency)
        sem = asyncio.Semaphore(max_concurrency)
        start = time.time()

        async with aiohttp.ClientSession(auth=auth, connector=connector) as session:
            # background ticker for on_tick and timeseries
            async def tick_task():
                while not self.stop_requested:
                    await asyncio.sleep(1)
                    now_sec = int(time.time())
                    cnt = self.per_second_count.get(now_sec, 0)
                    rt_avg = 0.0
                    if cnt > 0:
                        rt_avg = self.per_second_rt_sum.get(now_sec, 0.0) / cnt
                    self.timeseries.append({
                        'second': now_sec,
                        'requestsPerSecond': cnt,
                        'avgResponseTime': rt_avg
                    })
                    if self.on_tick:
                        self.on_tick({
                            'total': self.total,
                            'passed': self.passed,
                            'failed': self.failed,
                            'rps': cnt,
                            'avgResponseTime': rt_avg,
                            'elapsed': time.time() - start
                        })

            ticker = asyncio.create_task(tick_task())

            async def schedule_by_duration():
                # Producer loop pacing TPS
                next_at = time.perf_counter()
                sent = 0
                while (time.time() - start) < duration and not self.stop_requested:
                    # compute current TPS with ramp-up
                    elapsed = time.time() - start
                    if ramp_up > 0 and elapsed < ramp_up:
                        current_tps = target_tps * (elapsed / ramp_up)
                    else:
                        current_tps = target_tps
                    # if target_tps is 0, just fire as fast as allowed by concurrency
                    interval = 0.0 if current_tps <= 0 else (1.0 / current_tps)

                    # schedule one request
                    await sem.acquire()
                    asyncio.create_task(self._task_wrapper(session, sem, sent))
                    sent += 1

                    # sleep until next slot
                    if interval > 0:
                        next_at += interval
                        delay = max(0.0, next_at - time.perf_counter())
                        if delay:
                            await asyncio.sleep(delay)
                    else:
                        await asyncio.sleep(0)

            async def schedule_by_iterations(total_requests: int):
                next_at = time.perf_counter()
                for i in range(total_requests):
                    if self.stop_requested:
                        break
                    # TPS pacing
                    interval = 0.0 if target_tps <= 0 else (1.0 / target_tps)
                    await sem.acquire()
                    asyncio.create_task(self._task_wrapper(session, sem, i))
                    if interval > 0:
                        next_at += interval
                        delay = max(0.0, next_at - time.perf_counter())
                        if delay:
                            await asyncio.sleep(delay)
                    else:
                        await asyncio.sleep(0)

            if loop_count is not None:
                await schedule_by_iterations(int(loop_count))
            else:
                await schedule_by_duration()

            # wait for in-flight tasks to finish
            await asyncio.sleep(0)  # yield
            while sem._value < max_concurrency:
                await asyncio.sleep(0.01)

            self.stop_requested = True
            ticker.cancel()
            try:
                await ticker
            except Exception:
                pass

        return self._finalize(start)

    async def _task_wrapper(self, session: aiohttp.ClientSession, sem: asyncio.Semaphore, req_id: int):
        try:
            await self._send_one(session, req_id)
        finally:
            sem.release()

    def _finalize(self, start_ts: float) -> Dict[str, Any]:
        lat = sorted(self.latencies) if self.latencies else []
        p95 = lat[int(0.95 * (len(lat) - 1))] if lat else 0
        avg = (sum(self.latencies) / len(self.latencies)) if self.latencies else 0
        achieved_tps = 0
        duration = max(0.001, time.time() - start_ts)
        if self.total:
            achieved_tps = self.total / duration
        return {
            'totalRequests': self.total,
            'successfulRequests': self.passed,
            'failedRequests': self.failed,
            'successRate': (self.passed / self.total * 100) if self.total else 0,
            'avgResponseTime': avg,
            'percentile95': p95,
            'peakRPS': max((p['requestsPerSecond'] for p in self.timeseries), default=achieved_tps),
            'requestsPerSecond': achieved_tps,
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'codes': self.codes,
            'errors': self.errors,
            'samples': self.samples,
            'timeseries': self.timeseries,
        }

    def run(self) -> Dict[str, Any]:
        return asyncio.run(self._runner())


