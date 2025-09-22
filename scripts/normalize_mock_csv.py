from pathlib import Path
import csv
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 28

CSV_PATH = Path(__file__).resolve().parent.parent / 'mock_articoli.csv'

def is_null(x):
    return x is None or str(x).strip().upper() == 'NULL' or str(x).strip() == ''

def dec_str(d: Decimal) -> str:
    s = format(d, 'f')
    s = s.rstrip('0').rstrip('.')
    return s or '0'

def norm_fixed(value: str) -> str:
    if is_null(value):
        return ''
    s = str(value).strip()
    parts = s.split('.')
    if len(parts) >= 2 and all(part.isdigit() for part in parts):
        num = int(''.join(parts))
        scale = (len(parts) - 1) * 3
        d = (Decimal(num) / (Decimal(10) ** scale))
        return dec_str(d)
    s2 = s.replace(',', '.')
    try:
        d = Decimal(s2)
    except InvalidOperation:
        return s
    return dec_str(d)

def norm_pack(value: str) -> str:
    s = norm_fixed(value)
    if s == '':
        return ''
    try:
        return str(int(Decimal(s)))
    except Exception:
        return s.split('.')[0]

def norm_formato(value: str) -> str:
    if is_null(value):
        return ''
    s = str(value).strip().replace(',', '.')
    try:
        d = Decimal(s)
        return dec_str(d)
    except InvalidOperation:
        return s

def main():
    text = CSV_PATH.read_text(encoding='utf-8-sig')
    rows = list(csv.reader(text.splitlines(), delimiter=';'))
    if not rows:
        print('CSV vuoto')
        return
    header = rows[0]
    out_rows = [header]
    hmap = {h: i for i, h in enumerate(header)}
    for r in rows[1:]:
        rr = list(r)
        if 'EAN13' in hmap:
            i = hmap['EAN13']
            if is_null(rr[i]): rr[i] = ''
        if 'Descr_web' in hmap:
            i = hmap['Descr_web']
            if is_null(rr[i]): rr[i] = ''
        for col in ('pesotassabile','Prezzo','PrezzoNoIva','Dispnetta'):
            if col in hmap:
                i = hmap[col]
                rr[i] = norm_fixed(rr[i])
        if 'Pack' in hmap:
            i = hmap['Pack']
            rr[i] = norm_pack(rr[i])
        if 'Formato' in hmap:
            i = hmap['Formato']
            rr[i] = norm_formato(rr[i])
        out_rows.append(rr)

    with CSV_PATH.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerows(out_rows)
    print('Normalizzazione completata:', str(CSV_PATH), 'righe:', len(out_rows)-1)

if __name__ == '__main__':
    main()

