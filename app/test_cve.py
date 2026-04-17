import sys
sys.path.insert(0, '.')  # Чтобы видеть app.parser

from app.parser.nvdsearch import search_CVSS_CVE

print("🚀 Запуск теста search_CVSS_CVE...")
cve_id = "CVE-2025-14018"
print(f"🔍 Проверяем {cve_id}...")

cvss = search_CVSS_CVE(cve_id)

print(f"📊 Результат: {cvss}")
print("✅ Тест завершён.")