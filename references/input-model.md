# 输入模型与来源

## 寄存器数据

输入沿用 keil-pack-builder 的扁平输出：

- `device.name/version/description`；`peripherals[]`。
- 外设：`name/base_address/description/source/registers[]`。
- 寄存器：`name/offset/address/size/access/reset_value/reset_mask/description/source/fields[]`。
- 字段：`name/lsb/width/access/modified_write_values/read_action/description/source/enums[]`。
- 枚举：`name/value/description`。数值使用 JSON 整数，不能使用浮点或布尔值。
- `source` 定位标准表页和行；`origin` 可定位原始设计文件。空白来源不是已验证来源。继承属性空字符串表示继承或未声明，不表示显式无副作用。

支持 8/16/32 位、字节寻址、无重叠的扁平寄存器。数组、cluster、别名、读写双视图、通配枚举以及不同 read/write 枚举必须先扩展模型和验证器，不能悄悄展平。附带验证器是 UM 最低检查，不替代上游 Excel/SVD 校验或设计审核。

Excel 接入：若已有 keil-pack-builder，按其模板和转换器生成 model.json，再交给本 skill。该转换器不随本包复制；本包含独立 JSON 示例，可直接运行。不同 Excel 必须提供映射记录，逐条保留来源，并核对字段数和枚举数。

## 功能说明 content.json

- `synthetic: true/false` 明确示例属性，`scope` 是手册范围，`source` 是功能说明来源。
- `peripherals` 按外设名索引，每项 `overview`、`features[]`、`steps[]`、`source`。
- `figures[]`：`id/title/source/diagram`，diagram 为相对 content.json 的图形 JSON。当前生成器将这些图放在总览，外设内图需显式扩展定位字段。
- `style` 可设 `body_font`、`latin_font`、`body_size`、`line_spacing`、`table_header_fill`、`table_border_color`。示例是样式参数，不是从客户模板自动提取结果。

功能说明不完备时，在检查报告列出缺口；正文写明确的待补说明，不捏造设计行为。真实手册发布前解决缺口。

## 来源清单

生成清单记录 JSON 和所有图形源的 SHA256，以及输出文件哈希。不要将“设计规定”“计算值”“仿真”“实测”相互替换。图题不能充当测量来源；实测图还应记录样片、供电、温度、仪器、程序版本及原始文件。
