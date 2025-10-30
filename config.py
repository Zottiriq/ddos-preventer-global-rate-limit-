# config.py

# --- UYGULAMA KATMANI (HTTP Proxy) LİMİTLERİ ---
DEFAULT_RATE = 15
DEFAULT_BURST = 40
DEFAULT_CONN_LIMIT = 100
DEFAULT_BLOCK_SEC = 300  # 5 dakika

# --- GEO-BLOCKING AYARLARI ---
TRUSTED_COUNTRIES = {'TR'}
COUNTRY_RATE_LIMIT = 100
COUNTRY_BLOCK_SEC = 900

# --- TRANSPARENT PROXY VE PORT YÖNLENDİRME AYARLARI ---

# <--- DEĞİŞİKLİK BAŞLANGICI --->

# Bu liste, otomatik taramanın bulamadığı (örn: sadece belirli bir IP'de dinleyen)
# veya her durumda korunmasını istediğiniz temel portlar içindir.
# Otomatik tarama, bulduğu portları bu listenin üzerine ekleyecektir.
TARGET_PORTS = {
    22: 'tcp',       # SSH portu her zaman koruma altında olsun.
}

# Otomatik tarama, aşağıdaki portları 'http' olarak sınıflandıracaktır.
# Sunucunuzda farklı bir portta (örn: 8000) bir web servisi çalışıyorsa, buraya ekleyin.
WELL_KNOWN_HTTP_PORTS = {80, 443, 5000, 8000, 8080}

# <--- DEĞİŞİKLİK SONU --->


# Python betiğimizin gelen yönlendirilmiş trafiği dinleyeceği iç portlar.
# DİKKAT: Bu portların yukarıdaki listelerde OLMADIĞINDAN emin olun!
HTTP_PROXY_LISTEN_PORT = 8081
GENERIC_TCP_LISTEN_PORT = 9000

# --- SİSTEM VE SERVİS AYARLARI ---
DEFAULT_IPSET_NAME = "ddos_blockset"
DEFAULT_LOG_FILE = "/var/log/ddos-preventer.log"
IPTABLES_CHAIN = "DDOS_GATEWAY"