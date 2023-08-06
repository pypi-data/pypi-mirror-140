import re

from collections import defaultdict

if __name__ == "__main__":
    counts = defaultdict(int)
    for line in open("benches/benchmarks/collected-works.txt", "r").readlines():
        line = line.lower()
        words = re.findall(r'[^\s!,.?":;0-9]+', line)
        for word in words:
            counts[word] += 1
