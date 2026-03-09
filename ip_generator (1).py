import ipaddress
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIAPASONS_FILE = os.path.join(SCRIPT_DIR, "diapasons.txt")

def load_countries():
    countries = {}
    if not os.path.exists(DIAPASONS_FILE):
        print(f"[-] Файл {DIAPASONS_FILE} не найден!")
        exit(1)
    with open(DIAPASONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) < 2:
                continue
            country = parts[0].strip()
            ranges = []
            for r in parts[1:]:
                r = r.strip()
                if "-" in r:
                    start, end = r.split("-", 1)
                    ranges.append((start.strip(), end.strip()))
            if ranges:
                countries[country] = ranges
    return countries

def count_ips(ranges):
    total = 0
    for start, end in ranges:
        try:
            total += int(ipaddress.IPv4Address(end)) - int(ipaddress.IPv4Address(start)) + 1
        except:
            pass
    return total

def print_menu(countries):
    print("\n" + "="*50)
    print("          ГЕНЕРАТОР IP ПО СТРАНЕ")
    print(f"          Загружено стран: {len(countries)}")
    print("="*50)
    sorted_countries = sorted(countries.items(), key=lambda x: x[0])
    for i, (country, ranges) in enumerate(sorted_countries, 1):
        total = count_ips(ranges)
        print(f"  {i:>3}. {country:<25} (~{total:,} IP)")
    print("="*50)
    return sorted_countries

def generate_ips(country_name, ranges):
    safe_name = country_name.replace(" ", "_").replace("/", "-")
    output_file = f"{safe_name}_ips.txt"
    output_path = os.path.join(SCRIPT_DIR, output_file)
    total = count_ips(ranges)
    print(f"\n[*] Страна:   {country_name}")
    print(f"[*] Всего IP: {total:,}")
    print(f"[*] Файл:     {output_file}")
    print("[*] Генерация...", end="", flush=True)
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Страна: {country_name}\n")
        f.write(f"# Всего IP: {total:,}\n\n")
        for start, end in ranges:
            try:
                start_int = int(ipaddress.IPv4Address(start))
                end_int   = int(ipaddress.IPv4Address(end))
                f.write(f"# {start} - {end}\n")
                for ip_int in range(start_int, end_int + 1):
                    f.write(str(ipaddress.IPv4Address(ip_int)) + "\n")
                    count += 1
            except Exception as e:
                f.write(f"# Ошибка диапазона {start}-{end}: {e}\n")
    print(f" готово!")
    print(f"[+] Записано: {count:,} IP")
    print(f"[+] Путь:     {output_path}")

def main():
    countries = load_countries()
    sorted_countries = print_menu(countries)
    while True:
        try:
            choice = int(input(f"\nВыберите страну (1-{len(sorted_countries)}): "))
            if 1 <= choice <= len(sorted_countries):
                break
            print(f"[-] Введите число от 1 до {len(sorted_countries)}")
        except ValueError:
            print("[-] Введите число!")
    country_name, ranges = sorted_countries[choice - 1]
    total = count_ips(ranges)
    if total > 1_000_000:
        print(f"\n[!] Внимание: будет сгенерировано {total:,} IP адресов")
        confirm = input("[?] Продолжить? (y/n): ")
        if confirm.lower() != "y":
            print("[-] Отменено")
            return
    generate_ips(country_name, ranges)

if __name__ == "__main__":
    main()
