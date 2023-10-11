import decimal
import locale

n = decimal.Decimal('0.000001')
print(n)
print(locale.format_string('%.12g', n, grouping=True))
n = decimal.Decimal('2343523542342342342342342344234234234234')
print(n)
print(locale.format_string('%.12g', n, grouping=True))

f = decimal.Decimal('1')
if f:
    print(f)
