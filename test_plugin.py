import os
import textwrap
import langextract as lx


try:
    from dotenv import load_dotenv  
    load_dotenv()
except Exception:
    pass

# 提示词：抽取食品标签字段；要求严格用原文片段（不改写/不重叠）
prompt = textwrap.dedent(
    """
    从给定文本中抽取以下实体，按出现顺序输出：
    - food_name：食品名称/产品名称
    - ingredients：配料（整段）
    - net_content：净含量或规格
    - producer_name：生产者/制造商名称
    - producer_address：生产者/制造商地址
    - contact：联系方式（如服务热线、邮编等）
    - origin：原产地/产地
    - date_marking：日期标示（如生产日期说明、保质期等）
    - storage_condition：贮存条件
    - license_no：食品生产许可证编号
    - standard_code：产品标准代号/执行标准号
    - nutrition_table：营养成分表（整段）
    - other_marking：其他标示内容（整段）

    规则：
    1) extraction_text 必须严格使用原文中的片段，不得改写。
    2) 按出现顺序抽取；不同实体的字符区间不可重叠。
    3) 不需要生成多余的说明文字。
    """
)

# 示例：使用完整示例文本作为 ExampleData.text（与输入同源，确保抽取边界一致）
example_text = textwrap.dedent(
    """
    张君雅小妹妹酸辣虾味杯面（油炸方便面）
配料: 【面饼】: 小麦粉, 起酥油, 食用木薯淀粉, 食用盐, 食用马铃薯淀粉, 三聚磷酸钠, 多聚磷酸钠（包括六偏磷酸钠）, 碳酸钠, 羧甲基纤维素钠, 黄原胶, 可得然胶, 维生素E, 特丁基对苯二酚, 丁基羟基茴香醚, 柠檬酸, 栀子黄, 核黄素
固体复合调味粉包: 白砂糖, 食用盐, 脱水蔬菜（胡萝卜、大葱、辣椒）, 谷氨酸钠, 5'-鸟苷酸二钠, 5'-肌苷酸二钠, 琥珀酸二钠, 大蒜粉, 洋葱粉, 辣椒粉, 柠檬酸, 大豆水解蛋白, 酵母抽提物, 二氧化硅, 天门冬酰苯丙氨酸甲酯乙酰磺胺酸（含苯丙氨酸）
调味油包: 棕榈油, 大蒜, 香茅, 紫洋葱, 辣椒, 生姜, 高良姜, 食用香料, 辣椒油树脂
致敏物提示: 本产品含有麸质谷物制品及大豆制品；该生产线亦生产含乳类、鱼类、甲壳纲类等制品
生产日期: 日/月/年（见包装侧面）
保质期至: 日/月/年（见包装侧面）
贮藏条件: 请置于阴凉干燥处，避免阳光直射
原产国: 越南
在华注册编码: CVNM20012212070262
代理商: 上海勇盈贸易有限公司
电话: 021-54868350
地址: 上海市崇明区长兴镇潘圆公路1385号10幢3层302室
     """
)

examples = [
    lx.data.ExampleData(
        text=example_text,
        extractions=[
            lx.data.Extraction(extraction_class="food_name", extraction_text="蟹黄味糯米锅巴"),
            lx.data.Extraction(extraction_class="ingredients", extraction_text="配料:糯米（添加量≥49%）、食用植物油、玉米杂粮粉（玉米、绿豆、白芸豆、豌豆、豇豆、红小豆）、鸡蛋黄粉、淀粉、复合调味料（蟹香蛋黄调味粉）（添加量≥1%）、咸鸭蛋黄（添加量≥1%）、食用葡萄糖、食用盐、食用香精、辣椒红。"),
            lx.data.Extraction(extraction_class="net_content", extraction_text="净含量:390克"),
            lx.data.Extraction(extraction_class="producer_name", extraction_text="安徽佰益食品有限公司"),
            lx.data.Extraction(extraction_class="producer_address", extraction_text="安徽省合肥市安徽巢湖经济开发区（合巢产业新城）阳光大道与金巢大道交叉口向东100米二栋二层和三层"),
            lx.data.Extraction(extraction_class="contact", extraction_text="邮政编码：238062"),
            lx.data.Extraction(extraction_class="contact", extraction_text="消费者服务热线：400-820-0298"),
            lx.data.Extraction(extraction_class="origin", extraction_text="安徽省合肥市"),
            lx.data.Extraction(extraction_class="date_marking", extraction_text="生产日期（年/月/日）：见包装正面喷印处"),
            lx.data.Extraction(extraction_class="date_marking", extraction_text="保质期：180天"),
            lx.data.Extraction(extraction_class="storage_condition", extraction_text="贮存条件：请置于阴凉干燥处"),
            lx.data.Extraction(extraction_class="license_no", extraction_text="食品生产许可证编号：SC12434017430075"),
            lx.data.Extraction(extraction_class="standard_code", extraction_text="产品执行标准号：GB/T 20977"),
            lx.data.Extraction(extraction_class="nutrition_table", extraction_text="营养成分表 | 项目 每100g NRV% | 能量 2339kJ 28% | 蛋白质 6.1g 10% | 脂肪 34.3g 57% | —反式脂肪（酸） 0g | 碳水化合物 55.8g 19% | —糖 1.0g | 钠 329mg 16%"),
            lx.data.Extraction(extraction_class="other_marking", extraction_text="蟹黄味 | CRAB ROE GLUTINOUS RICE CRACKERS | 精选安徽圆糯米饭 | 0反式脂肪酸 米香浓郁 | 独立小袋 便携锁鲜 | 特添 | 咸鸭蛋黄 | 米香浓郁 | 超省 | 图片仅供参考 | 油炸类糕点 | 致敏物质提示：产品含有甲壳纲类动物及其制品、蛋类制品。 | 食用方法：开袋即食 | 警示信息：本产品如因贮存不当等质量问题，请勿食用，请及时到经销商处调换 | 扫描二维码以获取更多信息 检验合格 | 大润发 | RT-Mart | 本产品由大润发RT-Mart专卖"),
        ],
    )
]


input_text = example_text

import datetime
start_time = datetime.datetime.now()

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="qwen-flash",
    extraction_passes=1,
    max_workers=10,
)

# print(result)

end_time = datetime.datetime.now()
print(end_time-start_time)


lx.io.save_annotated_documents([result], output_name="product_extractions.jsonl", output_dir=".")
html = lx.visualize("product_extractions.jsonl")
with open("product_extractions.html", "w") as f:
    if hasattr(html, "data"):
        f.write(html.data)
    else:
        f.write(html)


