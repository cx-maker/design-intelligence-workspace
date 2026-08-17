import { AestheticReference } from "@/schemas/domain";

export function buildMockContext(selected: AestheticReference[]) {
  return { 项目简介: "唐睛眼视光 — 精确、值得信赖的视光品牌视觉。", 品牌资产: ["标志", "#008FDB"], 已选参考: selected.map((r) => r.title), 审美规则: ["克制", "清晰层级", "高识别度"], 当前步骤: "生成" };
}
