# core/geoip_manager.py
import logging
import os  # <--- DÜZELTME: os modülü eklendi
try:
    import geoip2.database
    from geoip2.errors import AddressNotFoundError
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False

logger = logging.getLogger("ddos-preventer")

class GeoIPManager:
    """GeoIP veritabanını bir kez yükler ve ülke sorguları için bir arayüz sağlar."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeoIPManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.geo_reader = None
        if GEOIP_AVAILABLE:
            try:
                # <--- DÜZELTME: Dosya yolu, bu dosyanın bulunduğu dizine göre dinamik olarak ayarlandı.
                base_dir = os.path.dirname(os.path.abspath(__file__))
                db_path = os.path.join(base_dir, "GeoLite2-Country.mmdb")
                self.geo_reader = geoip2.database.Reader(db_path)
                logger.info("GeoLite2 veritabanı başarıyla yüklendi.")
            except FileNotFoundError:
                logger.error("GeoLite2-Country.mmdb bulunamadı! Lütfen 'core' klasörünün içine yerleştirin. Geo-blocking devre dışı kalacak.")
        else:
            logger.warning("geoip2 kütüphanesi bulunamadı. Geo-blocking devre dışı kalacak.")

    def get_country(self, ip):
        """Verilen bir IP adresinin 2 harfli ülke kodunu döndürür."""
        if not self.geo_reader:
            return None
        try:
            return self.geo_reader.country(ip).country.iso_code
        except AddressNotFoundError:
            return None # Lokal veya özel IP adresleri
        except Exception as e:
            logger.error("GeoIP sorgu hatası %s: %s", ip, e)
            return None
