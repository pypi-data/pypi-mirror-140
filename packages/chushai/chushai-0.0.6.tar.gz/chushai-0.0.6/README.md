示例demo：
demo_use.py

### 初筛初始化
initChushai()
无输入参数
**返回**
classfication：分类器
queue_in：输入队列
queue_final_res：结果队列

### 初筛
```
imageScreening(img, quene_in, queue_final_res, metadata)
```
**入参**
img：ndarray图片
metadata object | 预留字段，回传给结果，方便业务拓展 |
queue_in：输入队列
queue_final_res：结果队列

**返回**
|参数|类型|说明|
|--|--|--|
|metadata| object | 入参的metadata |
|has_blemish| bool | 是否有瑕疵 |
|res| list | 初筛结果 |

|res.loc| object | 裁剪后的图相对入参图位置 |
```json
{
  "metadata": {},
  "has_blemish": true,
  "res": [
    {
      
      "loc": {
        "xmin": 112,
        "ymin": 224,
        "xmax": 448,
        "ymax": 560
      }
    },
    ...
  ]
}
```