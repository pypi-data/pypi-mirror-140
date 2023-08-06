# wqsketch

Developed by Benjamin Tay

## Examples

Basic Useage

```python
from wqsketch import create_sketch
from wqsketch import calculate_quantile
from wqsketch import merge_sketch
import numpy as np

data1 = 2 * np.random.random_sample((100,)) - 1
data2 = data1 + 1
data3 = data1 - 1

sketch1 = create_sketch(data1)
sketch2 = create_sketch(data2)
sketch3 = create_sketch(data3)

sketch1_median = calculate_quantile(0.5, sketch1)
sketch2_median = calculate_quantile(0.5, sketch2)
sketch3_median = calculate_quantile(0.5, sketch3)

sketch_list=[]
sketch_list.append(sketch1)
sketch_list.append(sketch2)
sketch_list.append(sketch3)

merged_sketch = merge_sketch(sketch_list)

merged_sketch_median = calculate_quantile(0.5,merged_sketch)
```