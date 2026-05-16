#!/usr/bin/env python3
"""
Análisis avanzado del archivo ffuf para encontrar endpoints únicos
y patrones no obvios que indiquen contenido especial
"""

import json
import sys
from collections import defaultdict, Counter
import statistics

def analyze_ffuf_results(filename):
    print("=== Advanced FFUF Analysis ===")

    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        results = data.get('results', [])
        print(f"Total results: {len(results)}")

        if not results:
            print("No results found in ffuf file")
            return

        # 1. Análisis de respuestas únicas por length/words/lines
        length_groups = defaultdict(list)
        words_groups = defaultdict(list)
        lines_groups = defaultdict(list)
        status_groups = defaultdict(list)
        time_groups = defaultdict(list)

        all_lengths = []
        all_words = []
        all_lines = []
        all_times = []

        for result in results:
            url = result.get('url', '')
            length = result.get('length', 0)
            words = result.get('words', 0)
            lines = result.get('lines', 0)
            status = result.get('status', 0)
            duration = result.get('duration', 0)

            length_groups[length].append(url)
            words_groups[words].append(url)
            lines_groups[lines].append(url)
            status_groups[status].append(url)
            time_groups[duration].append(url)

            all_lengths.append(length)
            all_words.append(words)
            all_lines.append(lines)
            all_times.append(duration)

        # 2. Buscar outliers estadísticos
        print("\n[*] Statistical Analysis:")

        # Length outliers
        if all_lengths:
            mean_length = statistics.mean(all_lengths)
            stdev_length = statistics.stdev(all_lengths) if len(all_lengths) > 1 else 0
            print(f"Response lengths - Mean: {mean_length:.2f}, StdDev: {stdev_length:.2f}")

            # Encontrar lengths únicos o raros
            length_counts = Counter(all_lengths)
            unique_lengths = [length for length, count in length_counts.items() if count == 1]
            rare_lengths = [length for length, count in length_counts.items() if count <= 3]

            print(f"Unique response lengths ({len(unique_lengths)}): {sorted(unique_lengths)[:20]}")

            # URLs con lengths únicos/raros
            print("\n[!] URLs with unique/rare response lengths:")
            for length in sorted(unique_lengths)[:10]:
                urls = length_groups[length]
                print(f"  Length {length}: {urls[0]}")

        # 3. Buscar patrones de timing
        if all_times:
            mean_time = statistics.mean(all_times)
            stdev_time = statistics.stdev(all_times) if len(all_times) > 1 else 0
            print(f"\nResponse times - Mean: {mean_time:.0f}ms, StdDev: {stdev_time:.0f}ms")

            # Endpoints con timing inusual (muy lento o muy rápido)
            slow_threshold = mean_time + (2 * stdev_time) if stdev_time > 0 else mean_time * 2
            fast_threshold = mean_time - (2 * stdev_time) if stdev_time > 0 else mean_time * 0.5

            slow_endpoints = []
            fast_endpoints = []

            for result in results:
                duration = result.get('duration', 0)
                url = result.get('url', '')
                if duration > slow_threshold:
                    slow_endpoints.append((url, duration))
                elif duration < fast_threshold and duration > 0:
                    fast_endpoints.append((url, duration))

            if slow_endpoints:
                print(f"\n[!] Unusually SLOW endpoints (possible processing):")
                for url, duration in sorted(slow_endpoints, key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  {duration}ms: {url}")

            if fast_endpoints:
                print(f"\n[!] Unusually FAST endpoints (possible cached/special):")
                for url, duration in sorted(fast_endpoints, key=lambda x: x[1])[:10]:
                    print(f"  {duration}ms: {url}")

        # 4. Análisis de status codes
        print(f"\n[*] Status Code Distribution:")
        status_counts = Counter(status_groups.keys())
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count} endpoints")

        # Endpoints con status codes interesantes
        interesting_status = [200, 301, 302, 401, 403, 500]
        for status in interesting_status:
            if status in status_groups and len(status_groups[status]) <= 10:
                print(f"\n[!] Status {status} endpoints:")
                for url in status_groups[status][:10]:
                    print(f"  {url}")

        # 5. Buscar patrones en paths
        print(f"\n[*] Path Pattern Analysis:")

        # Endpoints con extensiones específicas
        extensions = defaultdict(list)
        for result in results:
            url = result.get('url', '')
            if '.' in url.split('/')[-1]:
                ext = url.split('.')[-1].lower()
                extensions[ext].append(url)

        print(f"File extensions found: {list(extensions.keys())}")
        for ext, urls in extensions.items():
            if len(urls) <= 5:  # Extensiones raras
                print(f"  .{ext}: {urls}")

        # Endpoints con palabras clave específicas
        keywords = ['flag', 'admin', 'secret', 'config', 'debug', 'test', 'dev', 'api',
                   'coordinator', 'shadow', 'cluster', 'unlock', 'token', 'auth',
                   'backup', 'temp', 'tmp', 'old', 'new', 'bak']

        keyword_matches = defaultdict(list)
        for result in results:
            url = result.get('url', '').lower()
            for keyword in keywords:
                if keyword in url:
                    keyword_matches[keyword].append(result)

        print(f"\n[!] Endpoints with interesting keywords:")
        for keyword, matches in keyword_matches.items():
            if matches:
                print(f"  '{keyword}': {len(matches)} matches")
                for match in matches[:3]:  # Primeros 3
                    print(f"    {match.get('url', '')} (length: {match.get('length', 0)}, status: {match.get('status', 0)})")

        # 6. Buscar endpoints con parameters
        param_endpoints = []
        for result in results:
            url = result.get('url', '')
            if '?' in url:
                param_endpoints.append(result)

        if param_endpoints:
            print(f"\n[!] Endpoints with parameters ({len(param_endpoints)}):")
            for endpoint in param_endpoints[:10]:
                print(f"  {endpoint.get('url', '')} (length: {endpoint.get('length', 0)})")

        # 7. Clustering por response similarity
        print(f"\n[*] Response Clustering:")

        # Agrupar por length+words+lines (firma de respuesta)
        signatures = defaultdict(list)
        for result in results:
            signature = f"{result.get('length', 0)}:{result.get('words', 0)}:{result.get('lines', 0)}"
            signatures[signature].append(result.get('url', ''))

        # Encontrar signatures únicas (posibles endpoints especiales)
        unique_signatures = [sig for sig, urls in signatures.items() if len(urls) == 1]
        print(f"Unique response signatures: {len(unique_signatures)}")

        for sig in sorted(unique_signatures)[:15]:
            urls = signatures[sig]
            print(f"  {sig}: {urls[0]}")

    except Exception as e:
        print(f"Error analyzing ffuf file: {e}")

def main():
    filename = "/home/pheaker/Documents/CTF/ffuf_shadow_coordinator_20260514_122454.json"
    analyze_ffuf_results(filename)

if __name__ == "__main__":
    main()