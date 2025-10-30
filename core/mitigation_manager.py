# core/mitigation_manager.py
import asyncio
import time
import logging
from collections import deque

import config
from .geoip_manager import GeoIPManager

logger = logging.getLogger("ddos-preventer")

class TokenBucket:
    """Her bir IP adresi için hız limitini (rate limiting) uygular."""
    def __init__(self, rate, capacity):
        self.rate = float(rate)
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.last = time.time()

    def consume(self, amount=1.0):
        """Kovadan bir jeton harcamayı dener. Başarılı olursa True döner."""
        now = time.time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

class MitigationManager:
    """
    Tüm gelen bağlantılar için DDoS koruma mantığını merkezi olarak yöneten singleton sınıfı.
    IP bazlı rate limit, bağlantı limiti, kara liste ve Geo-blocking uygular.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MitigationManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'): return
        self._initialized = True
        
        logger.info("Merkezi Koruma Yöneticisi (MitigationManager) başlatılıyor...")
        self.rate = int(config.DEFAULT_RATE)
        self.burst = int(config.DEFAULT_BURST)
        self.conn_limit = int(config.DEFAULT_CONN_LIMIT)
        self.block_sec = int(config.DEFAULT_BLOCK_SEC)
        
        self.buckets, self.locks, self.conns = {}, {}, {}
        self.blacklist, self.whitelist, self.recent = {}, set(), {}
        self.country_traffic, self.blocked_countries = {}, {}
        self.metrics = {"total":0,"allowed":0,"blocked":0,"blocked_by_geo":0,"blacklisted":0}

        self.geoip_manager = GeoIPManager()
        self.trusted_countries = config.TRUSTED_COUNTRIES
        self.country_block_sec = config.COUNTRY_BLOCK_SEC
        self.country_rate_limit = config.COUNTRY_RATE_LIMIT

    def _now(self): return time.time()
    def _get_lock(self, ip): return self.locks.setdefault(ip, asyncio.Lock())
    def _get_recent(self, ip): return self.recent.setdefault(ip, deque(maxlen=1000))

    def is_blocked(self, ip):
        if ip in self.whitelist: return False
        ts = self.blacklist.get(ip)
        return bool(ts and ts > self._now())

    async def clear_expired_entries(self):
        now = self._now()
        expired_ips = [ip for ip, ts in self.blacklist.items() if ts <= now]
        for ip in expired_ips: self.blacklist.pop(ip, None)
        
        expired_countries = [c for c, ts in self.blocked_countries.items() if ts <= now]
        for c in expired_countries: self.blocked_countries.pop(c, None)
        
        if expired_ips or expired_countries:
            logger.info(f"{len(expired_ips)} IP ve {len(expired_countries)} ülke yasağı kaldırıldı.")

    def handle_geo_blocking(self, ip):
        country_code = self.geoip_manager.get_country(ip)
        if not country_code or country_code in self.trusted_countries: return False
        if country_code in self.blocked_countries:
            self.metrics["blocked_by_geo"] += 1
            return True
        now = self._now()
        traffic = self.country_traffic.get(country_code, {"count": 0, "start_time": now})
        if now - traffic["start_time"] > 1: traffic = {"count": 1, "start_time": now}
        else: traffic["count"] += 1
        self.country_traffic[country_code] = traffic
        if traffic["count"] > self.country_rate_limit:
            logger.warning(f"Ülke limiti aşıldı: {country_code}. {self.country_block_sec} saniye engellendi.")
            self.blocked_countries[country_code] = now + self.country_block_sec
            self.metrics["blocked_by_geo"] += 1
            return True
        return False

    async def check_and_mitigate(self, ip):
        self.metrics["total"] += 1
        if self.is_blocked(ip):
            self.metrics["blocked"] += 1
            return False, "IP blacklisted"
        if self.handle_geo_blocking(ip):
            return False, "Region traffic limit exceeded"
        async with self._get_lock(ip):
            tb = self.buckets.get(ip) or TokenBucket(self.rate, self.burst)
            self.buckets[ip] = tb
            r = self._get_recent(ip); r.append(self._now())
            if not tb.consume():
                if len([t for t in r if self._now() - t < 10]) > self.burst:
                    logger.warning(f"IP kara listeye alındı (rate limit burst): {ip}")
                    self.blacklist[ip] = self._now() + self.block_sec
                    self.metrics["blacklisted"] = len(self.blacklist)
                self.metrics["blocked"] += 1
                return False, "Rate limit exceeded"
        self.metrics["allowed"] += 1
        return True, "Allowed"
    
    async def increment_connection(self, ip):
        async with self._get_lock(ip):
            self.conns[ip] = self.conns.get(ip, 0) + 1
            if self.conns[ip] > self.conn_limit:
                logger.warning(f"IP kara listeye alındı (connection limit): {ip}")
                self.blacklist[ip] = self._now() + self.block_sec
                self.metrics["blocked"] += 1
                return False
        return True
        
    async def decrement_connection(self, ip):
        async with self._get_lock(ip):
            self.conns[ip] = max(0, self.conns.get(ip, 1) - 1)

    async def run_background_tasks(self):
        while True:
            try:
                await self.clear_expired_entries()
            except Exception as e:
                logger.exception("Arka plan temizlik görevinde hata: %s", e)
            await asyncio.sleep(10)
