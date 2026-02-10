import barcode
from barcode.writer import ImageWriter

# 生成一个内容为 6401010137 的 Code 128 条形码
print("Generating clean barcode...")
code128 = barcode.get_barcode_class('code128')
my_code = code128('6401010137', writer=ImageWriter())

# 保存为 clean_test
filename = my_code.save('src/edge_node/assets/clean_test')
print(f"✅ Generated: {filename}")