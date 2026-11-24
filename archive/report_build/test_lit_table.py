import sys
sys.stdout.reconfigure(encoding='utf-8')
import text_ch2

print("LIT_TABLE_ROWS count:", len(text_ch2.LIT_TABLE_ROWS))
for i, r in enumerate(text_ch2.LIT_TABLE_ROWS[:3]):
    print(f"Row {i}:", r)
